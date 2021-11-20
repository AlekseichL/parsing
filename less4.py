'''Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru,
lenta.ru, yandex-новости. Для парсинга использовать XPath. Структура данных должна содержать:
название источника;
наименование новости;
ссылку на новость;
дата публикации.'''

import pandas as pd
from lxml import html
import requests
from datetime import datetime
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client['mail']
news = db.news

new = []

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'
}

keys = ('title', 'date', 'link')
date_format = '%Y-%m-%dT%H:%M:%S%z'

link_mail_ru = 'https://mail.ru/'

request = requests.get(link_mail_ru, headers=headers)
root = html.fromstring(request.text)


news_links = root.xpath('''(//li[@data-testid =  "general-news-item"] | //li[@data-testid =  "extra-news-item-ml"])
                            //a[contains(@href, "https")]/@href''')

news_text = root.xpath('''(//li[@data-testid =  "general-news-item"]//p |
                           //li[@data-testid =  "general-news-item"]/div/a[contains(@href, "https")] | 
                           //li[@data-testid =  "extra-news-item-ml"]//a[contains(@href, "https")])
                           /text()''')

for i in range(len(news_text)):
    news_text[i] = news_text[i].replace(u'\xa0', u' ')
    news_text[i] = news_text[i].replace(u'\t', u'')

news_links_temp = []
for item in news_links:
    item = item.split('/')
    news_links_temp.append('/'.join(item[0:(len(item)-1)]))

news_links = news_links_temp
del (news_links_temp)

news_date = []

for item in news_links:
    request = requests.get(item, headers=headers)
    root = html.fromstring(request.text)
    date = root.xpath('''//span[@class="note__text breadcrumbs__text js-ago"]/@datetime | 
                         //div[@role="navigation"]//time/@datetime |
                         //time[@class="note__text breadcrumbs__text js-ago"]/@datetime 
                         ''')

    if date == []:
        news_date.extend(['Дата отсутствует'])
    else:
        news_date.extend(date)

for i in range(len(news_date)):
    if news_date[i] != 'Дата отсутствует':
        news_date[i] = str(datetime.strptime(news_date[i], date_format))

for item in list(zip(news_text, news_date, news_links)):
    news_dict = {}
    for key, value in zip(keys, item):
        news_dict[key] = value

    news_dict['source'] = 'mail.ru'
    new.append(news_dict)

'''Сложить собранные новости в БД'''
for it in new:
    news.insert_one(it)

for it in news.find({}):
    print(it)