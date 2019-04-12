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


