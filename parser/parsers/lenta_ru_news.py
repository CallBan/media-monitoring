import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver


class LentaRuParser:
    def __init__(self, url, driver, date_range, pattern=None, headers = None):
        self.url = url
        self.driver = driver
        self.headers = headers
        self.driver.get(url)
        self.TIMEOUT = 1
        self.news = []
        self.source_name = "Lenta.ru"
        self.date_start, self.date_end = date_range
        # https://lenta.ru/news/2025/05/05/muzh-sestry-buzovoy-sobralsya-izbavitsya-ot-zarubezhnoy-kvartiry/
        self.pattern_link = re.compile(
            r'/news/(\d{4})/(\d{2})/(\d{2})/.*')
        self.pattern_key_words = pattern


    def __urls_list(self):
        """Получает все ссылки на новости в данном диапазоне дат"""
        time.sleep(self.TIMEOUT)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        news_blocks = soup.find_all('a', href=self.pattern_link)
        news_links = ['https://lenta.ru' + block['href'] for block in news_blocks]        
        filtered_links = []       
        for link in news_links:
            if self.date_start <= self.get_date(self.pattern_link, link) <= self.date_end:
                filtered_links.append(link)
        return filtered_links

    def __parse_news_page(self, url):
        """Парсит страницу новости"""
        try:
            response = requests.get(url, headers=self.headers)

            soup = BeautifulSoup(response.text, 'html.parser')

            title = soup.find('h1').text

            paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]
            content = ' '.join(paragraphs)

            date_publication = self.get_date(self.pattern_link, url)

            return title, content, date_publication
        except Exception:
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
    def get_date(pattern, url):
        match = re.search(pattern, url)
        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))     
        return datetime(year, month, day).date()


def main():
    url = 'https://lenta.ru/rubrics/economics/'
    date_start, date_end = datetime(2025, 5, 2).date(), datetime(2025, 5, 6).date()

    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=chrome_options)

    parser = LentaRuParser(url=url, driver=driver,
                       date_range=(date_start, date_end))
    
    news = parser.news_page()
    print(news)


if __name__ == '__main__':
    main()
