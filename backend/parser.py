import random
import re
import time

from playwright.sync_api import sync_playwright

from sentiment import analyze_sentiment

# USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

USER_DATA_DIR = "./browser_data"

def parse_reviews(url: str):
    oid_match = re.search(r'oid(?:=|%3D)(\d+)', url)

    final_url = url
    if oid_match:
        org_id = oid_match.group(1)
        final_url = f"https://yandex.ru/maps/org/{org_id}/reviews/"
        print(f"Обнаружено ID организации! Собираем нормальную ссылку: {final_url}")

    print(f"Начинаем парсинг по URL: {final_url}")
    reviews_data = []

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
            page.goto(final_url, wait_until="domcontentloaded", timeout=30000)

            if "showcaptcha" in page.url or page.title() == "Ой!":
                print("Скрипт ждет, пока капча исчезнет...")
                page.wait_for_selector(".CheckboxCaptcha-Anchor", state="hidden", timeout=0)
                print("Капча пройдена! Продолжаем работу...")
                time.sleep(10)

            if "reviews" not in page.url:
                print("Мы не на вкладке отзывов. Ищем кнопку...")
                reviews_tab = page.query_selector(".tabs-select-view__title._name_reviews")

                if reviews_tab:
                    print("Кнопка найдена, кликаю...")
                    reviews_tab.click()
                    page.wait_for_load_state("networkidle")


            print("Страница загружена, скроллим вниз для подгрузки контента...")

            for _ in range(5):
                page.mouse.wheel(0, 1000)
                time.sleep(random.uniform(0.5, 1.5))
            # page.query_selector(".business-review-view")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(3000)

            review_elements = page.query_selector_all(".business-review-view")
            print(f"Найдено {len(review_elements)} отзывов на странице.")

            if not review_elements:
                print("Отзывы не найдены.")
                page.screenshot(path="debug_screenshot.png")
                print("Сделан отладочный скриншот debug_screenshot.png")

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
    return reviews_data


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
