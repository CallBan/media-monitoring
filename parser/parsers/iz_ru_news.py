import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By


class IzRuParser:
    def __init__(self, url, driver, date_range, pattern=None):
        self.url = url
        self.driver = driver
        self.driver.get(url)
        self.TIMEOUT = 1
        self.news = []
        self.source_name = "Известия"
        self.date_start, self.date_end = date_range
        # /1882075/2025-05-06/ekonomist-nazval-prichiny-snizheniia-srednikh-stavok-po-vkladam
        self.pattern_link = re.compile(
            r'/\d+/(\d{4}-\d{2}-\d{2})/.*')
        self.pattern_key_words = pattern


    def __urls_list(self):
        """Получает все ссылки на новости в данном диапазоне дат"""
        flag_break = True
        while flag_break:
            time.sleep(self.TIMEOUT)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            news_blocks = soup.find_all('a', href=self.pattern_link)
            news_links = ['https://iz.ru' + block['href'] for block in news_blocks]
            
            last_date = min([self.__get_date(self.pattern_link, link) for link in news_links])

            if last_date >= self.date_start:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            else:
                flag_break = False

        filtered_links = []       
        for link in news_links:
            if self.date_start <= self.__get_date(self.pattern_link, link) <= self.date_end:
                filtered_links.append(link)
        return filtered_links

    def __parse_news_page(self, url):
        """Парсит страницу новости"""
        self.driver.get(url)

        title = self.driver.find_element(By.TAG_NAME, 'h1').text

        paragraphs = self.driver.find_elements(By.CSS_SELECTOR, "div.block-container p")
        content = ' '.join([p.text for p in paragraphs])

        date_publication = self.__get_date(self.pattern_link, url)
        
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
    def __get_date(pattern, url):
        match = re.search(pattern, url)
        year, month, day = list(map(int, match.group(1).split('-')))    
        return datetime(year, month, day).date()


def main():
    url = 'https://iz.ru/rubric/ekonomika'
    date_start, date_end = datetime(2025, 5, 7).date(), datetime(2025, 5, 7).date()

    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=chrome_options)

    parser = IzRuParser(url=url, driver=driver,
                       date_range=(date_start, date_end))
    
    news = parser.news_page()
    print(news)



if __name__ == '__main__':
    main()
