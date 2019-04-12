import json
import csv
import lxml
import requests
from bs4 import BeautifulSoup as BS

def save_as_txt(list):
    filename = 'info.txt'
    with open(filename, 'a',encoding='utf-8') as file:
        file.write('\n'.join(list))

def save_as_json(dict):
    filename = 'info.json'
    with open(filename, 'a',encoding='utf-8') as file:
        file.write(json.dumps(dict, indent=4, ensure_ascii=False)+',\n')

def save_as_csv(list):
    filename = 'info.csv'
    with open(filename, 'a', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(list)


url = "https://www.zhihu.com/explore"

response = open('html.txt',encoding='utf-8')
bsobj = BS(response, 'lxml')
items = bsobj.find_all('div', class_='explore-feed feed-item', )
for item in items:
    question = item.a.string
    author = item.find(name='a', class_='author-link').get_text()
    answer = item.textarea.string
    info = [question,author,answer,]
    dict = {'question':question, 'author':author, 'answer':answer}
    save_as_txt(info)
    save_as_json(dict)
    save_as_csv(info)
