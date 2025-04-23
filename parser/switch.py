from parser.parsers import ria_news, tass_news, banki_ru_news

dict_sources = {'ria': ['https://ria.ru/economy/', ria_news.RIAParser],
                'tass': ['https://tass.com/', tass_news.TASSParser],
                'banki-ru': ['https://www.banki.ru/news/lenta/', banki_ru_news.BankiRuParser]}


def switch(source):
    return dict_sources[source]
