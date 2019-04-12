import time

from urllib.request import urlopen
from urllib.request import urlretrieve
from bs4 import BeautifulSoup

def get_img(url,i):
	resp = urlopen(url)
	imgsoup = BeautifulSoup(resp, "html.parser")
	imgP = imgsoup.find("p", class_="vsbcontent_img").find("img").get("src")
	imgUrls = "http://www.hrbcu.edu.cn/" + imgP
	print(imgUrls)
	urlretrieve(imgUrls, "C:/Users/葛苏健/Desktop/py/python小案例/001爬取哈商大官网校园风光/pic/"+str(i)+".jpg")
URl="http://www.hrbcu.edu.cn/info/1045/1001.htm"
headers={"User-Agent":" Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763"}
for i in range(1094,1095):
	try:
		URl = "http://www.hrbcu.edu.cn/info/1045/" + str(i) + ".htm"
		get_img(URl, i)
		time.sleep(4)
	finally:
		print("此链接失效")