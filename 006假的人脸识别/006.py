# encoding:utf-8
import base64
import requests
import urllib.request
import urllib.parse
'''
通用物体和场景识别
'''
request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general"
# 二进制方式打开图片文件
f = open('p632880577.jpg', 'rb')
img = base64.b64encode(f.read())
params = {"image":img,'top_num': 5}
data = urllib.parse.urlencode(params)
header={'Content-Type':'application/x-www-form-urlencoded'}
access_token = "24.379847171d39c8b6edb9492606e9219d.2592000.1555938561.282335-15832577"
request_url = request_url + "?access_token=" + access_token
request = requests.post(url=request_url, data=data, headers=header)
content = request.text
if content:
    print(content)