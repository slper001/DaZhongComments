import requests
from lxml import etree
from bs4 import BeautifulSoup
import re
import os
import pandas as pd

search_item = 'food'

"""
@author: 机器灵砍菜刀
"""

######################
# 主程序的作用是获取到每一个区的POI区域的所有店铺url信息
######################


simulate_browser_data = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Cache-Control':'max-age=0',
    'Connection':'keep-alive',
    'Host':'www.dianping.com',
    'Upgrade-Insecure-Requests':'1',
    'Referer':'http://www.dianping.com/shenzhen/food',
    # 'Cookie':'_lxsdk_cuid=15dc6ba8e2fc8-0d2b44655a32b8-8383667-1fa400-15dc6ba8e2f12; _lxsdk=15dc6ba8e2fc8-0d2b44655a32b8-8383667-1fa400-15dc6ba8e2f12; _hc.v=90e7af6a-725b-b44d-5de7-98603d1633e7.1502277701; ua=dpuser_8461747953; ctu=f35fe1f1280ad7053a4921df829f5aeda26cc85f94458af1b7a0cb62e973c726; JSESSIONID=86489596E7872D46A55DE5B667DADEB6; aburl=1; cye=shenzhen; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; ctu=67f7a12074a99bd317e2aa0cd29db41b7e5262085c4bb99c640c6a12f26184f9001d0343a29d29025b3a449eb821650d; cy=7; s_ViewType=10; _lxsdk_s=16030c2121d-06-ad1-4e6%7C%7C337',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36'
}

'''
起始页入口函数，获取起始页面html
'''
def get_page_index():
    url = 'http://www.dianping.com/shenzhen/' + search_item
    response = requests.get(url)
    try:
        if response.status_code == 200:
            if response.text:
                return response.text
    except Exception as e:
        print('获取起始页面出错',e)
'''
解析起始页html，建立分区分子区文件夹系统，获取进入子区域的链接入口
'''
def parse_init_page_html(html):
    soup = BeautifulSoup(str(html), 'lxml')
    city_zones = soup.find_all('dt')
    POI_zones = soup.find_all('dd')
    for i in range(0,len(POI_zones)):
        city_zone = city_zones[i].string
        POI_zone = str(POI_zones[i])
        pattern_index = re.compile('data-value="(.*?)" href="',re.S)
        search_indexs = re.findall(pattern_index,POI_zone)
        pattern_zone = re.compile('href="#">(.*?)</a>',re.S)
        search_zone = re.findall(pattern_zone,POI_zone)
        for j in range(0,len(search_indexs)):
            path = os.getcwd() + '\\' + search_item + '\\' + city_zone + '\\' + str(search_zone[j]).replace('/','')
            if not os.path.exists(path):
                os.makedirs(path)
            search_zone_page_url = 'http://www.dianping.com/search/category/7/10/' + search_indexs[j]
            print("正在爬取%s%s的店铺列表url..."%(city_zone,search_zone[j]))
            second_page_html = get_second_page_index(search_zone_page_url)
            page_nums = parse_second_page_get_pageNums(second_page_html)
            page_data = pd.DataFrame()
            for k in range(1, page_nums+1):
                next_page_url = 'http://www.dianping.com/search/category/7/10/' + search_indexs[j] + 'p' +str(k)
                nex_page_html = get_second_page_index(next_page_url)
                one_page_shop_name,one_page_shop_url = parse_second_page(nex_page_html)
                one_page_data = pd.DataFrame({'shop_name':one_page_shop_name,'shop_url':one_page_shop_url})
                page_data = page_data.append(one_page_data)
            page_data.to_csv(path + '\\' + 'url_data.csv', index=False)
            page_data.drop(page_data.index, inplace=True)
'''
此函数通过search_zone_page_url进入第二页面，获取第二页面的返回信息
'''
def get_second_page_index(url):
    try:
        response = requests.get(url, headers=simulate_browser_data)
        if response.status_code==200:
            if response.text:
                return response.text
            else:
                print('空返回')
                return get_second_page_index(url)
        else:
            print('拒绝访问')
            return get_second_page_index(url)
    except Exception as e:
        print('解析第二级页面有误', e)
        return get_second_page_index(url)
'''
解析第二页面的函数，获知一共有多少页店铺信息
'''
def parse_second_page_get_pageNums(html):
    html = etree.HTML(str(html))
    # pages是找出有一共多少页店铺信息（最繁华的地区是50页信息）,
    # 有的地区（如罗湖区田贝）没有10页店铺信息，则需要另外处理(好像还没有少于5的情况)
    if html.xpath(".//body/div[2]/div[3]/div[1]/div[2]/a[10]/@title"):
        if html.xpath(".//body/div[2]/div[3]/div[1]/div[2]/a[10]/@title")[0] == '下一页':
            pages = 9
        else:
            pages = int(html.xpath(".//body/div[2]/div[3]/div[1]/div[2]/a[10]/@title")[0])
    elif html.xpath(".//body/div[2]/div[3]/div[1]/div[2]/a[8]/@title"):
        pages = 8
    elif html.xpath(".//body/div[2]/div[3]/div[1]/div[2]/a[7]/@title"):
        pages = 7
    elif html.xpath(".//body/div[2]/div[3]/div[1]/div[2]/a[6]/@title"):
        pages = 6
    elif html.xpath(".//body/div[2]/div[3]/div[1]/div[2]/a[5]/@title"):
        pages = 5
    elif html.xpath(".//body/div[2]/div[3]/div[1]/div[2]/a[4]/@title"):
        pages = 4
    elif html.xpath(".//body/div[2]/div[3]/div[1]/div[2]/a[3]/@title"):
        pages = 3
    elif html.xpath(".//body/div[2]/div[3]/div[1]/div[2]/a[2]/@title"):
        pages = 2
    elif html.xpath(".//body/div[2]/div[3]/div[1]/div[2]/a[1]/@title"):
        pages = 1
    else:
        pages = 1
    return pages
'''
解析第二页面的函数,获得进入每个店铺的url
'''
def parse_second_page(html):
    html = etree.HTML(str(html))
    # 大众点评上,一页展示的店铺是15个
    title_list = []
    shop_url_list = []
    for i in range(1, 16):
        if html.xpath("//*[@id='shop-all-list']/ul/li[%d]/div[2]/div[1]/a[1]/h4/text()"%i):
            title = html.xpath("//*[@id='shop-all-list']/ul/li[%d]/div[2]/div[1]/a[1]/h4/text()" % i)[0]
            shop_url = html.xpath(".//*[@id='shop-all-list']/ul/li[%d]/div[2]/div[1]/a[1]/@href" % i)[0]
            title_list.append(title)
            shop_url_list.append(shop_url)
        else:
            break
    return title_list, shop_url_list

if __name__ == '__main__':
    path = os.getcwd() + '\\'+ search_item
    if not os.path.exists(path):
        os.mkdir(path)
    html = get_page_index()
    parse_init_page_html(html)

