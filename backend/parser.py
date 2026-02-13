import random
import re
import time

from playwright.sync_api import sync_playwright

from sentiment import analyze_sentiment

# USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

USER_DATA_DIR = "./browser_data"

def parse_reviews(url: str):
    oid_match = re.search(r'oid(?:=|%3D)(\d+)', url)
    org_id = None
    
    if oid_match:
        org_id = oid_match.group(1)
        main_url = f"https://yandex.ru/maps/org/{org_id}/"
        reviews_url = f"https://yandex.ru/maps/org/{org_id}/reviews/"
        print(f"ID найден: {org_id}")
    else:
        main_url = url
        if url.endswith("/"):
            reviews_url = url + "reviews/"
        else:
            reviews_url = url + "/reviews/"

    print(f"1. Идем за адресом: {main_url}")

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
            page.goto(main_url, wait_until="domcontentloaded", timeout=30000)

            if "showcaptcha" in page.url or page.title() == "Ой!":
                print("Скрипт ждет, пока капча исчезнет...")
                page.wait_for_selector(".CheckboxCaptcha-Anchor", state="hidden", timeout=0)
                print("Капча пройдена! Продолжаем работу...")
                time.sleep(3)

            try:
                print("Ищем адрес...")
                page.wait_for_selector(".business-contacts-view__address-link", timeout=5000) 
                
                address_element = page.query_selector(".business-contacts-view__address-link")
                if not address_element:
                     address_element = page.query_selector("meta[itemprop='address']")
                     if address_element:
                         company_address = address_element.get_attribute("content")
                
                if address_element and not company_address:
                    company_address = address_element.inner_text()
                
                print(f"Адрес: {company_address}")
            except Exception as e:
                print(f"Адрес не найден (не страшно): {e}")

            print(f"2. Переходим к отзывам: {reviews_url}")
            page.goto(reviews_url, wait_until="domcontentloaded", timeout=60000)

            try:
                page.wait_for_selector(".business-reviews-view__reviews-list", timeout=15000)
            except:
                print("Контейнер отзывов не появился сразу, пробуем скроллить...")

            print("Скроллим...")
            for _ in range(5):
                page.mouse.wheel(0, 5000)
                time.sleep(random.uniform(0.5, 1.0))
            
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

            page.wait_for_timeout(3000)

            review_elements = page.query_selector_all(".business-review-view")
            print(f"Найдено {len(review_elements)} отзывов.")

            for review_element in review_elements:
                try:
                    rating = 0
                    rating_element = review_element.query_selector(".business-rating-badge-view__stars")
                    if rating_element:
                        aria_label = rating_element.get_attribute("aria-label")
                        if aria_label:
                            match = re.search(r'\d+', aria_label)
                            if match:
                                rating = int(match.group(0))

                    author_name_element = review_element.query_selector(".business-review-view__link")
                    author_name = author_name_element.inner_text() if author_name_element else "Аноним"

                    review_text_element = review_element.query_selector(".spoiler-view__text-container")
                    review_text = review_text_element.inner_text() if review_text_element else ""

                    review_date_element = review_element.query_selector(
                    ".business-review-view__date meta[itemprop='datePublished']")
                    if review_date_element:
                        review_date = review_date_element.get_attribute("content")
                    else:
                        review_date_element_fallback = review_element.query_selector(".business-review-view__date")
                        review_date = review_date_element_fallback.inner_text() if review_date_element_fallback else ""

                    if review_text:
                        sentiment = analyze_sentiment(review_text)

                        if rating > 0 and rating <= 2 and sentiment in ["positive", "neutral"]:
                            sentiment = "negative"
                        
                        if rating == 5 and sentiment == "negative":
                            sentiment = "positive"
                        reviews_data.append({
                            "rating": rating,
                            "author": author_name.strip(),
                            "text": review_text.strip(),
                            "date": review_date.strip(),
                            "sentiment": sentiment
                        })
                except Exception as e:
                    print(f"Произошла ошибка при парсинге отзыва: {e}")

        except Exception as e:
            print(f"Произошла глобальная ошибка при парсинге: {e}")
            page.screenshot(path="error_screenshot.png")
            print("Сделан скриншот ошибки error_screenshot.png")

        finally:
            context.close()

    print(f"Парсинг завершен. Собрано {len(reviews_data)} отзывов.")
    return reviews_data, company_address


def main():
    url = "https://yandex.ru/maps/org/pyatyorochka/187303066631/reviews/"
    reviews = parse_reviews(url)

    for i, review in enumerate(reviews):
        print(f"\n--- Отзыв #{i + 1} ---")
        print(f"Рейтинг: {review['rating']}")
        print(f"Автор: {review['author']}")
        print(f"Дата: {review['date']}")
        print(f"Текст: {review['text']}")


if __name__ == "__main__":
    main()
