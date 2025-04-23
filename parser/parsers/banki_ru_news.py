import re
import time
from bs4 import BeautifulSoup
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException


class BankiRuParser:
    def __init__(self, url, driver, date_range, key_words=None, count_pages=5):
        self.url = url
        self.driver = driver
        self.count_pages = count_pages
        self.driver.get(url)
        self.TIMEOUT = 0.2
        self.news = []

        self.date_start = datetime.strptime(
            date_range[0].strip(), "%Y-%m-%d").date()
        self.date_end = datetime.strptime(
            date_range[1].strip(), "%Y-%m-%d").date()

        self.pattern_lenta = re.compile(r'/news/lenta/\?id')
        self.pattern_key_words = None
        if key_words:
            escaped_words = [re.escape(word.lower()) for word in key_words]
            self.pattern_key_words = re.compile('|'.join(escaped_words))

        self.urls = []

    def urls_list(self):
        for page_num in range(1, self.count_pages + 1):
            time.sleep(self.TIMEOUT)

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            news_blocks = soup.find_all(
                'div', class_='NewsItemstyled__StyledNewsList-sc-jjc7yr-0')

            for block in news_blocks:
                try:
                    # Получаем дату блока
                    date_tag = block.find(
                        'h2', class_='NewsItemstyled__StyledNewsDate-sc-jjc7yr-1')
                    if not date_tag:
                        continue

                    news_date = datetime.strptime(
                        date_tag.text.strip(), "%d.%m.%Y").date()

                    # Пропускаем новости вне диапазона
                    if not (self.date_start <= news_date <= self.date_end):
                        print(f"Пропускаем блок вне диапазона: {news_date}")
                        continue

                    # Извлекаем ссылки на новости из этого блока
                    for link in block.find_all('a', class_='NewsItemstyled__StyledItemTitle-sc-jjc7yr-7'):
                        href = link.get('href')
                        text = link.text

                        if not href or not re.search(self.pattern_lenta, href):
                            continue

                        if self.pattern_key_words:
                            if not re.search(self.pattern_key_words, text.lower()):
                                continue

                        self.urls.append('https://www.banki.ru' + href)

                except Exception as e:
                    print(f"Ошибка в блоке: {e}")

            # Переход на следующую страницу
            next_page = page_num + 1
            try:
                self.driver.get(
                    f'https://www.banki.ru/news/lenta/?page={next_page}')
            except WebDriverException as e:
                print(f"Не удалось загрузить страницу {next_page}: {e}")
                break

        return self.urls

    def parse_news_page(self, url):
        """Парсинг полного текста новости"""
        self.driver.get(url)
        time.sleep(self.TIMEOUT)

        title = self.driver.find_element(By.TAG_NAME, 'h1').text.strip()
        # Извлекаем строку вида "Дата публикации: 20.04.2025 06:00"
        date_raw = self.driver.find_element(
            By.XPATH, "//span[@data-test = 'news-date-published']").text.strip()

        # Удаляем префикс и преобразуем в datetime
        date_str = date_raw.replace("Дата публикации: ", "")
        date_publication = datetime.strptime(date_str, "%d.%m.%Y %H:%M")

        content = '\n'.join([p.text.strip()
                            for p in self.driver.find_elements(By.TAG_NAME, 'p')])
        return title, content, date_publication

    def news_page(self):
        news_urls = self.urls_list()
        for url in news_urls[:2]:
            try:
                title, content, date_publication = self.parse_news_page(url)
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
