from parser.parsers import ria_news, banki_ru_news, rbk_news, komersant_news, lenta_ru_news, tass_news, garant_ru_news, iz_ru_news, rg_ru_news


def get_sources():
    return [
        {'id': 'ria', 'url': 'https://ria.ru/economy/',
            'name': 'РИА Новости', 'class_link': ria_news.RIAParser},
        {'id': 'banki-ru', 'url': 'https://www.banki.ru/news/lenta/', 'name': 'Banki.ru',
         'class_link': banki_ru_news.BankiRuParser},
        {'id': 'rbk', 'url': 'https://www.rbc.ru/finances/', 'name': 'РБК',
         'class_link': rbk_news.RBKParser},
        {'id': 'kommersant', 'url': 'https://www.kommersant.ru/rubric/3?from=burger', 'name': 'Коммерсантъ',
         'class_link': komersant_news.KomersantParser},
        {'id': 'lenta-ru', 'url': 'https://lenta.ru/rubrics/economics/', 'name': 'Lenta.ru',
         'class_link': lenta_ru_news.LentaRuParser},
        {'id': 'tass', 'url': 'https://tass.ru/ekonomika', 'name': 'ТАСС',
         'class_link': tass_news.TASSParser},
        {'id': 'garant', 'url': 'https://www.garant.ru/news/', 'name': 'Гарант.ру',
         'class_link': garant_ru_news.GarantRuParser},
        {'id': 'iz-ru', 'url': 'https://iz.ru/rubric/ekonomika', 'name': 'Известия',
         'class_link': iz_ru_news.IzRuParser},
        {'id': 'rg-ru', 'url': 'https://rg.ru/tema/ekonomika', 'name': 'RG.RU',
         'class_link': rg_ru_news.RgRuParser}
    ]


def switch(source_id):
    return next((item for item in get_sources() if item['id'] == source_id), None)
