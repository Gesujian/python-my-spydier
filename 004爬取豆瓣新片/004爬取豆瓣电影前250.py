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
import MySQLdb
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


