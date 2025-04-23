from selenium import webdriver
from backend.llm import llm_model
from backend.switch import switch
import os

date_range = ['2025-04-22', '2025-04-22']
sources = ['banki-ru']
class Main:
    def __init__(self, sources, date_range, keywords = None):
        giga_chat_api = os.environ.get('API_GIGA_CHAT')
        print(giga_chat_api)
        self.giga = llm_model.GigaChatApi(api=giga_chat_api)

        driver = webdriver.Chrome()
        self.news_pages = [] # Массив для обработки страниц из различных источников
        for source in sources:
            url_class = switch(source)
            url, class_parser = url_class[0], url_class[1]

            self.bank = class_parser(url, driver, date_range=date_range)
            self.news_pages.extend(self.bank.news_page())

        self.__process_parsing()

    def __process_parsing(self):

        for idx, item in enumerate(self.news_pages, 1):
            print(f"\nНовость #{idx}:")
            print(f"Заголовок: {item['title']}")
            print(f"URL: {item['url']}")
            print(f"Текст: {item['content'][:200]}...")
            print(f"Дата публикации: {item['date_publication']}")



        # for news_one_source in self.news_pages:
        #     for item in news_one_source:
        #         item['Дата публикации'] = item.pop('date_publication')
        #         item['Заголовок'] = item.pop('title')
        #         """Подкрутили LLM для summary"""
        #         item['Краткая суть'] = self.giga.take_answer(item['content']) if len(item['content']) > 150 else item['content']
        #         item['Источник'] = 'banki.ru'
        #         item['Ссылка'] = item.pop('url')
        #         del item['content']  # Можно удалить, если не нужно в таблице
        #     save_excel = excel_generation.ExcelGeneration(news_one_source, 'news3.xlsx')



