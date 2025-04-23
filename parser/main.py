import re
from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from datetime import datetime

from list_news import LentaParser
from excel_generation import ExcelGeneration
from llm_model import GigaChatApi
import os


# Текущая дата и время
current_datetime = datetime.now()
current_date = current_datetime.date()
print("Текущая дата:", current_date)

date_range = ['2025-04-22', '2025-04-22']
url_lenta = 'https://www.banki.ru/news/lenta/'

def main():

    giga_chat_api = os.environ.get('API_GIGA_CHAT')
    print(giga_chat_api)

    driver = webdriver.Chrome()
    bank = LentaParser(url_lenta, driver, count_pages=2, date_range=date_range)
    news = bank.news_page()
    giga = GigaChatApi(api=giga_chat_api)

    # for idx, item in enumerate(news, 1):
    #     print(f"\nНовость #{idx}:")
    #     print(f"Заголовок: {item['title']}")
    #     print(f"URL: {item['url']}")
    #     print(f"Текст: {item['content'][:200]}...")
    #     print(f"Дата публикации: {item['date_publication']}")

    for item in news:
        item['Дата публикации'] = item.pop('date_publication')
        item['Заголовок'] = item.pop('title')
        """Подкрутили LLM для summary"""
        item['Краткая суть'] = giga.take_answer(item['content']) if len(item['content']) > 150 else item['content']
        item['Источник'] = 'banki.ru'
        item['Ссылка'] = item.pop('url')
        del item['content']  # Можно удалить, если не нужно в таблице

    save_excel = ExcelGeneration(news, 'news3.xlsx')

if __name__ == '__main__':
    main()

