import re
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
from sentiment import analyze_sentiment
from utils import convert_date
USER_DATA_DIR = "./browser_data_2gis"

def parse_reviews(url: str):
    # --- URL LOGIC ---
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
            # --- ADRESS ---
            page.goto(main_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(2)
            try:
                addr = page.query_selector("._oqoid")
                if not addr: addr = page.query_selector("a[href*='/geo/']")
                if addr: 
                    company_address = addr.inner_text().split('\n')[0]
                    print(f"Адрес: {company_address}")
            except: pass

            # --- REVIEWS ---
            print(f"Идем к отзывам: {reviews_url}")
            page.goto(reviews_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(4)
            
            page.mouse.move(400, 600)

            last_count = 0
            retries = 0
            
            # Крутим сильнее и дольше, чтобы собрать все (включая отредактированные)
            while True:
                for _ in range(3):
                    page.mouse.wheel(0, 4000)
                    time.sleep(0.5)
                
                time.sleep(2)
                
                # Считаем по датам (они есть у всех отзывов)
                # Ищем элементы, содержащие цифры и название месяца
                # Это грубая проверка для счетчика
                # (Более точная проверка будет при парсинге)
                current_count = len(page.query_selector_all("meta[itemprop='datePublished']"))
                print(f"Скролл... Вижу ~{current_count} отзывов")

                if current_count >= 500: break
                if current_count > last_count:
                    last_count = current_count
                    retries = 0 
                else:
                    retries += 1
                    if retries >= 6: break
            
            # --- PARSING ---
            print("Начинаем разбор...")
            
            date_regex = re.compile(r'(\d{1,2}\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)(\s+\d{4})?)|сегодня|вчера', re.IGNORECASE)
            
            candidates = page.query_selector_all("div, span")
            processed_ids = set() # Храним уникальные тексты/ID

            for cand in candidates:
                try:
                    raw_text = cand.inner_text().strip()
                    # Убираем ", отредактирован" для проверки регуляркой
                    clean_date_text = raw_text.split(',')[0].strip()

                    if date_regex.fullmatch(clean_date_text):
                        review_date = clean_date_text # "20 июля 2024"
                        
                        # Ищем контейнер
                        container = cand.evaluate_handle("el => el.parentElement.parentElement.parentElement.parentElement.parentElement").as_element()
                        if not container: continue
                        
                        full_text_blob = container.inner_text()
                        
                        # Защита от дублей
                        h = hash(full_text_blob)
                        if h in processed_ids: continue
                        processed_ids.add(h)

                        # 1. АВТОР (Ищем ссылку на юзера внутри контейнера - это 100% вариант)
                        author_name = "Аноним"
                        user_link = container.query_selector("a[href*='/user/']")
                        if user_link:
                            author_name = user_link.inner_text().strip()
                        
                        # 2. РАЗБОР ТЕКСТА
                        lines = [l.strip() for l in full_text_blob.split('\n') if l.strip()]
                        review_text = ""
                        max_len = 0
                        
                        for l in lines:
                            # ФИЛЬТРЫ МУСОРА:
                            # 1. Если строка совпадает с датой (даже с "отредактирован")
                            if l.startswith(review_date) or clean_date_text in l: continue
                            # 2. Если строка совпадает с автором
                            if l == author_name: continue
                            # 3. Если это "5 отзывов" или "Знаток города"
                            if "отзыв" in l.lower() or "знаток" in l.lower(): continue
                            # 4. Если это "Отзыв подтвержден" и прочее
                            if "подтверждён" in l or "Официальный ответ" in l or "Показать ещё" in l: continue
                            # 5. Инициалы из аватарки (обычно 1-2 заглавные буквы)
                            if len(l) <= 2 and l.isupper(): continue
                            
                            # Ищем самую длинную оставшуюся строку
                            if len(l) > max_len:
                                review_text = l
                                max_len = len(l)
                        
                        if len(review_text) < 2: continue # Пустышки не нужны

                        # 3. РЕЙТИНГ (Пока 0, т.к. 2ГИС прячет)
                        rating = 0
                        
                        # 4. СЕНТИМЕНТ
                        sentiment = analyze_sentiment(review_text)

                        reviews_data.append({
                            "rating": rating,
                            "author": author_name,
                            "text": review_text,
                            "date": convert_date(review_date),
                            "sentiment": sentiment,
                            "source": "2gis"
                        })
                        
                        print(f"[OK] {author_name} ({review_date}): {review_text[:30]}...")

                except Exception as e:
                    pass

        except Exception as e:
            print(f"Error: {e}")
        finally:
            context.close()

    return reviews_data, company_address

if __name__ == "__main__":
    url = "https://2gis.ru/kemerovo/firm/70000001032439269" 
    res, _ = parse_reviews(url)
    print(f"Всего: {len(res)}")