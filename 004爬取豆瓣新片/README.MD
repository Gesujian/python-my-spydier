##### 没有全部完成，没有过程解释，只有整体框架，等我写完，下周末继续完成。
---
如题，我要爬取豆瓣电影Top250的相关信息，包括但不限于——电影排名、电影名、电影导演、主演、编剧、类型、制片国家、语言、  上映时间、片长、别名、评分、评分人数、5星占比等。
**希望用到的技能：**
- 爬虫基础知识
- BeautifulSoup的使用
- 多进程
- 操作数据库
- 使用队列
- 文件操作
- MATLAB画图统计，实现数据可视化
- 下载图片
- 正则表达式
- 使用代理池、防止封锁
- 克服反爬机制等
---
**我分析过了整个网站，大致分为以下几个步骤进行：**

1. 先获取250个电影的详情页的地址，保存为txt文件，并将其保存到队列中等待处理
2. 从队头开始爬取页面，保存为BeautifulSoup对象，同时队首出队。这里可能会遇到反爬机制
3. 处理BeautifulSoup对象，清洗数据，获得电影相关信息，以及其电影海报页面地址，其中会用到正则表达式，这里也可能会遇到反爬机制
4. 将清洗后的数据存入数据库
5. 下载相关电影海报图，并附上相关信息，将其存到一个文件夹下txt+pic
6. 利用MATLAB处理数据，输出统计图
2、3、5尝试使用多进程加快处理速度
---
**目前已经完成的步骤：1、2、5**
**正在进行的步骤：3**
**遇到的问题：多进程在win10上遇到了神奇的bug，还没解决、在清洗数据时遇到了一点小问题，是对BeautifulSoup掌握度不够的问题、基础不扎实。**

在写的时候我就注意了爬虫的礼仪，设定了访问间隔时间，并没有遇到封锁，很幸运。可以说豆瓣简直就是爬虫新手的乐园，难度不大、但有一定挑战性。

---
通过这次练习，我对自己的水平有了大致的了解，远远不够——**MATLAB不会使、代理IP不熟悉、多进程不会用、相关基础知识不深刻、数据结构使用不合理、代码结构不规范等很多问题。**

在写代码时，发现了很多问题，这都将是我接下来努力的方向！！
![目标](https://upload-images.jianshu.io/upload_images/15391438-534e456ccf8e21f7.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
---
**代码没写完，主程序没写，下周末更新！**
全部代码：
```
import time
import os
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.request import urlretrieve

#我用的自己写的队列，模块QUEUE使用不熟练
class LNode:
	def __init__(self,arg):
		self.data=arg
		self.next=None
class MyQueue:
	#模拟队列
	def __init__(self):
		#phead=LNode(None)
		self.data=None
		self.next=None
		self.front=self#指向队列首
		self.rear=self#指向队列尾
	#判断队列是否为空,如果为空返回True，否则返回false
	def isEmpty(self):
		return self.front==self.rear
	#返回队列的大小
	def size(self):
		p=self.front
		size=0
		while p.next!=self.rear.next:
			p=p.next
			size+=1
		return size
	#返回队列首元素
	def top(self):
		if not self.isEmpty():
			return self.front.next.data
		else:
			print("队列为空")
			return None
	#返回队列尾元素
	def bottom(self):
		if not self.isEmpty():
			return self.rear.data
		else:
			print("队列为空")
			return None
	#出队列
	def pop(self):
		if self.size()==1:
			data=self.front.next
			self.rear=self
			return data.data

		elif not self.isEmpty():
			data=self.front.next
			self.front.next=self.front.next.next
			print("出队列成功")
			return data.data
		else:
			print("队列已为空")
			return None
	#入队列
	def push(self,item):
		tmp=LNode(item)
		self.rear.next=tmp
		self.rear=self.rear.next
		print("入队列成功")
	#清空队列
	def destroy(self):
		self.next=None
		print("队列已清空")
	#打印队列
	def showQueue(self):
		if not self.isEmpty():
			p=self.front.next
			while p != self.rear.next:
				print(p.data)
				p=p.next
#获得10页包含250个简介的页面地址	
def get_ten_pageurl():
	array=[]
	for i in range(0,250,25):
		array.append("https://movie.douban.com/top250?start="+str(i)+"&filter=")
	return array

# 得到每一个电影的详情页地址		
def get_250movie_page_url(ten_pageurl,Directory):
	"""
	输入10页地址
	将top250 的电影首页地址保存下来，同时存到队列中和本地text
	"""
	if not os.path.exists(Directory):
		os.makedirs(Directory)
	url_queue=MyQueue()
	for page_url in ten_pageurl:
		try:
			html = urlopen(page_url)
			bsobj = BeautifulSoup(html, features="html.parser")
			# 得到当前页面上25个包含序号、详情页的地址的div标签，存为列表
			movie_info_items = bsobj.findAll("div", {"class": "pic"})
			for movie_info in movie_info_items:
				try:
					movie_id = int(movie_info.find("em").get_text())
					movie_info_url = movie_info.find("a").attrs["href"]
					movie_name=movie_info.find("img").attrs["alt"]
					url_queue.push(movie_info_url)
					with open(Directory + "/250homepage_url.txt", "a") as f:
						f.write(str(movie_id))
						f.write("\t")
						f.write(movie_name)
						f.write("\t")
						f.write(movie_info_url)
						f.write("\n")
					print("获取movie_id/movie_info_url成功：", movie_id)
				except:
					print("获取movie_id/movie_info_url失败：", movie_info[30:34])
					continue
			time.sleep(2)
		except:
			print("页面%s处理失败"%(page_url))
			time.sleep(1)
			continue
	return url_queue

#获取详情页
def get_movie_info(url):
	try:
		html = urlopen(url)
		bsobj = BeautifulSoup(html, features="html.parser")
		time.sleep(2)
		return bsobj
	except:
		print("页面%s处理失败"%(url[-8:]))
		time.sleep(1)
		return None
#处理详情页
def configure_infopage(bsobj):
	try:
		#电影排名：
		movie_id=bsobj.find("span", {"class": "top250-no"}).get_text()
		# 得到当前页面上的电影名称
		movie_name = bsobj.find("span", {"property": "v:itemreviewed"}).get_text()
		#电影简介
		movie_intro=bsobj.find("span",{"property":"v:summary"})
		#获取电影海报页面链接
		movie_photos=bsobj.find("a",{"class":"nbgnbg"}).attrs["href"]
		#电影详细信息左
		movie_info_items=bsobj.find("div",{"class":"subjectwrap clearfix"})
		#处理电影详细信息
		#导演: 弗兰克·德拉邦特
		movie_directer=movie_info_items.find("a",{"rel":"v:directedBy"}).get_text()
		#编剧: 弗兰克·德拉邦特 / 斯蒂芬·金
		movie_attrs=None
		#主演: 蒂姆·罗宾斯 / 摩根·弗里曼 / 鲍勃·冈顿 / 威廉姆·赛德勒 / 克兰西·布朗 / 吉尔·贝罗斯 / 马克·罗斯顿 / 詹姆斯·惠特摩 / 杰弗里·德曼 / 拉里·布兰登伯格 / 尼尔·吉恩托利 / 布赖恩·利比 / 大卫·普罗瓦尔 / 约瑟夫·劳格诺 / 祖德·塞克利拉 / 保罗·麦克兰尼 / 芮妮·布莱恩 / 阿方索·弗里曼 / V·J·福斯特 / 弗兰克·梅德拉诺 / 马克·迈尔斯 / 尼尔·萨默斯 / 耐德·巴拉米 / 布赖恩·戴拉特 / 唐·麦克马纳斯
		movie_actors=None
		#类型: 剧情 / 犯罪
		movie_genre=None
		#制片国家/地区: 美国
		movie_saition=movie_info_items.find("a",{"rel":"v:directedBy"}).get_text()
		#语言: 英语
		movie_language=None
		#上映日期: 1994-09-10(多伦多电影节) / 1994-10-14(美国)
		movie_initialReleaseDate=None
		#片长: 142分钟
		movie_Runtime=None
		#又名: 月黑高飞(港) / 刺激1995(台) / 地狱诺言 / 铁窗岁月 / 消香克的救赎
		movie_alias=None
		#IMDb链接: tt0111161
		movie_IMDb_url=None
		#电影评分信息
		movie_votes_info=bsobj.find("div",{"id":"interest_sectl"})
		#处理电影评分信息
		#评分
		movie_vote=None
		#评分人数
		movie_voters=None
		#5星数量
		movie_vote_5_stars=None
	except:
		print("电影信息处理失败")
		return None
	return [movie_id,movie_name,movie_vote,movie_voters,movie_vote_5_stars,movie_directer,movie_attrs,movie_actors,movie_genre,movie_saition,movie_language,\
			movie_initialReleaseDate,movie_Runtime,movie_alias,movie_IMDb_url,movie_intro,movie_photos]

# 下载海报
def download_img(url,download_directory):
	"""
	保存海报
	输入：下载文件地址，和板存路径
	输出：将文件保存到相应文件下
	"""
	if not os.path.exists(download_directory):
		os.makedirs(download_directory)
	file_path=download_directory+url[-14:]
	try:
		urlretrieve(url, file_path)
		print("1")
		print("下载图片：%s完成！\n存储在：%s" % (url[-14:],file_path))
		time.sleep(2)
	except :
		print("下载图片：%s失败！" % (url[-14:]))
		return None

```

---
今天的文比较长：加代码一共8296字，不算代码一共：3746.
阅读时间较长，内容仅做参考，
之前看了不少大厂对实习生的招聘要求，对python实习生的要求中都要求要有爬虫编写的经验，这两周的爬虫项目让我学到了很多，所以不论是为了入门，还是为了提高，写写小型的项目总是很有用的。
希望用到的技能：
- **爬虫基础知识**
- **BeautifulSoup的使用**
- 多进程
- **操作数据库**
- **使用队列**
- **文件操作**
- MATLAB画图统计，实现数据可视化
- **下载图片**
- **正则表达式**
- 使用代理池、防止封锁
 - 克服反爬机制等

在写爬虫之前我是希望用到这些知识的，有些我了解，有些没接触过，加粗的是这次用到的，下面来一步一步开始我们的爬虫，我会随时介绍我在编写的时候遇到的问题。
先来看下成果：
![image.png](https://upload-images.jianshu.io/upload_images/15391438-a9cfd1eeb77e70da.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
![image.png](https://upload-images.jianshu.io/upload_images/15391438-17498fdac14d980c.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
![image.png](https://upload-images.jianshu.io/upload_images/15391438-85110570173091b2.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
![image.png](https://upload-images.jianshu.io/upload_images/15391438-44e0c80807b76d92.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

还有数据库，我用的数据可视化工具Navicat：

![image.png](https://upload-images.jianshu.io/upload_images/15391438-08ad8e963ca3abf3.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
![image.png](https://upload-images.jianshu.io/upload_images/15391438-022b7fc1dfbeac56.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

很多爬虫教程都是在爬妹子图、美女图、啥啥图，这些对身体不好。不过我也帮室友爬过他们感兴趣的网站，就是那个解数学题的那个。我们正经一点！

首先豆瓣网站对与爬虫工程还是十分友好的，在写爬虫之前，我们先来看一下这个网站的robots.txt文件:https://movie.douban.com/robots.txt
```
User-agent: *
Disallow: /subject_search
Disallow: /amazon_search
Disallow: /search
Disallow: /group/search
Disallow: /event/search
Disallow: /celebrities/search
Disallow: /location/drama/search
Disallow: /forum/
Disallow: /new_subject
Disallow: /service/iframe
Disallow: /j/
Disallow: /link2/
Disallow: /recommend/
Disallow: /doubanapp/card
Sitemap: https://www.douban.com/sitemap_index.xml
Sitemap: https://www.douban.com/sitemap_updated_index.xml
# Crawl-delay: 5

User-agent: Wandoujia Spider
Disallow: /
```
从这份文件中，我们可以看到：User-agent: *，这是指的所有的爬虫，它下面的Disallow后面的所有的文件夹都不允许爬。# Crawl-delay: 5这是说的是爬虫的延时，不能太快，不然会增加豆瓣服务器的负担。我们为了学习当然是不会故意为难人家的服务器。
`User-agent: Wandoujia Spider`
`Disallow: /`这两句就有意思了，豌豆荚的爬虫是不允许爬所有的文件的。

**当然上面说的所有的规定都只是规定，你如果非要爬，那也不是做不到，但是没有必要。我们没必要跟别人作对，如果你真的爬到了什么不该知道的东西，那你可能就凉了。**爬虫礼仪还是很重要的！

所以我们先去看了我们需要的内容在哪个文件夹下：
250电影列表：`https://movie.douban.com/top250`——/top250/
电影详细信息：`https://movie.douban.com/subject/1292052/`——/subject/
电影海报：`https://movie.douban.com/photos/photo/480747492/`——/photos/

这三个目录在上面的robotsx.txt文件是没有禁止的，所以可以爬取，但是delay是要求5秒。
。。。。。。这有点长了，那理想情况：5*250=1250s,在加上30张海报，5*30*250=37500s,这得猴年马月？？所以我都设置为了1s，而且中间加上了一些BeautifulSoup的处理时间，差不多了。

robots.txt看完了，接下来就是应该分析我们需要哪些步骤来完成整个项目，说实话，这个项目不算大，但是也不小，算是目前我写过的最大的爬虫了。。。。

看一下首页：
![top250首页](https://upload-images.jianshu.io/upload_images/15391438-7b46cd9c223aaeb8.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
页面地址非常简单。这是第一页，每一部电影的排名，电影名称等信息都是以一个长方形的item展示在页面上

在首页的下面可以清楚的看到每一页25部电影，一共10页，一共250个items。非常规范，这对我们编写爬虫是非常有利的。
![第一页](https://upload-images.jianshu.io/upload_images/15391438-5288e96d9949f043.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)



每部电影的详情页的地址非常清晰，页面上的信息也非常丰富，基本上这一页能看到的东西，我都想拿下来。
![详情页](https://upload-images.jianshu.io/upload_images/15391438-9ee8f5f3f775cd05.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

再来看一下海报的地址，浏览器直接点击电影封面就行：
![海报](https://upload-images.jianshu.io/upload_images/15391438-00fd4969b62bbbf1.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
可以发现一部的电影的照片还是不少的，No.1就有535张，全部爬下来都行，但是没有必要，所以我们就取30张海报就行。

####好了，我们在浏览器里用眼睛看到了我们想要的东西，电影信息，电影海报，这是我们需要的。
网站的结构是这样的

>排行榜——10页
>>详情页面——一页
>>>海报页面——有多页（只取30张）

所以根据网页结构，以及我们需要的数据内容，可以将获取信息的步骤分为：
####步骤：
1. 爬取10页排行榜地址
2. 爬取所有250部电影详情页地址
3. 处理每一部电影
3.1  爬取详情页
3.1  清洗数据
3.2  存储数据
3.3  爬取电影海报页面的30张海报的地址
3.4 下载海报

函数式编程：
大概的步骤是这样的，因此我们就可以先写出main函数：
```
def main():
	#1. 爬取10页排行榜地址
	ten_url=get_ten_page_url()
	#2. 爬取所有250部电影详情页地址
	movie250infos_url=get_250movie_info_url(ten_url)
	#3. 处理每一部电影
	for i in movie250infos_url:
		#3.1  爬取详情页
		info=get_info(i)
		#3.1  清洗数据
		info=configue_info(info)
		#3.2  存储数据
		save_info(info)
		#3.3  爬取电影海报页面的30张海报的地址
		img=get_img(info)
		#3.4 下载海报
		save_img(img)
```

接下来只要完成每一个函数的功能即可：
###1. 爬取10页排行榜地址
有10页，所以现在来看一下下一页的地址是怎样的：
![image.png](https://upload-images.jianshu.io/upload_images/15391438-82562212d7b70b88.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
可以看出，`https://movie.douban.com/top250?start=25&filter=`
这地址还是非常清楚的，start=25，filter=。这意思就是是从第25号开始，过滤器值为空。
这里就有问题了，那第一页的地址和第二页的地址结构是不一样的，而且明明第一页有25部电影，他为什么是start=25？？，这对学编程的人来说，显而易见，我们数数是从0开始的，第一部0，第二部是1，第三部是2....,以此类推，所以我带着好奇心试了这个地址：https://movie.douban.com/top250?start=0&filter=

![image.png](https://upload-images.jianshu.io/upload_images/15391438-5b82038fddbbe07a.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
哈哈。跟之前的/top250/显示的是一样的。那么filter=是什么意思呢？
可以看到第一部电影的item的右上角，有一个我没看过的选项，这应该就是需要过滤的东西，但是这里对我们没有影响，所以我们可以很容易的得到全部10页排行榜的地址：
```
#获得10页包含250个简介的页面地址	
def get_ten_pageurl():
	#array=["https://movie.douban.com/top250?start=0&filter="]
	array=[]
	for i in range(0,250,25):
		array.append("https://movie.douban.com/top250?start="+str(i)+"&filter=")
	return array
```
这里可以发现，`#array=["https://movie.douban.com/top250?start=0&filter="]`这一句是我用来测试代码用的。因为，一共10页，你在后面试运行时，不可能每次都从头开始，这样会浪费很多时间。你可以像我一样，将一些需要循环的处理的列表设置成只有一个值，这样就不会等到先处理完10页链接，在执行你需要的地方。这是一个调试的好方法，但是在最后的时候，你要把他注释掉，别忘记了。

这里我们是非常幸运的，并没有遇到用ajax来换页的情况，在之前我爬取拉勾网时，就遇到了，下一页的地址和上一页的地址是一样的，他是通过ajax动态交互技术实现的，所以获取下一页的地址就成了问题。当然解决它也是很容易的，等下次写爬虫我在详细介绍ajax页面的爬取。

###2. 爬取所有250部电影详情页地址
前面的10页的地址的获取不算是爬虫，只能算是一个简单的for循环。下面我们来看一看如何爬取250部电影的详情页地址：
先来看一看网页的代码，分析下结构，打开我们要爬取的页面按F12，或者直接在items上右键->检查元素：
![image.png](https://upload-images.jianshu.io/upload_images/15391438-4fb986a297cc8cd3.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
就会出现下面的情况：
![image.png](https://upload-images.jianshu.io/upload_images/15391438-86a6bc8638864e10.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
可以看到直接找到了我们需要的地址。
当然，如果你按的F12，出来的不是这样的，你需要点击元素
然后点击这个![image.png](https://upload-images.jianshu.io/upload_images/15391438-a7c3a1deb5d99574.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

然后将鼠标移到电影信息上，单击。就会出来一样的东西。

然后我们来看一下我们需要的详情页的地址在哪个位置：
![image.png](https://upload-images.jianshu.io/upload_images/15391438-4d2e1e9422b98c81.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

可以看出，整个页面是用
```
<ol>
<li><\li>
<li><\li>
<li><\li>
<li><\li>
<li><\li>
<\ol>
```
这样的结构，每一个<li>标签里包含一个div标签，里面又有pic和info两个标签
![image.png](https://upload-images.jianshu.io/upload_images/15391438-bf209266e8e5f489.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

展开里面的全部标签，可以看出这里包含了我们需要的大部分信息，但是还不够，我们需要像详情页里那样详细的信息，不过，这里的信息我们页可以保存一部分。这里我只拿了排名、电影名、电影详情页地址，这三个信息。观察html文件可以发现，这三个信息都在class="pic"的a标签里，所以只要取这一小段就行，然后获取信息就行。利用BeautifulSoup将页面上的25部电影的信息筛选出来，然后for循环处理，提取信息保存。
```
# 得到每一个电影的详情页地址		
def get_250movie_page_url(ten_pageurl,Directory):
	"""
	输入10页地址
	将top250 的电影首页地址保存下来，同时存到队列中和本地text
	"""
	if not os.path.exists(Directory):
		os.makedirs(Directory)
	url_queue=MyQueue()
	conn = mysql.connector.connect(user='root', password='password', database='douban250')
	cursor = conn.cursor()
	conn.commit()
	for page_url in ten_pageurl:
		try:
			html = urlopen(page_url)
			bsobj = BeautifulSoup(html, features="html.parser")
			# 得到当前页面上25个包含序号、详情页的地址的div标签，存为列表
			movie_info_items = bsobj.findAll("div", {"class": "pic"})
			for movie_info in movie_info_items:
				try:
					movie_id = int(movie_info.find("em").get_text())
					movie_info_url = movie_info.find("a").attrs["href"]
					movie_name=movie_info.find("img").attrs["alt"]
					url_queue.push(movie_info_url)

					with open(Directory + "/250homepage_url.txt", "a") as f:
						f.write(str(movie_id))
						f.write("\t")
						f.write(movie_name)
						f.write("\t")
						f.write(movie_info_url)
						f.write("\n")
					print("获取movie%s详情页url成功"%(movie_id))
					cursor.execute('insert into movie_250url '
					               '(id, name,url) '
					               'values (%s, %s,%s)',
					               [movie_id, movie_name, movie_info_url])
					conn.commit()
				except:
					print("获取movie详情页url失败！")
					#continue
			time.sleep(2)
		except:
			print("页面%s处理失败"%(page_url))
			time.sleep(1)
			continue
	cursor.close()
	return url_queue
```
可以发现这个函数很长，因为这里包含了很多操作。这里我将250个信息存在了队列里，因为，我不打算使用多线程了。存在队列里，队列先进先出，没毛病。然后用了os新建文件夹。用了数据库，将排名、电影名、地址存为一张数据表。用了txt文件读写，将这些信息保存在了txt文本中。用了try。。。except。。。语句错误调试，以防突发问题，从而不影响整个程序。用了time模块，爬虫间隔2s。最后返回一个队列。

可以发现我用的是urllib的urlopen，而不是requests的get。这个问题以及BeautifulSoup的使用我以后会单独拿出来写。
###3. 处理每一部电影
得到了250个页面的地址，都存在队列里。接下来处理他们。
####3.1 爬取详情页
我直接将队列的头元素传入函数，获取页面，并新建为一个BeautifulSoup对象返回
```
#获取详情页
def get_movie_info(url):
	try:
		html = urlopen(url)
		bsobj = BeautifulSoup(html, features="html.parser")
		print("获取详情页面成功",url[-8:])
		time.sleep(1)
		return bsobj
	except:
		print("详情页面%s获取失败"%(url[-8:]))
		time.sleep(1)
		return None
```
`bsobj = BeautifulSoup(html, features="html.parser")`这我现在还不太清楚，这是运行时加的——features="html.parser"，没细看。但是不加会给个警告warning。

####3.1 清洗数据
得到了bs对象，接下来就是处理他了。
详情页的结构比前面的250电影的结构要复杂很多，这里花了我不少时间，到现在还有三个没有解决：制片国家、语言、电影别名。这三个的html的结构有点奇怪。而且BeautifulSoup处理信息的速度并不快，所以就没管它了，等下次将BeautifulSoup、xpath等工具时在来处理这个问题，这里我将他们作为一个列表反回了，方便后面的处理。
```
#处理详情页
def configure_infopage(bsobj):
	try:
		#电影排名：
		movie_id=bsobj.find("span", {"class": "top250-no"}).get_text()
		# 得到当前页面上的电影名称
		movie_name = bsobj.find("span", {"property": "v:itemreviewed"}).get_text()
		#电影简介
		movie_intro=bsobj.find("span",{"property":"v:summary"}).get_text().replace("\n                                    \u3000\u3000","").replace("                                　　","")
		#获取电影海报页面链接
		movie_photos=bsobj.find("a",{"class":"nbgnbg"}).attrs["href"]
		#电影详细信息左
		movie_info_items=bsobj.find("div",{"id":"info"})
		#处理电影详细信息
		#导演: 弗兰克·德拉邦特
		movie_directer = movie_info_items.find("a", {"rel": "v:directedBy"}).get_text()
		#编剧: 弗兰克·德拉邦特 / 斯蒂芬·金
		movie_attrs =movie_info_items.find_all("a",{"href":re.compile("/celebrity"),})[0].get_text()+"|"+ \
		             movie_info_items.find_all("a", {"href": re.compile("/celebrity"), })[1].get_text()
		#主演: 蒂姆·罗宾斯 / 摩根·弗里曼 / 鲍勃·冈顿 / 威廉姆·赛德勒 / 克兰西·布朗 / 吉尔·贝罗斯 / 马克·罗斯顿 / 詹姆斯·惠特摩 / 杰弗里·德曼 / 拉里·布兰登伯格 / 尼尔·吉恩托利 / 布赖恩·利比 / 大卫·普罗瓦尔 / 约瑟夫·劳格诺 / 祖德·塞克利拉 / 保罗·麦克兰尼 / 芮妮·布莱恩 / 阿方索·弗里曼 / V·J·福斯特 / 弗兰克·梅德拉诺 / 马克·迈尔斯 / 尼尔·萨默斯 / 耐德·巴拉米 / 布赖恩·戴拉特 / 唐·麦克马纳斯
		# 取前3
		movie_actors=""
		for i in movie_info_items.find_all("a",{"rel":"v:starring"})[:5]:
			movie_actors=movie_actors+i.get_text()
		#类型: 剧情 / 犯罪
		movie_genre=movie_info_items.find_all("span",{"property":"v:genre"})[0].get_text()+"|"+ \
		            movie_info_items.find_all("span", {"property": "v:genre"})[1].get_text()
		#制片国家/地区: 美国
		movie_saition=None
		#语言: 英语
		movie_language=None
		#上映日期: 1994-09-10(多伦多电影节) / 1994-10-14(美国)
		movie_initialReleaseDate =""
		for i in movie_info_items.find_all("span", {"property": "v:initialReleaseDate"}):
			movie_initialReleaseDate=movie_initialReleaseDate+i.get_text()
		#片长: 142分钟
		movie_Runtime=movie_info_items.find("span",{"property":"v:runtime"}).get_text()
		#又名: 月黑高飞(港) / 刺激1995(台) / 地狱诺言 / 铁窗岁月 / 消香克的救赎
		movie_alias=None
		#IMDb链接: tt0111161
		movie_IMDb_url=movie_info_items.find("a",{"rel":"nofollow"}).attrs["href"]
		#电影评分信息
		movie_votes_info=bsobj.find("div",{"id":"interest_sectl"})
		#处理电影评分信息
		#评分
		movie_vote=movie_votes_info.find("strong",{"class":"ll rating_num"}).get_text()
		#评分人数
		movie_voters=movie_votes_info.find("span",{"span":"v:votes"})
		#5星数量
		movie_vote_5_stars=movie_votes_info.find_all("span",{"class":"rating_per"})[0].get_text()
		print("正在解析电影信息",movie_id)
	except:
		print("电影信息解析失败")
		return None
	return [movie_id,
	        movie_name,
	        movie_vote,
	        movie_voters,
	        movie_vote_5_stars,
	        movie_directer,
	        movie_attrs,
	        movie_actors,
	        movie_genre,
	        movie_saition,
	        movie_language,
	        movie_initialReleaseDate,
	        movie_Runtime,
	        movie_alias,
	        movie_IMDb_url,
	        movie_intro,
		    movie_photos]
```

####3.2 存储数据
```
#存储信息
def save_infos(infos,Directory):
	filepath = Directory + "/info/"
	if not os.path.exists(filepath):
		os.makedirs(filepath)
	conn = mysql.connector.connect(user='root', password='password', database='douban250')
	cursor = conn.cursor()
	print("-"*20)
	print("正在将movie%s信息存到数据库。。。。"%(infos[0]))
	cursor.execute('insert into movie_250_info \
	               (\
	               movie_id,\
	               movie_name,\
	               movie_vote,\
	               movie_voters,\
	               movie_vote_5_stars,\
	               movie_directer,\
	               movie_attrs,\
	               movie_actors,\
	               movie_genre,\
	               movie_saition,\
	               movie_language,\
	               movie_initialReleaseDate,\
	               movie_Runtime,\
	               movie_alias,\
	               movie_IMDb_url,\
	               movie_intro,\
	               movie_photos\
	               ) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', infos)
	conn.commit()
	conn.close()
	print("正在将文件存储为txt。。。。。")
	with open(filepath+ infos[0][3:] + ".txt", "a") as fi:
		for i in infos:
			if type(i) == list:
				for x in i:
					fi.write(x)
					fi.write("\t")
				continue
			fi.write(i if i is not None else "None")
			fi.write("\n")
	print("存储完成！")
	print("-" * 20)
```
在这一步，数据库的插入工作也废了不少时间，首先这是我第一次使用数据库，对于数据库的设计还一知半解，这也放之后单讲，今天上午我在写关于数据库的文了。应该很快了。这里我也存了一份文件作为参考。

####3.3 爬取电影海报页面的30张海报的地址
可以看到，我将电影的海报地址作为列表的最后一项。这是只要用[-1]就能取到这个值。
```
# 获取海报页面前30张图片的地址
def get_img_url(movie_url):
	html=urlopen(movie_url)
	bsobj=BeautifulSoup(html, features="html.parser")
	img_url=bsobj.find_all("div",{"class":"cover"})
	l=[]
	for i in img_url:
		url=i.find("img").attrs["src"]
		l.append(url)
	#print("-"*20)
	print("30张海报地址获取成功！")
	return l
```
####3.4下载海报
下载就很简单了，我没有用requests的保存二进制文件来保存文件，用的是urllib.urlretrieve,这个很好用。
```
#下载图片
def save_img(infos,Directory):
	img = get_img_url(infos[-1])
	filepath=Directory + "/pic/" + infos[0] + "/"
	print("-" * 20)
	print("海报储存在",filepath)
	#print("-" * 20)
	#print("\n")
	for i in img:
		download_img(i, filepath)
	print("海报30张下载成功")
	print("-" * 20)
# 下载海报
def download_img(url,download_directory):
	"""
	保存海报
	输入：下载文件地址，和板存路径
	输出：将文件保存到相应文件下
	"""
	if not os.path.exists(download_directory):
		os.makedirs(download_directory)
	file_path=download_directory+url[-14:]
	try:
		urlretrieve(url, file_path)
		#print("1")
		print("下载图片：%s完成！" % (url[-14:]))
		time.sleep(1)
	except :
		print("下载图片：%s失败！" % (url[-14:]))
		return None
```
我把他们分开写成了两个函数。我的老师跟我说，一个函数不应该很长。这次写爬虫中并没有注意这个问题，下次一定注意。而且我函数的分工还是有些冗余，不明确。这是一个缺点。

按照我们前面的分析，到这里就结束了。但是开头的main函数是我刚写的，之前并没这么想。
我的main函数：
```
def main():
	Directory = "C:/Users/葛苏健/Desktop/py/python小案例/004爬取豆瓣新片"
	print("正在获取10页目录。。。。。")
	ten_pageUrl = get_ten_pageurl()
	print("正在连接数据库。。。。。")
	conn = mysql.connector.connect(user='root', password='password', database='douban250')
	cursor = conn.cursor()
	cursor.execute('create table movie_250url '
	               '(id int primary key, '
	               'name varchar(20), '
	               'url char(50))')
	cursor.execute('create table movie_250_info (\
						movie_id char(10) primary key,\
						movie_name text,\
						movie_vote char(20),\
		                movie_voters char(20),\
		                movie_vote_5_stars char(20),\
		               movie_directer text,\
		               movie_attrs text,\
		               movie_actors text,\
		               movie_genre text,\
		               movie_saition text NULL,\
		               movie_language text NULL,\
		               movie_initialReleaseDate text,\
		               movie_Runtime text,\
		               movie_alias text NULL,\
		               movie_IMDb_url text,\
		               movie_intro text,\
		               movie_photos text\
		               )')
	conn.commit()
	time.sleep(1)
	print("连接成功！")
	print("正在获取250个电影的详情页url。。。。")
	movieInfoPage_queue = get_250movie_page_url(ten_pageUrl, Directory)
	print("获取250个电影的详情页url成功！")
	time.sleep(1)
	# movieInfoPage_queue =MyQueue()
	# movieInfoPage_queue.destroy()
	# movieInfoPage_queue.push("https://movie.douban.com/subject/1291546/")
	# # #info_path = Directory + "/info.txt"
	print("正在创建文件夹")
	if not os.path.exists(Directory):
		os.makedirs(Directory)
		print("创建成功")
	print("开始爬取top250电影：")
	print("#"*50)
	while not movieInfoPage_queue.isEmpty():
		try:
			print("=" * 50)
			print("正在获取页面。。。")
			info = get_movie_info(movieInfoPage_queue.top())
			movieInfoPage_queue.pop()
			print("开始解析电影详情页。。。")
			infos = configure_infopage(info)
			print("解析电影详情页成功！")
			save_infos(infos,Directory)
			print("开始下载海报：")
			save_img(infos,Directory)
			print("海报下载完成\n")
			print("电影%s爬取成功！"%(infos[0]))
			print("=" * 50)
			print("\n")
		except:
			#print("=" * 50)
			print("失败！")
			print("=" * 50)
			print("\n")
			continue

```

....废话非常多，是因为我想了解爬虫每时每刻都在做什么。
###下面来总结下：
这次爬虫用到了beautifulsoup、os、re、time、urllib.urlopen、mysql.connector、urllib.urlretrieve这里个库，高级的技术也没用到。
这次学会的：数据库交互。。。其他的都只是巩固，而且这次的数据库操作也不是很复杂，数据可视化还没有完成，代理、反爬都没遇到过。。。。

但是我还是巩固了基础，对爬虫的整体架构有了更深入的理解。之后我会单独将这次用到的技术拿出来写，以此来巩固。

那再来说说这次的不足：
代码冗余，不够精简、层次不清晰、写代码前的准备不够充分、函数式编程设计模式不熟悉，没有章法。我应该去看看设计模式方面的东西——spring MVC啥的。
同时这次的爬虫速度慢、空间使用量大。我昨晚上仔细看了看python的垃圾回收机制，收获不少——引用计数、代回收Generational GC，前者用于大多数情况，后专为循环引用设计，详细见[python垃圾回收](https://www.jianshu.com/p/4b1c11a15494
)
写的很好。这次的爬虫还是有点问题，250部爬下来160部，剩下的都是因为处理信息时以及电脑自身问题，爬虫是在昨天运行的，写完文章后便没理它，一直运行，结果电脑频繁睡眠，电脑的wifi一直断，还好设置了等待，不然直接出错就全凉了，后来在我自己监督下还是断了几次，所以只爬了一半多，当然我觉得大部分还是代码的问题，存数据库，数据清洗的地方有问题，因为每部电影的详情页上的信息不一样，我只参照了几个，剩下的就是格式问题，因为时间问题，仅做学习用，也就没去找那几页的差距。

好的就这样，下周末继续，下面的代码，库安装完成后可以直接运行。
---
全部代码：
```
# 爬取要求：
# 目标豆瓣top250
# 结果：电影名，排名，导演，主演，评分，年代，分类，多少人评价，一句概括，电影海报。
# 用数据库储存
# 知识点：
# 爬虫基础
# 数据库
# 用队列存储未完成的标题
# 可以考虑多进程
import time
import os
import re
import mysql.connector
#考虑使用xpath
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.request import urlretrieve

#我用的自己写的队列，模块QUEUE使用不熟练
class LNode:
	def __init__(self,arg):
		self.data=arg
		self.next=None

class MyQueue:
	#模拟队列
	def __init__(self):
		#phead=LNode(None)
		self.data=None
		self.next=None
		self.front=self#指向队列首
		self.rear=self#指向队列尾
	#判断队列是否为空,如果为空返回True，否则返回false
	def isEmpty(self):
		return self.front==self.rear
	#返回队列的大小
	def size(self):
		p=self.front
		size=0
		while p.next!=self.rear.next:
			p=p.next
			size+=1
		return size
	#返回队列首元素
	def top(self):
		if not self.isEmpty():
			return self.front.next.data
		else:
			#print("队列为空")
			return None
	#返回队列尾元素
	def bottom(self):
		if not self.isEmpty():
			return self.rear.data
		else:
			#print("队列为空")
			return None
	#出队列
	def pop(self):
		if self.size()==1:
			data=self.front.next
			self.rear=self
			return data.data

		elif not self.isEmpty():
			data=self.front.next
			self.front.next=self.front.next.next
			#print("出队列成功")
			return data.data
		else:
			#print("队列已为空")
			return None
	#入队列
	def push(self,item):
		tmp=LNode(item)
		self.rear.next=tmp
		self.rear=self.rear.next
		#print("入队列成功")
	#清空队列
	def destroy(self):
		self.next=None
		#print("队列已清空")
	#打印队列
	def showQueue(self):
		if not self.isEmpty():
			p=self.front.next
			while p != self.rear.next:
				print(p.data)
				p=p.next

#获得10页包含250个简介的页面地址	
def get_ten_pageurl():
	#array=["https://movie.douban.com/top250?start=0&filter="]
	array=[]
	for i in range(0,250,25):
		array.append("https://movie.douban.com/top250?start="+str(i)+"&filter=")
	return array

# 得到每一个电影的详情页地址		
def get_250movie_page_url(ten_pageurl,Directory):
	"""
	输入10页地址
	将top250 的电影首页地址保存下来，同时存到队列中和本地text
	"""
	if not os.path.exists(Directory):
		os.makedirs(Directory)
	url_queue=MyQueue()
	conn = mysql.connector.connect(user='root', password='password', database='douban250')
	cursor = conn.cursor()
	conn.commit()
	for page_url in ten_pageurl:
		try:
			html = urlopen(page_url)
			bsobj = BeautifulSoup(html, features="html.parser")
			# 得到当前页面上25个包含序号、详情页的地址的div标签，存为列表
			movie_info_items = bsobj.findAll("div", {"class": "pic"})
			for movie_info in movie_info_items:
				try:
					movie_id = int(movie_info.find("em").get_text())
					movie_info_url = movie_info.find("a").attrs["href"]
					movie_name=movie_info.find("img").attrs["alt"]
					url_queue.push(movie_info_url)

					with open(Directory + "/250homepage_url.txt", "a") as f:
						f.write(str(movie_id))
						f.write("\t")
						f.write(movie_name)
						f.write("\t")
						f.write(movie_info_url)
						f.write("\n")
					print("获取movie%s详情页url成功"%(movie_id))
					cursor.execute('insert into movie_250url '
					               '(id, name,url) '
					               'values (%s, %s,%s)',
					               [movie_id, movie_name, movie_info_url])
					conn.commit()
				except:
					print("获取movie详情页url失败！")
					#continue
			time.sleep(2)
		except:
			print("页面%s处理失败"%(page_url))
			time.sleep(1)
			continue
	cursor.close()
	return url_queue

#获取详情页
def get_movie_info(url):
	try:
		html = urlopen(url)
		bsobj = BeautifulSoup(html, features="html.parser")
		print("获取详情页面成功",url[-8:])
		time.sleep(1)
		return bsobj
	except:
		print("详情页面%s获取失败"%(url[-8:]))
		time.sleep(1)
		return None

#处理详情页
def configure_infopage(bsobj):
	try:
		#电影排名：
		movie_id=bsobj.find("span", {"class": "top250-no"}).get_text()
		# 得到当前页面上的电影名称
		movie_name = bsobj.find("span", {"property": "v:itemreviewed"}).get_text()
		#电影简介
		movie_intro=bsobj.find("span",{"property":"v:summary"}).get_text().replace("\n                                    \u3000\u3000","").replace("                                　　","")
		#获取电影海报页面链接
		movie_photos=bsobj.find("a",{"class":"nbgnbg"}).attrs["href"]
		#电影详细信息左
		movie_info_items=bsobj.find("div",{"id":"info"})
		#处理电影详细信息
		#导演: 弗兰克·德拉邦特
		movie_directer = movie_info_items.find("a", {"rel": "v:directedBy"}).get_text()
		#编剧: 弗兰克·德拉邦特 / 斯蒂芬·金
		movie_attrs =movie_info_items.find_all("a",{"href":re.compile("/celebrity"),})[0].get_text()+"|"+ \
		             movie_info_items.find_all("a", {"href": re.compile("/celebrity"), })[1].get_text()
		#主演: 蒂姆·罗宾斯 / 摩根·弗里曼 / 鲍勃·冈顿 / 威廉姆·赛德勒 / 克兰西·布朗 / 吉尔·贝罗斯 / 马克·罗斯顿 / 詹姆斯·惠特摩 / 杰弗里·德曼 / 拉里·布兰登伯格 / 尼尔·吉恩托利 / 布赖恩·利比 / 大卫·普罗瓦尔 / 约瑟夫·劳格诺 / 祖德·塞克利拉 / 保罗·麦克兰尼 / 芮妮·布莱恩 / 阿方索·弗里曼 / V·J·福斯特 / 弗兰克·梅德拉诺 / 马克·迈尔斯 / 尼尔·萨默斯 / 耐德·巴拉米 / 布赖恩·戴拉特 / 唐·麦克马纳斯
		# 取前3
		movie_actors=""
		for i in movie_info_items.find_all("a",{"rel":"v:starring"})[:5]:
			movie_actors=movie_actors+i.get_text()
		#类型: 剧情 / 犯罪
		movie_genre=movie_info_items.find_all("span",{"property":"v:genre"})[0].get_text()+"|"+ \
		            movie_info_items.find_all("span", {"property": "v:genre"})[1].get_text()
		#制片国家/地区: 美国
		movie_saition=None
		#语言: 英语
		movie_language=None
		#上映日期: 1994-09-10(多伦多电影节) / 1994-10-14(美国)
		movie_initialReleaseDate =""
		for i in movie_info_items.find_all("span", {"property": "v:initialReleaseDate"}):
			movie_initialReleaseDate=movie_initialReleaseDate+i.get_text()
		#片长: 142分钟
		movie_Runtime=movie_info_items.find("span",{"property":"v:runtime"}).get_text()
		#又名: 月黑高飞(港) / 刺激1995(台) / 地狱诺言 / 铁窗岁月 / 消香克的救赎
		movie_alias=None
		#IMDb链接: tt0111161
		movie_IMDb_url=movie_info_items.find("a",{"rel":"nofollow"}).attrs["href"]
		#电影评分信息
		movie_votes_info=bsobj.find("div",{"id":"interest_sectl"})
		#处理电影评分信息
		#评分
		movie_vote=movie_votes_info.find("strong",{"class":"ll rating_num"}).get_text()
		#评分人数
		movie_voters=movie_votes_info.find("span",{"span":"v:votes"})
		#5星数量
		movie_vote_5_stars=movie_votes_info.find_all("span",{"class":"rating_per"})[0].get_text()
		print("正在解析电影信息",movie_id)
	except:
		print("电影信息解析失败")
		return None
	return [movie_id,
	        movie_name,
	        movie_vote,
	        movie_voters,
	        movie_vote_5_stars,
	        movie_directer,
	        movie_attrs,
	        movie_actors,
	        movie_genre,
	        movie_saition,
	        movie_language,
	        movie_initialReleaseDate,
	        movie_Runtime,
	        movie_alias,
	        movie_IMDb_url,
	        movie_intro,
		    movie_photos]

# 获取海报页面前30张图片的地址
def get_img_url(movie_url):
	html=urlopen(movie_url)
	bsobj=BeautifulSoup(html, features="html.parser")
	img_url=bsobj.find_all("div",{"class":"cover"})
	l=[]
	for i in img_url:
		url=i.find("img").attrs["src"]
		l.append(url)
	#print("-"*20)
	print("30张海报地址获取成功！")
	return l

# 下载海报
def download_img(url,download_directory):
	"""
	保存海报
	输入：下载文件地址，和板存路径
	输出：将文件保存到相应文件下
	"""
	if not os.path.exists(download_directory):
		os.makedirs(download_directory)
	file_path=download_directory+url[-14:]
	try:
		urlretrieve(url, file_path)
		#print("1")
		print("下载图片：%s完成！" % (url[-14:]))
		time.sleep(1)
	except :
		print("下载图片：%s失败！" % (url[-14:]))
		return None

#处理信息
def save_infos(infos,Directory):
	filepath = Directory + "/info/"
	if not os.path.exists(filepath):
		os.makedirs(filepath)
	conn = mysql.connector.connect(user='root', password='password', database='douban250')
	cursor = conn.cursor()
	print("-"*20)
	print("正在将movie%s信息存到数据库。。。。"%(infos[0]))
	cursor.execute('insert into movie_250_info \
	               (\
	               movie_id,\
	               movie_name,\
	               movie_vote,\
	               movie_voters,\
	               movie_vote_5_stars,\
	               movie_directer,\
	               movie_attrs,\
	               movie_actors,\
	               movie_genre,\
	               movie_saition,\
	               movie_language,\
	               movie_initialReleaseDate,\
	               movie_Runtime,\
	               movie_alias,\
	               movie_IMDb_url,\
	               movie_intro,\
	               movie_photos\
	               ) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', infos)
	conn.commit()
	conn.close()
	print("正在将文件存储为txt。。。。。")
	with open(filepath+ infos[0][3:] + ".txt", "a") as fi:
		for i in infos:
			if type(i) == list:
				for x in i:
					fi.write(x)
					fi.write("\t")
				continue
			fi.write(i if i is not None else "None")
			fi.write("\n")
	print("存储完成！")
	print("-" * 20)

#下载图片
def save_img(infos,Directory):
	img = get_img_url(infos[-1])
	filepath=Directory + "/pic/" + infos[0] + "/"
	print("-" * 20)
	print("海报储存在",filepath)
	#print("-" * 20)
	#print("\n")
	for i in img:
		download_img(i, filepath)
	print("海报30张下载成功")
	print("-" * 20)

def main():
	Directory = "C:/Users/葛苏健/Desktop/py/python小案例/004爬取豆瓣新片"
	print("正在获取10页目录。。。。。")
	ten_pageUrl = get_ten_pageurl()
	print("正在连接数据库。。。。。")
	conn = mysql.connector.connect(user='root', password='password', database='douban250')
	cursor = conn.cursor()
	cursor.execute('create table movie_250url '
	               '(id int primary key, '
	               'name varchar(20), '
	               'url char(50))')
	cursor.execute('create table movie_250_info (\
						movie_id char(10) primary key,\
						movie_name text,\
						movie_vote char(20),\
		                movie_voters char(20),\
		                movie_vote_5_stars char(20),\
		               movie_directer text,\
		               movie_attrs text,\
		               movie_actors text,\
		               movie_genre text,\
		               movie_saition text NULL,\
		               movie_language text NULL,\
		               movie_initialReleaseDate text,\
		               movie_Runtime text,\
		               movie_alias text NULL,\
		               movie_IMDb_url text,\
		               movie_intro text,\
		               movie_photos text\
		               )')
	conn.commit()
	time.sleep(1)
	print("连接成功！")
	print("正在获取250个电影的详情页url。。。。")
	movieInfoPage_queue = get_250movie_page_url(ten_pageUrl, Directory)
	print("获取250个电影的详情页url成功！")
	time.sleep(1)
	# movieInfoPage_queue =MyQueue()
	# movieInfoPage_queue.destroy()
	# movieInfoPage_queue.push("https://movie.douban.com/subject/1291546/")
	# # #info_path = Directory + "/info.txt"
	print("正在创建文件夹")
	if not os.path.exists(Directory):
		os.makedirs(Directory)
		print("创建成功")
	print("开始爬取top250电影：")
	print("#"*50)
	while not movieInfoPage_queue.isEmpty():
		try:
			print("=" * 50)
			print("正在获取页面。。。")
			info = get_movie_info(movieInfoPage_queue.top())
			movieInfoPage_queue.pop()
			print("开始解析电影详情页。。。")
			infos = configure_infopage(info)
			print("解析电影详情页成功！")
			save_infos(infos,Directory)
			print("开始下载海报：")
			save_img(infos,Directory)
			print("海报下载完成\n")
			print("电影%s爬取成功！"%(infos[0]))
			print("=" * 50)
			print("\n")
		except:
			#print("=" * 50)
			print("失败！")
			print("=" * 50)
			print("\n")
			continue

if __name__ == '__main__':
	main()

```

可以做做修改，提高效率，然后将存数据库和提取信息的地方的容错率提高一点，这样每一页就都能保存下来了。下周寻个有点难度但是内容不要太多。

加油！最近在复习计算机网络——tcp/ip——应用层->运输层->网络层->数据链路层->物理层，这里的应用层和运输层之间还是不太理解。
。。。。。
2019年3月17日17:04:44
