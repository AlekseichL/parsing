from bs4 import BeautifulSoup as bs
import re
import pandas as pd
import requests
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client['hh']
vacancy = db.vacancies

vac = input('Введите вакансию которую вы ищете:  ')
vac = vac.replace(' ', '+')

itr = 0
url = f'https://hh.ru/search/vacancy?text={vac}&area=1&salary=&currency_code=RUR&experience=doesNotMatter&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true&page={itr}'

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36', }

m = []

while requests.get(url=url, headers=headers).status_code != 404:
    url = f'https://hh.ru/search/vacancy?text={vac}&area=1&salary=&currency_code=RUR&experience=doesNotMatter&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true&page={itr}'
    print("Обрабатывается страница № " + str(itr + 1))
    response = requests.get(url=url, headers=headers).text

    soup = bs(''.join(response), features='lxml')

    div_p = soup.find_all('div', attrs={'class': "vacancy-serp-item",
                                        'data-qa': re.compile('^vacancy-serp')})
    if div_p == []:
        break

    hh = 'https://hh.ru'
    for i in div_p:
        vacance = i.find('a', attrs={'class': "bloko-link", 'data-qa': "vacancy-serp__vacancy-title"}).string
        zp = i.find('span', attrs={'data-qa': "vacancy-serp__vacancy-compensation",
                                   'class': "bloko-header-section-3 bloko-header-section-3_lite"})
        d = {}
        if zp != None:
            zp = zp.contents
            zp = " ".join(zp)
            zp = zp.replace('\u202f', '')
            zp = zp.replace('–', '')
            zp = zp.split(' ')
            while zp.count('') != 0:
                zp.remove('')
            if zp[0] == 'от':
                zp1 = int(zp[1])
                zp2 = None
                zp3 = zp[2]
            elif zp[0] == 'до':
                zp1 = None
                zp2 = int(zp[1])
                zp3 = zp[2]
            else:
                zp1 = int(zp[0])
                zp2 = int(zp[1])
                zp3 = zp[2]
        else:
            zp1 = None
            zp2 = None
            zp3 = None

        href = i.find('a', attrs={'class': "bloko-link", 'data-qa': "vacancy-serp__vacancy-title"})['href']

        d['Наименование вакансии'] = vacance
        d['Минимальная зарплата'] = zp1
        d['Максимальная зарплата'] = zp2
        d['Валюта'] = zp3
        d['Ссылка на вакансию'] = href
        d['Ссылка на сайт вакансий'] = hh

        m.append(d)

    itr += 1

for i in m:
    l=0
    for item in vacancy.find(i):
        if type(item) == dict:
            l+=1
            break
    if l>0:
        continue
    else:
        vacancy.insert_one(i)
n=0
for it in vacancy.find({}):
    n += 1
    print(n)
    print(it)

# print(m)
# df = pd.DataFrame(m, index=[i for i in range(1, len(m) + 1)])
#
# print(df)
#
# df.to_excel("output.xlsx")
