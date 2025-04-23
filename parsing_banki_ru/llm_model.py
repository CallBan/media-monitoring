from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat
import os
import time
giga_chat_api = os.environ.get('API_GIGA_CHAT')
print(giga_chat_api)
class GigaChatApi:
    def __init__(self):
        giga_chat_api = os.environ.get('API_GIGA_CHAT')
        self.giga = GigaChat(
            # Для авторизации запросов используйте ключ, полученный в проекте GigaChat API
            credentials=giga_chat_api,
            verify_ssl_certs=False,
        )

    def take_answer(self, text_page):
        start = time.time()
        prompt = f"""
                Ты должен сделать небольшое summary по прочитанному тексту
                Вот текст: {text_page}
                """
        messages = [
            SystemMessage(
                content = prompt
            )
        ]
        print("Передача текста в модель")
        res = self.giga.invoke(messages)
        messages.append(res)
        summary = res.content
        finish = time.time()
        print(f"Время генерации ответа: {finish - start}")
        return summary

goga = GigaChatApi()
print(goga.take_answer("А куда еще короче?"))


