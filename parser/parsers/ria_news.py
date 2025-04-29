from typing import List, Dict, Union
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium import webdriver
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

date_start = datetime.strptime(DATE_RANGE[0], '%Y-%m-%d').date()
date_end = datetime.strptime(DATE_RANGE[1], '%Y-%m-%d').date()
today = datetime.today()
yesterday = today - timedelta(days=1)


class RiaParser:
    def __init__(self, url, driver, date_range, key_words=None):

        self.driver = driver
        self.driver.get(url)
        self.TIMEOUT = 0.1
        self.date_start, self.date_end = date_range

        self.pattern_key_words = None
        if key_words:
            escaped_words = [re.escape(word.lower()) for word in key_words]
            self.pattern_key_words = re.compile('|'.join(escaped_words))

        self.news: List[Dict] = []
        self.processed_urls = set()
        self.session = requests.Session()  # Используем сессию для повторных запросов
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def parse_date(self, date_str: str) -> Union[datetime.date, None]:
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

    def extract_news_items(self, html: str) -> List[Dict]:
        """Извлекает новости из HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all('div', class_='list-item')
        extracted = []
        idx = 1

        for item in items:
            date_div = item.find('div', {'data-type': 'date'})
            links = item.find_all('a')

            if not date_div or len(links) < 2:
                continue

            url = links[1].get('href')
            if url in self.processed_urls:
                continue

            if self.pattern_key_words:
                if not re.search(self.pattern_key_words, links[1].text):
                    continue

            date_str = date_div.text.strip()
            article_date, time_hour_min = self.parse_date(date_str)

            if article_date < date_start:
                return extracted, False  # Прекращаем обработку, если дата слишком ранняя

            if article_date > date_end:
                continue

            extracted.append({
                "id": str(idx),
                "url": url,
                "title": links[1].text if links[1].text else links[0].text,
                "date_publication": article_date.strftime('%Y-%m-%d') + ", " + time_hour_min,
                "content": None,
            })
            self.processed_urls.add(url)
            idx += 1

        return extracted, True # while продолжает работать

    def scroll_and_load(self):
        """Выполняет скроллинг и загрузку контента"""
        scroll_count = 0
        continue_loading = True

        while continue_loading:
            element = None
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, "div.list-more.color-btn-second-hover")
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
                new_items, continue_loading = self.extract_news_items(self.driver.page_source)
                self.news.extend(new_items)

    def run(self):
        """Основной метод запуска парсера"""
        try:
            self.driver.get(URL)
            self.scroll_and_load()
            return self.news
        finally:
            self.driver.quit()

    def parse_news_page(self, url: str) -> tuple:
        """Парсинг полного текста новости через requests и BeautifulSoup"""
        try:
            response = self.session.get(url)
            response.raise_for_status()  # Проверяем успешность запроса
            soup = BeautifulSoup(response.text, 'html.parser')

            # Извлекаем заголовок
            title_elem = soup.find('div', class_='article__title')
            title = title_elem.text.strip() if title_elem else ""

            # Извлекаем основной текст
            text_blocks = soup.find_all('div', class_='article__text')
            content = '\n'.join([p.text.strip() for p in text_blocks if p.text.strip()])

            return title, content

        except Exception as e:
            return None, None



    def news_page(self):
        news_urls = self.run()
        for item in news_urls[:10]:
            try:
                title, content = self.parse_news_page(item['url'])
                item['content'] = content
                # Заголовок может не подтягиваться при парсинге списка ссылок, прописываем еще раз, хотя сверху я наверное None на title поставлю
                item['title'] = title
            except Exception as e:
                print(f"{e}")
        return self.news