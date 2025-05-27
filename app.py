import re

from flask import Flask, render_template, request, send_file
from parser.main_parser import Main
from parser.switch import get_sources


app = Flask(__name__)
app.secret_key = 'secret_key'
NEWS_SOURCES = get_sources()
main = None


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', news_sources=NEWS_SOURCES, news=None)


@app.route('/search', methods=['POST'])
def search():
    global main
    keywords = request.form.get("keywords")
    sources = request.form.getlist("sources")
    date_range = request.form.get("date_range")
    main = Main(sources=sources, keywords=keywords, date_range=date_range)
    news = main.get_list_news()
    return render_template("index.html", news_sources=NEWS_SOURCES, news=news)


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
