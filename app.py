import re

from flask import Flask, render_template, request, send_file, Response
from parser.main_parser import Main
from parser.switch import get_sources
import asyncio
from parser.set_value import shared_state
import json
import time
from threading import Thread

app = Flask(__name__)
app.secret_key = 'secret_key'
NEWS_SOURCES = get_sources()
main = None


def run_async_task(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro)

@app.route('/stream')
def stream():
    def event_gen():
        while True:
            data = shared_state.get_data()
            json_data = json.dumps(data)  # Сериализуем словарь в JSON строку
            yield f"data: {json_data}\n\n"  # Отправляем как корректный JSON
            time.sleep(1)

    return Response(event_gen(), mimetype="text/event-stream")

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', news_sources=NEWS_SOURCES, news=None)



@app.route('/search', methods=['POST'])
def search():
    global main
    keywords = request.form.get("keywords")
    sources = request.form.getlist("sources")
    date_range = request.form.get("date_range")

    # Инициализация основного класса
    main = Main(sources=sources, keywords=keywords, date_range=date_range)
    p1 = Thread(target=run_async_task, args=(main.main_cycle(),), daemon=True)
    p1.start()
    p1.join()
    # Получаем новости
    news_pages = main.get_list_news()
    # Очищаем и предобрабатываем данные
    clear_news = []
    for item in news_pages:
        if not item:  # Пропускаем None-элементы
            continue

        try:
            preprocess_item = {
                'id': item.get('id', ''),  # Используем get() для безопасного доступа
                'title': item.get('title', 'Без заголовка'),
                'url': item.get('url', '#'),
                'content': item.get('content', '')[:300],  # Обрезаем контент
                'date_publication': item.get('date_publication', 'Дата не указана'),
                'source': item.get('source', 'Неизвестный источник')
            }
            clear_news.append(preprocess_item)

        except Exception as e:
            print(f"Ошибка обработки элемента: {e}")
            continue

    return render_template("index.html",
                           news_sources=NEWS_SOURCES,
                           news=clear_news if clear_news else None)


@app.route('/export', methods=['POST'])
def export():
    selected_news = list(map(int, request.form.getlist("selected_news")))
    file = main.export_to_excel(selected_news)
    return send_file(
        file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='news.xlsx'
    )


if __name__ == '__main__':
    app.run(debug=True)

