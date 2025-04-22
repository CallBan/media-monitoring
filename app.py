from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = 'secret_key'

# Временные данные для примера
NEWS_SOURCES = [
    {'id': 'ria', 'name': 'РИА Новости'},
    {'id': 'tass', 'name': 'ТАСС'},
    {'id': 'banki-ru', 'name': 'Banki.ru'}
]


@app.route('/')
def index():
    return render_template('index.html', news_sources=NEWS_SOURCES)


if __name__ == '__main__':
    app.run(debug=True)
