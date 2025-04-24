from selenium import webdriver
from llm import llm_model
from parser.switch import switch
from excel import excel_generation
from dotenv import load_dotenv
import os

load_dotenv()


class Main:
    def __init__(self, sources, date_range, keywords=None):
        giga_chat_api = os.getenv('API_KEY')
        print(giga_chat_api)
        self.giga = llm_model.GigaChatApi(api=giga_chat_api)
        driver = webdriver.Chrome()

        self.news_pages = []  # Массив для обработки страниц из различных источников
        for source in sources:
            url_class = switch(source)
            url, class_parser = url_class['url'], url_class['class_link']

            self.bank = class_parser(url, driver, date_range=date_range)
            self.news_pages.extend(self.bank.news_page())

        self.__print_news_tittles()

    def get_list_news(self):
        return self.news_pages

    def __print_news_tittles(self):
        for item in self.news_pages:
            print(f"\nНовость #{item['id']}:")
            print(f"Заголовок: {item['title']}")
            print(f"URL: {item['url']}")
            print(f"Текст: {item['content'][:200]}...")
            print(f"Дата публикации: {item['date_publication']}")

    def export_to_excel(self, mask):
        mask_news = []

        for item in self.news_pages:
            new_one = {}
            if item['id'] in mask:
                new_one['Дата публикации'] = item['date_publication']
                new_one['Заголовок'] = item['title']
                """Подкрутили LLM для summary"""
                new_one['Краткая суть'] = self.giga.take_answer(item['content']) if len(
                    item['content']) > 150 else item['content']
                new_one['Источник'] = 'banki.ru'
                new_one['Ссылка'] = item['url']
                # del item['content']  # Можно удалить, если не нужно в таблице
                # del item['id']
                mask_news.append(new_one)

        return excel_generation.ExcelGeneration(mask_news).generate()
