import time
from typing import Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


BASE_URL = 'https://www.banki.ru'
TIMEOUT = 0.1
MAX_NEWS = 5


def init_driver():
    """Инициализация headless-браузера"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    return webdriver.Chrome(options=chrome_options)


def fetch_news_urls(driver, page):
    """Получение списка URL новостей"""
    driver.get(f'{BASE_URL}/news/lenta/?page={page}')
    time.sleep(TIMEOUT)

    return [element.get_attribute('href') for element in driver.find_elements(
        By.CSS_SELECTOR, 'a[href*="/news/lenta/?id"]')]


def parse_news_page(driver, url):
    """Парсинг полного текста новости"""
    driver.get(url)
    time.sleep(TIMEOUT)

    title = driver.find_element(By.TAG_NAME, 'h1').text.strip()
    content = '\n'.join([p.text.strip() for p in driver.find_elements(By.TAG_NAME, 'p')])
    return title, content


def get_news() -> list[Any] | None:
    """Основная функция получения новостей"""
    driver = init_driver()
    news = []
    page = 1
    count_news = 0

    while count_news < MAX_NEWS:
        news_urls = fetch_news_urls(driver, page)
        if len(news_urls) > MAX_NEWS:
            news_urls = news_urls[:MAX_NEWS]
        for url in news_urls:
            try:
                title, content = parse_news_page(driver, url)
                news.append({
                    "url": url,
                    "title": title,
                    "content": content
                })
            except Exception as e:
                print(f"Ошибка при обработке {url}: {str(e)}")
                continue
        count_news += len(news_urls)
        page += 1

    driver.quit()
    return news


def main():
    news = get_news()
    for idx, item in enumerate(news, 1):
        print(f"\nНовость #{idx}:")
        print(f"Заголовок: {item['title']}")
        print(f"URL: {item['url']}")
        print(f"Текст: {item['content'][:200]}...")



if __name__ == '__main__':
    main()