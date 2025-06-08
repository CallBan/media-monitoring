import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from llm import llm_model
from parser.switch import switch
from excel import excel_generation
from dotenv import load_dotenv
from datetime import datetime
import os
from parser.set_value import shared_state
import asyncio


load_dotenv()

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

class Main:
    def __init__(self, sources, date_range, keywords=None):
        giga_chat_api = os.getenv('API_KEY')
        self.giga = llm_model.GigaChatApi(api=giga_chat_api)
        self.sources = sources
        self.news_pages = []

        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0...')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        self.driver = webdriver.Chrome(options=options)

        try:
            if ' to ' in date_range:
                start_str, end_str = date_range.split(' to ')
                self.date_start = datetime.strptime(
                    start_str.strip(), "%Y-%m-%d").date()
                self.date_end = datetime.strptime(
                    end_str.strip(), "%Y-%m-%d").date()
            else:
                single_date = datetime.strptime(
                    date_range.strip(), "%Y-%m-%d").date()
                self.date_start = self.date_end = single_date
        except Exception as e:
            print(f"Ошибка разбора даты: {e}")
            today = datetime.today().date()
            self.date_start = self.date_end = today

        # можно добавить другие символы и пробел
        symbols = re.compile(r'[,.!?\s]+')

        words = re.split(symbols, keywords)
        words = [word for word in words if word]

        escaped_words = [re.escape(word.lower()) for word in words]
        self.pattern_key_words = re.compile('|'.join(escaped_words))
        print(self.pattern_key_words)


    async def main_cycle(self):
        for idx, source in enumerate(self.sources, 1):
            url_class = switch(source)
            url, class_parser = url_class['url'], url_class['class_link']
            try:
                shared_state.update(url_class['name'], idx, len(self.sources))
                self.bank = class_parser(url, self.driver, date_range=(
                    self.date_start, self.date_end), pattern=self.pattern_key_words, headers = headers)
                self.news_pages.extend(self.bank.news_page())
            except Exception as e:
                print(f"У нас отвалился парсер {source}, по причине ошибки {e}")
        self.driver.quit()

        for idx in range(len(self.news_pages)):
            self.news_pages[idx]['id'] = idx + 1

        self.__print_news_tittles()

    def get_list_news(self):
        return self.news_pages

    def __print_news_tittles(self):
        try:
            for item in self.news_pages:
                print(f"\nНовость #{item['id']}:")
                print(f"Заголовок: {item['title']}")
                print(f"URL: {item['url']}")
                print(f"Текст: {item['content'][:200]}...")
                print(f"Дата публикации: {item['date_publication']}")
                print(f"Источник: {item['source']}")
        except Exception as e:
            print(e, "Ловим None в content")


    def export_to_excel(self, mask):
        mask_news = []

        for item in self.news_pages:
            new_one = {}
            if item['id'] in mask and item['content'] is not None:
                new_one['Дата публикации'] = item['date_publication']
                new_one['Заголовок'] = item['title']
                """Подкрутили LLM для summary"""
                new_one['Краткая суть'] = self.giga.take_answer(item['content']) if len(
                    item['content']) > 150 else item['content']
                new_one['Источник'] = item['source']
                new_one['Ссылка'] = item['url']
                print(new_one)
                mask_news.append(new_one)

        return excel_generation.ExcelGeneration(mask_news).generate()
