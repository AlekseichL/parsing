# Написать программу, которая собирает входящие письма из своего или тестового почтового ящика и сложить данные о письмах в базу данных
# (от кого, дата отправки, тема письма, текст письма полный)
# Логин тестового ящика: study.ai_172@mail.ru
# Пароль тестового ящика: NextPassword172#

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import datetime
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client['mail']
let = db.letter

chrome_options = Options()
chrome_options.add_argument("--start-maximized")

driver = webdriver.Chrome('/home/user/Рабочий стол/PyCharm/chromedriver', options=chrome_options)
driver.implicitly_wait(10)

driver.get('https://mail.ru/')

elem = driver.find_element(By.XPATH, '//div[@class="email-input-container svelte-1tib0qz"]/input')
elem.send_keys('study.ai_172')
elem.send_keys(Keys.ENTER)

elem = driver.find_element(By.XPATH, '//div//input[@type="password"]')
elem.send_keys('NextPassword172#')
elem.send_keys(Keys.ENTER)

block = driver.find_element(By.CLASS_NAME, 'dataset__items')

li = []
letters = block.find_elements(By.TAG_NAME, 'a')
while letters[-1].get_attribute(
        'class') != "list-letter-spinner llct list-letter-spinner_default list-letter-spinner_hidden":
    letters = block.find_elements(By.TAG_NAME, 'a')
    for i in letters:
        url = i.get_attribute('href')
        li.append(url)
    actions = ActionChains(driver)
    actions.move_to_element(letters[-1])
    actions.perform()

li = set(li)
d = []

month = {'января,': '01', 'февраля,': '02', 'марта,': '03', 'апреля,': '04', 'мая,': '05', 'июня,': '06', 'июля,': '07',
         'августа,': '08', 'сентября,': '09', 'октября,': '10', 'ноября,': '11', 'декабря,': '12'}

now = datetime.datetime.now()
for i in li:
    di = {}
    data = driver.get(i)
    di['contact'] = driver.find_element(By.XPATH, '//span[@class="letter-contact"]').get_attribute('title')
    date = driver.find_element(By.XPATH, '//div[@class="letter__date"]').text.split(' ')
    if date[0] == 'Вчера,':
        date[0] = now.strftime(f"{now.day - 1}.%m.%Y,")
    elif date[0] == 'Сегодня,':
        date[0] = now.strftime("%d.%m.%Y,")
    else:
        date[0] = f'{date[0]}.{month[date[1]]}.2021,'  # в ящике нет писем предыдущих лет
        date.pop(1)
    date = " ".join(date)
    di['date'] = date
    di['theme'] = driver.find_element(By.XPATH, '//h2[@class="thread__subject"]').text
    di['text'] = driver.find_element(By.XPATH, '//div[@class="letter__body"]').text
    d.append(di)

driver.quit()

for it in d:
    let.insert_one(it)

for it in let.find({}):
    print(it)
