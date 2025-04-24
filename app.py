from flask import Flask, render_template, request
from parser.main_parser import Main
from parser.switch import get_sources

main = Main(['banki-ru'], '2025-04-22')
main.export_to_excel([1, 2, 3])
# app = Flask(__name__)
# app.secret_key = 'secret_key'
# NEWS_SOURCES = get_sources()
#
#
# @app.route('/search', methods=['POST'])
# def search():
#     keywords = request.form.get("keywords")
#     sources = request.form.getlist("sources")
#     date_range = request.form.get("date_range")
#     main = Main(sources=sources, keywords=keywords, date_range=date_range)
#     news = main.get_list_news()
#     return render_template("index.html", news_sources=NEWS_SOURCES, news=news)
#
#
# @app.route('/', methods=['GET'])
# def index():
#     return render_template('index.html', news_sources=NEWS_SOURCES, news=None)
#
#
# if __name__ == '__main__':
#     app.run(debug=True)