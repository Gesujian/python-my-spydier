import urllib.request
# client_id 为官网获取的AK， client_secret 为官网获取的SK
host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&c' \
       'lient_id=1KariOhd8HcILKFWqRUcaOg8&client_secret=HupclSiCElxuM9npQZHokFHnw5aWnPQy'
request = urllib.request.urlopen(host)
content =request.read()
if (content):
    print(content)