from langchain_core.messages import SystemMessage
from langchain_gigachat.chat_models import GigaChat
import time


class GigaChatApi:
    def __init__(self, api):

        self.giga = GigaChat(
            # Для авторизации запросов используйте ключ, полученный в проекте GigaChat API
            credentials=api,
            verify_ssl_certs=False,
        )

    def take_answer(self, text_page):
        start = time.time()
        limit = min(5000, len(text_page))
        prompt = f"""
                Ты должен сделать небольшое summary по прочитанному тексту
                Вот текст: {text_page[:limit]}
                """
        messages = [
            SystemMessage(
                content=prompt
            )
        ]
        print("Передача текста в модель")
        res = self.giga.invoke(messages)
        messages.append(res)
        summary = res.content
        finish = time.time()
        print(f"Время генерации ответа: {finish - start}")
        return summary
