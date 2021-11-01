from bs4 import BeautifulSoup as bs
import re
import pandas as pd
import requests

# https://hh.ru/search/vacancy?text={vac}tist&area=1&salary=&currency_code=RUR&experience=doesNotMatter&order_by=relevance&search_period=0&items_on_page=100&no_magic=true&L_save_area=true

vac = input('Введите вакансию которую вы ищете:  ')
vac = vac.replace(' ', '+')

url = str(f"https://hh.ru/search/vacancy?text={vac}")

# Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36', }

response = requests.get(url=url, headers=headers).text

soup = bs(''.join(response), features='lxml')

div_p = soup.find_all('div', attrs={'class': "vacancy-serp-item",
                                    'data-qa': re.compile('^vacancy-serp__vacancy vacancy-serp__vacancy')})
hh = soup.find('img', attrs={'src': "https://i.hh.ru/logos/svg/hh.ru.svg?v=20052019", 'class': "print-logo"})['alt']
hh = f'https://{hh}'
m = []
for i in div_p:
    vacance = i.find('a', attrs={'class': "bloko-link", 'data-qa': "vacancy-serp__vacancy-title"}).string
    zp = i.find('span', attrs={'data-qa': "vacancy-serp__vacancy-compensation",
                               'class': "bloko-header-section-3 bloko-header-section-3_lite"})
    if zp != None:
        zp = zp.contents
        zp = " ".join(zp)
        zp = zp.replace('\u202f', '')
        zp = zp.replace('–', '')
        zp = zp.split(' ')
        while zp.count('') != 0:
            zp.remove('')
        if zp[0] == 'от':
            zp1 = zp[1]
            zp2 = None
            zp3 = zp[2]
        elif zp[0] == 'до':
            zp1 = None
            zp2 = zp[1]
            zp3 = zp[2]
        else:
            zp1 = zp[0]
            zp2 = zp[1]
            zp3 = zp[2]
    else:
        zp1 = None
        zp2 = None
        zp3 = None

    href = i.find('a', attrs={'class': "bloko-link", 'data-qa': "vacancy-serp__vacancy-title"})['href']
    li = [vacance, zp1, zp2, zp3, href, hh]
    m.append(li)

df = pd.DataFrame(m, columns=['Наименование вакансии', 'Минимальная зарплата', 'Максимальная зарплата', 'Валюта',
                              'Ссылка на вакансию', 'Ссылка на сайт вакансий'],
                  index=[i for i in range(1, len(m) + 1)])

print(df)

df.to_excel("output.xlsx")
