from typing import List, Dict, Union
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import time
import requests

SCROLL_PAUSE_TIME = 0.5
PARSE_INTERVAL = 5  # Парсим каждые 5 скроллов

today = datetime.today()
yesterday = today - timedelta(days=1)

class KomersantParser:
    def __init__(self, url, driver, date_range, pattern=None):
        self.url = url
        self.driver = driver
        self.TIMEOUT = 0.1
        self.date_start, self.date_end = date_range
        self.window = None
        self.pattern_key_words = pattern
        self.source_name = "КоммерсантЪ"

        self.news: List[Dict] = []
        self.processed_urls = set()
        self.session = requests.Session()  # Используем сессию для повторных запросов
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def __extract_news_items(self, html: str, flag_parse_all = False) -> List[Dict]:

        # # Скользящее окно по html
        # if not flag_parse_all and self.window is not None:
        #     html_len = len(html)
        #     html = html[self.window:]
        #     self.window = html_len
        #
        # if self.window is None:
        #     self.window = len(html)
        """Извлекает новости из HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all("article", class_='uho')
        extracted = []

        for item in items:
            date_publication = item.find("p", class_="uho__tag").text.strip()
            date_str, time_str = [part.strip() for part in date_publication.split(",")]
            full_datetime_str = f"{date_str} {time_str}"  # например: "05.05.2025 13:15"
            article_datetime = datetime.strptime(full_datetime_str, '%d.%m.%Y %H:%M')  # ← теперь datetime

            url = item.get("data-article-url")
            if url in self.processed_urls:
                continue

            if article_datetime.date() < self.date_start:
                return extracted, False  # Прекращаем обработку, если дата слишком ранняя

            if article_datetime.date() > self.date_end:
                continue

            title = item.get("data-article-title")

            if self.pattern_key_words:
                if not re.search(self.pattern_key_words, title.lower()):
                    continue

            extracted.append({
                "url": url,
                "title": title,
                "date_publication": str(article_datetime.date()),
                "content": None,
                "source": self.source_name
            })

            self.processed_urls.add(url)

        return extracted, True  # while продолжает работать

    def __scroll_and_load(self):
        """Выполняет скроллинг и загрузку контента"""
        scroll_count = 0
        continue_loading = True

        while continue_loading:
            element = None
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, "button.ui-button.ui-button--standart")
            except:
                pass

            if element:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                                           element)
                self.driver.execute_script("arguments[0].click();", element)
            else:
                self.driver.execute_script("window.scrollBy({top: 1500, left: 0, behavior: 'smooth'});")

            scroll_count += 1
            time.sleep(SCROLL_PAUSE_TIME)

            if scroll_count % PARSE_INTERVAL == 0:
                new_items, continue_loading = self.__extract_news_items(self.driver.page_source)
                self.news.extend(new_items) # В отличие от РИА новостей экстендится прям так

        print(self.news)


    def __run(self):
        """Основной метод запуска парсера"""
        self.driver.get(self.url)
        self.__scroll_and_load()



    def __parse_news_page(self, url: str):
        """Парсинг полного текста новости через requests и BeautifulSoup"""
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Извлекаем основной текст
            text_blocks = soup.find_all('p', class_='doc__text')
            content = "\n".join([i.text for i in text_blocks])
            return content

        except Exception as e:
            print("Не удалось обратиться")
            return None

    def news_page(self): # public
        self.__run()
        for item in self.news:
            try:
                content = self.__parse_news_page(item['url'])
                item['content'] = content
            except Exception as e:
                print(f"{e}")
        return self.news

# if __name__ == "__main__":
#     url = "https://www.kommersant.ru/rubric/3?from=burger"
#     driver = webdriver.Chrome()
#     date_start = datetime.strptime(
#         DATE_RANGE[0].strip(), "%Y-%m-%d").date()
#     date_end = datetime.strptime(
#         DATE_RANGE[1].strip(), "%Y-%m-%d").date()
#     parser = KomersantParser(url=url, date_range=(date_start, date_end), driver=driver)
#     result = parser.news_page()
#     print(f"Найдено новостей: {len(result)}")
#     for item in result:  # Выводим первые 5 для примера
#         print(item)