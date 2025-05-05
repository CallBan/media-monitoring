import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime


class RBKParser:
    def __init__(self, url, driver, date_range, pattern=None):
        self.url = url
        self.driver = driver
        self.driver.get(url)
        self.TIMEOUT = 1
        self.news = []
        self.date_start, self.date_end = date_range

        self.pattern_link = re.compile(
            r'https://www\.rbc\.ru/finances/(\d{2})/(\d{2})/(\d{4})/.*')
        self.pattern_key_words = pattern


    def __urls_list(self):
        """Получает все ссылки на новости в данном диапазоне дат"""
        flag_break = True
        while flag_break:
            time.sleep(self.TIMEOUT)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            print('блять работает 1')
            news_blocks = soup.find_all('a', href=self.pattern_link)
            print('блять работает 2')
            news_links = []
            for block in news_blocks:
                try:
                    news_links.append(block['href'])

                except Exception as e:
                    print(f"Ошибка в блоке: {e}")
            
            last_date = self.get_date(self.pattern_link, news_links[-1])

            if last_date >= self.date_start:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            else:
                flag_break = False

        filtered_links = []       
        for link in news_links:
            if self.date_start <= self.get_date(self.pattern_link, link) <= self.date_end:
                filtered_links.append(link)
        return filtered_links

    def __parse_news_page(self, url):
        """Парсит страницу новости"""
        response = requests.get(url)

        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.find('h1').text

        paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]
        tg_index = paragraphs.index('Читайте РБК вTelegram.')
        content = ' '.join(paragraphs[:tg_index])

        date_publication = self.get_date(self.pattern_link, url)
        
        return title, content, date_publication


    def news_page(self):
        news_urls = self.__urls_list()
        for url in news_urls:
            try:
                title, content, date_publication = self.__parse_news_page(url)
                self.news.append({
                    "url": url,
                    "title": title,
                    "content": content,
                    "date_publication": date_publication
                })

            except Exception as e:
                print(f"Ошибка при обработке {url}: {str(e)}")
                continue

        return self.news
    
    @staticmethod
    def get_date(pattern, url):
        match = re.search(pattern, url)
        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))     
        return datetime(year, month, day).date()


def main():
    # url = 'https://www.rbc.ru/finances/'
    # date_start, date_end = datetime(2025, 4, 20), datetime(2025, 5, 5)

    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--disable-dev-shm-usage')
    # chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument('--enable-unsafe-webgpu')
    # chrome_options.add_argument('--use-angle=swiftshader')
    # chrome_options.add_argument('--enable-features=SwiftShader')
    # chrome_options.add_argument('--ignore-gpu-blocklist')
    # chrome_options.add_argument('--disable-software-rasterizer')
    # chrome_options.add_argument('--disable-extensions')
    # chrome_options.add_argument('--disable-setuid-sandbox')
    # chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')  
    # driver = webdriver.Chrome(options=chrome_options)

    # parser = RBKParser(url=url, driver=driver,
    #                    date_range=(date_start, date_end))
    
    # new = parser.parse_news_page('https://www.rbc.ru/finances/24/04/2025/6809a8b49a7947500db9177f')
    # print(new)
    pass


if __name__ == '__main__':
    main()
