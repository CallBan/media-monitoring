from typing import List, Dict, Union
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time

import requests

SCROLL_PAUSE_TIME = 0.5
PARSE_INTERVAL = 5  # Парсим каждые 5 скроллов

# Инициализация
months = {
    'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04',
    'мая': '05', 'июня': '06', 'июля': '07', 'августа': '08',
    'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'
}

today = datetime.today()
yesterday = today - timedelta(days=1)

DATE_RANGE = ["2025-05-09", "2025-05-10"]
class InterFaxParser:
    def __init__(self, url, driver, date_range, pattern=None):
        self.url = url
        self.driver = driver
        self.TIMEOUT = 0.1
        self.MAX_WAIT_TIME = 20
        self.date_start, self.date_end = date_range
        self.SOURCE_NAME = "Интерфакс"
        self.BASE_URL = "https://www.interfax.ru"
        self.window = None

        self.pattern_key_words = None

        if pattern:
            self.pattern_key_words = pattern
        print(self.pattern_key_words)
        self.news: List[Dict] = []
        # self.processed_urls = set()
        self.session = requests.Session()  # Используем сессию для повторных запросов
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def __parse_date(self, date_str: str) -> Union[datetime.date, None]:
        """Парсит дату из различных форматов"""
        date_str = date_str.strip()

        if re.match(r'^\d{2}:\d{2}$', date_str):
            return today.date(), date_str

        try:
            if date_str.startswith('Вчера'):
                return yesterday.date(), date_str.split(",")[1].strip()

            if ',' in date_str:
                date_part, time_part = date_str.split(',', 1)
                date_part = date_part.strip()

                if ' ' in date_part:
                    day, month_name = date_part.split()
                    if month_name in months:
                        month = months[month_name]
                        year = today.year
                        return datetime.strptime(f'{day}-{month}-{year}', '%d-%m-%Y').date(), date_str.split(",")[1].strip()

        except Exception as e:
            print(f"Ошибка парсинга даты: {date_str} - {e}")
        return None

    def __extract_news_items(self, html: str, flag_parse_all = False) -> List[Dict]:
        processed_urls = set()
        dir_names = ["group", "photo", "text"]
        soup = BeautifulSoup(html, 'html.parser')
        groups = [soup.find_all("div", class_=f'timeline__{i}') for i in dir_names]
        extracted = []

        if not flag_parse_all:
            news_blocks = groups[0][-1].find_all("div", recursive=False)
            for block in news_blocks:
                time_tag = block.find("time")
                date_str = time_tag.get("datetime")
                article_datetime = datetime.strptime(date_str.split("T")[0], '%Y-%m-%d').date()
                if article_datetime < self.date_start:
                    return False  # Остановить while
        else:
            for group_type, groups_ in zip(dir_names, groups):
                for group in groups_:
                    # Для timeline__group ищем вложенные div, для других - работаем с самим элементом
                    news_blocks = group.find_all("div", recursive=False) if group_type == "group" else [group]

                    for block in news_blocks:
                        time_tag = block.find("time")
                        a_tags = block.find_all("a")

                        # Ищем заголовок (h3)
                        h3_tag = block.find("h3")
                        if not h3_tag:
                            continue

                        # Берем первую ссылку, содержащую заголовок
                        main_a_tag = None
                        for a in a_tags:
                            if a.find("h3"):
                                main_a_tag = a
                                break

                        if not main_a_tag:
                            continue

                        url = main_a_tag.get("href")
                        title = h3_tag.get_text(strip=True)
                        date_str = time_tag.get("datetime")

                        # Пропускаем дубли
                        if url in processed_urls:
                            continue
                        processed_urls.add(url)

                        article_datetime = datetime.strptime(date_str.split("T")[0], '%Y-%m-%d').date()

                        if article_datetime > self.date_end:
                            continue

                        if article_datetime < self.date_start:
                            break
                        print(url, title, date_str)
                        extracted.append({
                            "url": self.BASE_URL + url,
                            "title": title,
                            "date_publication": str(article_datetime),
                            "content": None,
                            "source": self.SOURCE_NAME
                        })

        return extracted, True

    def __scroll_and_load(self):
        scroll_count = 0
        continue_loading = True

        while continue_loading:
            start_time = time.time()
            try:
                # Ищем ВСЕ кнопки с нужным data-test-id
                buttons = self.driver.find_elements(By.CSS_SELECTOR, "div.timeline__more")

                if buttons:
                    button = buttons[0]  # Берём первый найденный элемент
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                     # Небольшая пауза, чтобы прокрутка завершилась
                    self.driver.execute_script("arguments[0].click();", button)
                    print("🔘 Кнопка найдена и нажата.")
                    time.sleep(SCROLL_PAUSE_TIME)
                else:
                    self.driver.execute_script("window.scrollBy({top: 2000, left: 0});")
                    print("🔍 Кнопка не найдена. Скролл вниз.")

                elapsed = time.time() - start_time
                if elapsed > self.MAX_WAIT_TIME:
                    print(f"⏱ Страница грузилась более {self.MAX_WAIT_TIME} секунд. Прерывание.")
                    break  # Есть проблемы с загрузкой страницы при скролле, сторона сервера ТАСС

                if scroll_count % PARSE_INTERVAL == 0:
                    continue_loading = self.__extract_news_items(self.driver.page_source, False)
                    print(continue_loading)

            except NoSuchElementException:
                print("Ошибка при поиске кнопок.")
                continue_loading = False

            scroll_count += 1
            time.sleep(SCROLL_PAUSE_TIME)

        new_items, _ = self.__extract_news_items(self.driver.page_source, True)
        self.news = new_items



    def __run(self):
        """Основной метод запуска парсера"""
        self.driver.get(self.url)
        self.__scroll_and_load()
        return self.news


    def __parse_news_page(self, url: str):
        """Парсинг полного текста новости через requests и BeautifulSoup"""
        try:
            response = requests.get(url, headers={'Accept-Charset': 'utf-8'})
            response.encoding = response.apparent_encoding  # Замена кодировки для текста страницы
            soup = BeautifulSoup(response.text, 'html.parser')
            # Извлекаем основной текст
            text_blocks = soup.find_all('p')
            content = '\n'.join([p.text.strip() for p in text_blocks if p.text.strip()])
            return content
        except Exception as e:
            return None

    def news_page(self): # public
        news_urls = self.__run()
        print("Вызов после")
        for item in news_urls:
            try:
                content = self.__parse_news_page(item['url'])
                item['content'] = content
                print(content)
            except Exception as e:
                print(f"{e}")
        return self.news

# if __name__ == "__main__":
#     url = "https://www.interfax.ru/business/"
#     driver = webdriver.Chrome()
#     date_start = datetime.strptime(
#         DATE_RANGE[0].strip(), "%Y-%m-%d").date()
#     date_end = datetime.strptime(
#         DATE_RANGE[1].strip(), "%Y-%m-%d").date()
#     parser = RIAParser(url=url, date_range = (date_start, date_end), driver=driver)
#     result = parser.news_page()
#     print(f"Найдено новостей: {len(result)}")
#     for item in result:  # Выводим первые 5 для примера
#         print(item)