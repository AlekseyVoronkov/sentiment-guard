import re
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
from sentiment import analyze_sentiment
from utils import convert_date
USER_DATA_DIR = "./browser_data_2gis"

def parse_reviews(url: str):
    if "kemerovo/firm" in url and "reviews" not in url:
        url = url.rstrip("/") + "/reviews/"

    oid_match = re.search(r'firm/(\d+)', url)
    city_match = re.search(r'2gis\.ru/([^/]+)', url)
    
    if oid_match and city_match:
        main_url = f"https://2gis.ru/{city_match.group(1)}/firm/{oid_match.group(1)}"
        reviews_url = main_url + "/tab/reviews"
    else:
        main_url = url.split('/tab/')[0]
        reviews_url = main_url + "/tab/reviews"

    reviews_data = []
    company_address = None

    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            args=["--start-maximized"],
            no_viewport=True,
            slow_mo=50
        )
        page = context.pages[0]

        try:
            page.goto(main_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(2)
            try:
                addr = page.query_selector("._oqoid")
                if not addr: addr = page.query_selector("a[href*='/geo/']")
                if addr: 
                    company_address = addr.inner_text().split('\n')[0]
                    print(f"Адрес: {company_address}")
            except: pass

            print(f"Идем к отзывам: {reviews_url}")
            page.goto(reviews_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(4)
            
            page.mouse.move(400, 600)

            last_count = 0
            retries = 0
            js_count_script = """() => {
                const dateRegex = /(\\d{1,2}\\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)(\\s+\\d{4})?)|сегодня|вчера/i;
                let count = 0;
                document.querySelectorAll('div, span').forEach(el => {
                    if (el.children.length === 0 && dateRegex.test(el.innerText)) count++;
                });
                return count;
            }"""

            while True:
                try:
                    btn = page.get_by_role("button", name="Загрузить ещё")
                    if btn.is_visible():
                        btn.click()
                except: pass

                for _ in range(3):
                    page.mouse.wheel(0, 15000)
                    time.sleep(0.5)
                
                time.sleep(2)

                current_count = page.evaluate(js_count_script)
                print(f"Вижу отзывов: {current_count}")

                if current_count >= 500: break
                if current_count > last_count:
                    last_count = current_count
                    retries = 0 
                else:
                    retries += 1
                    if retries >= 6: break
            
            # --- PARSING ---
            print("Начинаем разбор...")
            
            raw_reviews_data = page.evaluate("""() => {
                const results = [];
                // Регулярка для дат
                const dateRegex = /^(\\d{1,2}\\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)(\\s+\\d{4})?)(.*)?$|сегодня|вчера/i;
                
                // Ищем все div и span
                const elements = document.querySelectorAll('div, span');
                const seen_texts = new Set();

                elements.forEach(el => {
                    // смотрим только листья дерева
                    if (el.children.length > 0) return;
                    
                    const text = el.innerText.trim();
                    if (!text) return;

                    const cleanDate = text.split(',')[0].trim();

                    if (dateRegex.test(cleanDate)) {
                        // Поднимаемся на 5 уровней вверх
                        let container = el;
                        for (let i = 0; i < 5; i++) {
                            if (container.parentElement) container = container.parentElement;
                        }
                        
                        if (container) {
                            const fullText = container.innerText;
                            if (!seen_texts.has(fullText)) {
                                seen_texts.add(fullText);
                                
                                let rating = 0;
                                // Ищем все SVG внутри этого контейнера
                                const svgs = container.querySelectorAll('svg');
                                svgs.forEach(svg => {
                                    const width = svg.getAttribute('width');
                                    const fill = svg.getAttribute('fill');
                                    
                                    // Проверяем: ширина около 10px и цвет НЕ серый
                                    if (width && parseInt(width) <= 14) {
                                        if (fill && !fill.includes('929292')) {
                                            rating++;
                                        }
                                    }
                                });
                                if (rating > 5) rating = 5;

                                results.push({
                                    raw_date: text,
                                    full_text: fullText,
                                    rating: rating // Передаем рейтинг в Python
                                });
                            }
                        }
                    }
                });
                return results;
            }""")
            
            print(f"JS вернул {len(raw_reviews_data)} блоков. Обрабатываем...")

            for item in raw_reviews_data:
                try:
                    full_text = item['full_text']
                    raw_date = item['raw_date']
                    rating = item['rating']
                    
                    clean_date_check = raw_date.split(',')[0].strip()

                    lines = [l.strip() for l in full_text.split('\n') if l.strip()]
                    
                    author_name = "Аноним"
                    review_text = ""
                    
                    # Находим индекс даты
                    date_index = -1
                    for i, line in enumerate(lines):
                        if line.startswith(clean_date_check):
                            date_index = i
                            break
                    
                    if date_index != -1:
                        # 1. АВТОР
                        if date_index > 0:
                            potential_author = lines[date_index - 1]
                            if len(potential_author) <= 2 and potential_author.isupper() and date_index > 1:
                                potential_author = lines[date_index - 2]
                            author_name = re.sub(r'\d+\s+отзыв.*', '', potential_author).strip().strip('\u200b')

                        # 2. ТЕКСТ
                        if date_index + 1 < len(lines):
                            potential_text = lines[date_index + 1]
                            bad_words = ["Читать целиком", "Полезно?", "1 посещение", "Отзыв подтверждён"]
                            if not any(bw in potential_text for bw in bad_words):
                                review_text = potential_text
                            else:
                                if date_index + 2 < len(lines):
                                    review_text = lines[date_index + 2]

                    if not review_text or len(review_text) < 2 or "Читать целиком" in review_text: 
                        continue
                    
                    sentiment = analyze_sentiment(review_text)
                    
                    if rating > 0:
                        if rating <= 2 and sentiment in ["Positive", "Neutral"]:
                            sentiment = "Negative"
                        if rating == 5 and sentiment == "Negative":
                            sentiment = "Positive"

                    reviews_data.append({
                        "rating": rating,
                        "author": author_name,
                        "text": review_text,
                        "date": convert_date(raw_date),
                        "sentiment": sentiment,
                        "source": "2gis"
                    })

                except Exception as e:
                    pass


        except Exception as e:
            print(f"Error: {e}")
        finally:
            context.close()

    print(f"2ГИС завершен. Собрано: {len(reviews_data)}")
    return reviews_data, company_address

if __name__ == "__main__":
    url = "https://2gis.ru/kemerovo/firm/704670989297908" 
    parse_reviews(url)
