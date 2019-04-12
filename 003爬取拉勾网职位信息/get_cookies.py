import requests
import urllib.request
from bs4 import BeautifulSoup
from urllib.parse import urlencode

params = {
    'labelWords': '',
    'fromSearch': 'true',
    'suginput': ''
}

# https://www.lagou.com/jobs/list_python?labelWords=&fromSearch=true&suginput=
base_url = 'https://www.lagou.com/jobs/list_python?'
url = base_url + urlencode(params)

# response = requests.get(url)
# print(response.text)

html = urllib.request.urlopen(url)
bsobj = BeautifulSoup(html, 'lxml')
print(bsobj)