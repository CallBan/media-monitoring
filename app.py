from flask import Flask, render_template, request
from parser.main_parser import Main

app = Flask(__name__)
app.secret_key = 'secret_key'

# Временные данные для примера
NEWS_SOURCES = [
    {'id': 'ria', 'name': 'РИА Новости'},
    {'id': 'tass', 'name': 'ТАСС'},
    {'id': 'banki-ru', 'name': 'Banki.ru'}
]


@app.route('/', methods=['GET', 'POST'])
def start_parsing():
    if request.method == "POST":
        keywords = request.form.get("keywords")
        sources = request.form.getlist("sources")
        date_range = request.form.get("date_range")
        main = Main(sources=sources, keywords=keywords, date_range=date_range)
    return render_template("index.html", news_sources=NEWS_SOURCES)


@app.route('/')
def index():
    return render_template('index.html', news_sources=NEWS_SOURCES)


if __name__ == '__main__':
    app.run()
