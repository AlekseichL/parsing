
#_ 1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
# сохранить JSON-вывод в файле *.json.

import requests
import json

username = input('Введите username: ')
if username == '':
    username = 'AlekseichL'
else:
    username

# https://api.github.com/users/USERNAME/repos
url = f'https://api.github.com/users/{username}/repos'

req = requests.get(url)
req = req.json()

print('Результат:')
print(req)


rep = []
for i in req:
    rep.append(i['name'])
print(f'Список репозиториев пользователя {username}:')
print(rep)

with open('rep.json', 'w') as f:
    json_rep = json.dump(rep, f)
    
