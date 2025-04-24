from flask import Flask, render_template, request
from parser.main_parser import Main
from parser.switch import get_sources

app = Flask(__name__)
app.secret_key = 'secret_key'
NEWS_SOURCES = get_sources()
# Для тестирования
# news = [
#     {'id': 123, 'url': 'https://ya.ru/', 'title': 'Загловок 1', 'content': 'Новость 1'},
#     {'id': 456, 'url': 'https://ya.ru/', 'title': 'Загловок 2', 'content': 'Новость 2'}
# ]

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', news_sources=NEWS_SOURCES, news=None)


@app.route('/search', methods=['POST'])
def search():
    keywords = request.form.get("keywords")
    sources = request.form.getlist("sources")
    date_range = request.form.get("date_range")
    main = Main(sources=sources, keywords=keywords, date_range=date_range)
    news = main.get_list_news()
    return render_template("index.html", news_sources=NEWS_SOURCES, news=news)


@app.route('/export', methods=['POST'])
def export():
    # список id-шников выбранных новостоей (тип - string)
    selected_news = request.form.getlist("selected_news")
    """
    TODO: отправлять excel-файл 
    """
    return render_template("result.html")


if __name__ == '__main__':
    app.run(debug=True)