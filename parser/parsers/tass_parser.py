from typing import List, Dict, Union
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import requests

months = {
    'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04',
    'мая': '05', 'июня': '06', 'июля': '07', 'августа': '08',
    'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'
}
MAX_WAIT_TIME = 20  # секунд

SCROLL_PAUSE_TIME = 0.2
PARSE_INTERVAL = 5  # Парсим каждые 5 скроллов
BASE_URL = "https://tass.ru/ekonomika" # Не стал подтягивать со свича, т.к лишний цикл
SOURCE_NAME = "ТАСС"

today = datetime.today()
year_today = today.year

class TASSParser:

    def __init__(self, url, driver, date_range, pattern=None):
        self.url = url
        self.driver = driver
        self.driver.get(url)
        self.date_start, self.date_end = date_range
        self.window = None
        self.pattern_key_words = pattern
        self.news: List[Dict] = []

    @staticmethod
    def get_date(date_time):
        date_time = date_time.replace('\xa0', ' ')  # заменяем неразрывный пробел
        parts = [part.strip() for part in date_time.split(",") if part.strip()]

        if len(parts) != 2:
            raise ValueError(f"Неверный формат даты: {date_time}")

        date, time = parts
        day, month = date.split(' ')
        month = months[month.lower()]
        date_publication = datetime.strptime(f"{day}-{month}-{year_today}", '%d-%m-%Y').date()

        return date_publication

    def parse_news_page(self, url: str, flag_date = False):
        """Парсинг полного текста новости через requests и BeautifulSoup"""
        response = requests.get("https://tass.ru/" + url)
        soup = BeautifulSoup(response.text, 'html.parser')
        if flag_date:
            date_time = soup.find('div', class_ = 'PublishedMark_date__LG42P').text
            return TASSParser.get_date(date_time)
        else:
            all_p = soup.find_all("p", class_ = "Paragraph_paragraph__9WAFK")
            content = "\n".join([p.get_text(strip=True) for p in all_p])
            date_time = soup.find('div', class_='PublishedMark_date__LG42P').text
            date = TASSParser.get_date(date_time)
            return date, content


    def extract_news_items(self, html: str, flag_parse_all = False):
        processed_urls = set()
        """Извлекает новости из HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all("a", class_='tass_pkg_link-v5WdK')
        extracted = []
        if not flag_parse_all:
            url = items[-1].get("href")
            print(url)
            article_datetime = self.parse_news_page(url, True)
            print(article_datetime)
            if article_datetime < date_start:
                return False  # Прекращаем обработку, если дата слишком ранняя
        else:
            for item in items:
                url = item.get("href")
                if url in processed_urls:
                    continue
                title = item.find("span").text
                # if self.pattern_key_words:
                #     if not re.search(self.pattern_key_words, title.lower()):
                #         continue

                article_datetime, content = self.parse_news_page(url)
                if article_datetime > date_end:
                    continue

                if article_datetime < date_start:
                    break  # Прекращаем обработку, если дата слишком ранняя


                extracted.append({
                    "url": url,
                    "title": title,
                    "date_publication": str(article_datetime),
                    "content": content,
                    "source": SOURCE_NAME
                })
        return extracted, True  # while продолжает работать

    def scroll_and_load(self):
        scroll_count = 0
        continue_loading = True

        while continue_loading:
            start_time = time.time()
            try:
                # Ищем ВСЕ кнопки с нужным data-test-id
                buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button[data-test-id="ds-external-button"]')

                # Фильтруем по тексту
                target_button = None
                for button in buttons:
                    if button.text.strip() == "Загрузить больше результатов":
                        target_button = button
                        break

                if target_button:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_button)
                    self.driver.execute_script("arguments[0].click();", target_button)
                else:
                    self.driver.execute_script("window.scrollBy({top: 2000, left: 0});")

                elapsed = time.time() - start_time
                if elapsed > MAX_WAIT_TIME:
                    print(f"⏱ Страница грузилась более {MAX_WAIT_TIME} секунд. Прерывание.")
                    break  # Есть проблемы с загрузкой страницы при скролле, сторона сервера ТАСС

                if scroll_count % PARSE_INTERVAL == 0:
                    continue_loading = self.extract_news_items(self.driver.page_source, False)
                    print(continue_loading)

            except NoSuchElementException:
                print("Ошибка при поиске кнопок.")
                continue_loading = False

            scroll_count += 1
            time.sleep(SCROLL_PAUSE_TIME)

        new_items, _ = self.extract_news_items(self.driver.page_source, True) # Полный парсинг html, со скипом новостей до и после
        self.news = new_items

    def news_page(self): # public
        self.scroll_and_load()
        return self.news


if __name__ == "__main__":
    url = "https://tass.ru/ekonomika"
    DATE_RANGE = ["2025-05-07", "2025-05-07"]
    driver = webdriver.Chrome()
    date_start = datetime.strptime(
        DATE_RANGE[0].strip(), "%Y-%m-%d").date()
    date_end = datetime.strptime(
        DATE_RANGE[1].strip(), "%Y-%m-%d").date()
    tass = TASSParser(url=url, driver=driver, date_range=(date_start, date_end))
    new_items = tass.news_page()

    for item in new_items:
        print(f"Заголовок: {item['title']}")
        print(f"URL: {item['url']}")
        print(f"Текст: {item['content'][:200]}...")
        print(f"Дата публикации: {item['date_publication']}")
        print(f"Источник: {item['source']}")
