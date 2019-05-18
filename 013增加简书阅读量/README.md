这其实挺无聊的
>本文纯粹为了测试，不为获取任何收益。

###这程序不会有任何输出，程序只是增加本文的阅读量！

###同时希望简友不要滥用！
---
正文：

今天在知乎热榜上看到这么个问题：

![...](https://upload-images.jianshu.io/upload_images/15391438-3632efd5fb5bc20c.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

我觉得很有意思，下面的很多回答都说的不可以，我看了看说的都很有道理，网站的seo优化是专门的一个领域，不是说提高排名就能够做到的。当然都说量变引起质变，我很想试试。

**实践是检验真理的唯一标准。**

我打算写个程序，自动化访问**这一篇文章**，在我发布完这一篇文章后，我就会运行程序，自动访问1000次，看看能有什么效果。

这效果我不清楚，如果给官方给封了，那我之后再补上，但是不运行就是了。

如果程序成功，则这一篇的阅读量将到达1k+，真是期待呢，简书的简书钻是文章曝光率的一个影响因素，但是这阅读量不知道有什么用。

我不知道有没有人这么做过。我就来做第一个吃螃蟹的人吧！如果官方发现这个问题，认为我这是在作弊，我希望能够改进这一点。如果没有关系，请放过我！。。。。。。

我是利用的selenium+chrome，来实现自动化访问的，程序很短。非常简单。
因为我需要得到文章的链接地址，得先发布之后才能更新文章，在运行程序。
```
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

for x in range(1000):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    browser_s = webdriver.Chrome(chrome_options=chrome_options)
    wait = WebDriverWait(browser_s, 10)
    browser_s.get(url='https://www.jianshu.com/p/530dfe917afb')# 本文地址
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body > div.note > div.post > div.meta-bottom > div.like > div > div.btn-like > a')))
    browser_s.quit()
```

