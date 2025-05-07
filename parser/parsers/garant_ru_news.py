import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By

months = {
    'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04',
    'мая': '05', 'июня': '06', 'июля': '07', 'августа': '08',
    'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'
}


class GarantRuParser:
    def __init__(self, url, driver, date_range, pattern=None):
        self.url = url
        self.driver = driver
        self.driver.get(url)
        self.TIMEOUT = 1
        self.news = []
        self.date_start, self.date_end = date_range
        self.source_name = "Гарант.ру"
        self.pattern_link = re.compile(
            r'/news/\d{7}/')
        self.pattern_key_words = pattern

    def __urls_list(self):
        """Получает все ссылки на новости в данном диапазоне дат"""
        flag_break = True
        while flag_break:
            time.sleep(self.TIMEOUT)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            last_block_date = soup.find_all('time')[-1].text
            day, month_str, year, _ = last_block_date.split()
            month = months[month_str]
            last_date = datetime(year=int(year), month=int(month), day=int(day)).date()

            if last_date >= self.date_start:
                next_button = self.driver.find_element(
                    By.CLASS_NAME, "pagination-next")
                next_button.click()
            else:
                flag_break = False

        news_links = ['https://www.garant.ru' + block['href']
                      for block in soup.find_all('a', class_='title', href=self.pattern_link)]

        filtered_links = []
        for link in news_links:
            print(self.date_start, self.__get_date(link), self.date_end)
            if self.date_start <= self.__get_date(link) <= self.date_end:
                filtered_links.append(link)
        return filtered_links

    def __parse_news_page(self, url):
        """Парсит страницу новости"""
        response = requests.get(url)

        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find('h1').text
        content = soup.find('div', class_='page-content').text
        date_publication = self.__get_date(url)

        return title, content, date_publication

    def news_page(self):
        news_urls = self.__urls_list()
        for url in news_urls:
            try:
                title, content, date_publication = self.__parse_news_page(url)
                if self.pattern_key_words:
                    if not re.search(self.pattern_key_words, title.lower()):
                        continue
                self.news.append({
                    "url": url,
                    "title": title,
                    "content": content,
                    "date_publication": date_publication,
                    "source": self.source_name
                })

            except Exception as e:
                print(f"Ошибка при обработке {url}: {str(e)}")
                continue

        return self.news

    @staticmethod
    def __get_date(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.find('div', class_='page-content')
        str_date = content.find('time').text
        # 29 апреля 2025
        day, month_str, year = str_date.split()
        month = months[month_str]
        return datetime(year=int(year), month=int(month), day=int(day)).date()


def main():
    url = 'https://www.garant.ru/news/'
    date_start, date_end = datetime(
        2025, 5, 2).date(), datetime(2025, 5, 6).date()

    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=chrome_options)

    parser = GarantRuParser(url=url, driver=driver,
                            date_range=(date_start, date_end))

    news = parser.news_page()
    print(news)


if __name__ == '__main__':
    main()
