from banki_ru_parser import get_news

news = get_news()
for idx, item in enumerate(news, 1):
    print(f"\nНовость #{idx}:")
    print(f"Заголовок: {item['title']}")
    print(f"URL: {item['url']}")
    print(f"Текст: {item['content'][:200]}...")
