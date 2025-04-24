from parser.parsers import ria_news, banki_ru_news


def get_sources():
    return [
        {'id': 'ria', 'url': 'https://ria.ru/economy/',
            'name': 'РИА Новости', 'class_link': ria_news.RIAParser},
        {'id': 'banki-ru', 'url': 'https://www.banki.ru/news/lenta/', 'name': 'Banki.ru',
         'class_link': banki_ru_news.BankiRuParser},
    ]


def switch(source_id):
    return next((item for item in get_sources() if item['id'] == source_id), None)
