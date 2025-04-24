from selenium import webdriver
from llm import llm_model
from parser.switch import switch
from excel import excel_generation
import os


class Main:
    def __init__(self, sources, date_range, keywords = None):
        giga_chat_api = os.environ.get('API_GIGA_CHAT')
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
        for idx, item in enumerate(self.news_pages, 1):
            print(f"\nНовость #{idx}:")
            print(f"Заголовок: {item['title']}")
            print(f"URL: {item['url']}")
            print(f"Текст: {item['content'][:200]}...")
            print(f"Дата публикации: {item['date_publication']}")

    def export_to_excel(self, mask):
        mask_news = []
        for i in mask:
            mask_news.append(dict(self.news_pages[i]))

        for item in mask_news:
            item['Дата публикации'] = item.pop('date_publication')
            item['Заголовок'] = item.pop('title')
            """Подкрутили LLM для summary"""
            item['Краткая суть'] = self.giga.take_answer(item['content']) if len(item['content']) > 150 else item['content']
            item['Источник'] = 'banki.ru'
            item['Ссылка'] = item.pop('url')
            del item['content']  # Можно удалить, если не нужно в таблице
        save_excel = excel_generation.ExcelGeneration(mask_news, 'news3.xlsx')

# sources = ['banki.ru']
# date_range = ['2025-04-22', '2025-04-23']
# main = Main(sources=sources, date_range=date_range)