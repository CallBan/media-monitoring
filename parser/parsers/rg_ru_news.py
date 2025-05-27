import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By


class RgRuParser:
    def __init__(self, url, driver, date_range, pattern=None, headers = None):
        self.url = url
        self.driver = driver
        self.headers = headers
        self.driver.get(url)
        self.TIMEOUT = 0.2
        self.news = []
        self.date_start, self.date_end = date_range
        self.source_name = "RG.RU"
        self.pattern_link = re.compile(
            r'/(\d{4})/(\d{2})/(\d{2})/.*')
        self.pattern_key_words = pattern

    def __urls_list(self):
        """Получает все ссылки на новости в данном диапазоне дат"""
        flag_break = True
        while flag_break:
            time.sleep(self.TIMEOUT)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            news_blocks = soup.find_all('a', href=self.pattern_link)
            news_links = ['https://rg.ru' + block['href'] for block in news_blocks]
            
            last_date = min([self.__get_date(self.pattern_link, link) for link in news_links])

            if last_date >= self.date_start:
                button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Загрузить еще')]")
                button.click()
            else:
                flag_break = False

        filtered_links = []
        for link in news_links:
            if self.date_start <= self.__get_date(self.pattern_link, link) <= self.date_end:
                filtered_links.append(link)
        return list(set(filtered_links))

    def __parse_news_page(self, url):
        """Парсит страницу новости"""
        try:
            response = requests.get(url, headers=self.headers)

            soup = BeautifulSoup(response.text, 'html.parser')

            title = soup.find('h1').text
            content = ' '.join([p.get_text(strip=True) for p in soup.find_all('p')])
            date_publication = self.__get_date(self.pattern_link, url)

            return title, content, date_publication
        except:
            return None

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
    def __get_date(pattern, url):
        match = re.search(pattern, url)
        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))     
        return datetime(year, month, day).date()


def main():
    url = 'https://rg.ru/tema/ekonomika'
    date_start, date_end = datetime(
        2025, 5, 6).date(), datetime(2025, 5, 7).date()

    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=chrome_options)

    parser = RgRuParser(url=url, driver=driver,
                            date_range=(date_start, date_end))

    news = parser.news_page()
    print(news)


if __name__ == '__main__':
    main()
