import requests
from lxml import etree
import pandas as pd
import re
import json
import time

"""
@author: 机器灵砍菜刀
"""

######################
# 次程序的作用是根据主程序中获取的url列表信息，依次提取店铺的详细信息
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
根据每个店铺的url，获取店铺页面返回html
'''
def get_shop_html(url):
    try:
        response = requests.get(url, headers=simulate_browser_data)
        if response.status_code == 403:
            print("服务器拒绝访问店铺页")
            return get_shop_html(url)
        elif response.status_code == 200:
            if response.text:
                return response.text
            else:
                print('存在空返回，重新请求')
                return get_shop_html(url)
        else:
            print('获取店铺页面状态码%d'%response.status_code)
            return get_shop_html(url)
    except Exception as e:
        print('获取店铺详细信息出错', e)
        return get_shop_html(url)
'''
根据每个店铺的评论页url，获取店铺评论页返回html
'''
def get_shop_review_html(url):
    try:
        response=requests.get(url,headers=simulate_browser_data)
        if response.status_code==403:
            print('服务器拒绝访问评论页详细信息')
            return get_shop_review_html(url)
        elif response.status_code==200:
            return response.text
        else:
            print('获取店铺评论页状态码%d'%response.status_code)
            return get_shop_review_html(url)
    except Exception as e:
        print("获取店铺详评论细信息出错", e)
        return get_shop_review_html(url)
'''
解析每一个店铺信息
'''
def parse_shop_info(html):
    shop_config_pattern = re.compile('window.shop_config=(.*?)</script>',re.S)
    shop_config = json.dumps(re.search(shop_config_pattern,str(html)).group(1).replace('\n','').replace(' ','').replace('"',''),ensure_ascii=False)
    shop_config = eval(str(shop_config))
    shop_config_dict = {}
    # print(shop_config)
    for item in shop_config.split(','):
        if len(item.split(':', 1)) == 2:
            key = item.split(':', 1)[0]
            value = item.split(':', 1)[1]
            shop_config_dict[key] = value
    html = etree.HTML(str(html))
    shop_name = html.xpath(".//*[@id='basic-info']/h1/text()")[0].replace('\n','')
    if html.xpath("//*[@id='basic-info']/div[1]/span[1]/@title"):
        shop_level = html.xpath("//*[@id='basic-info']/div[1]/span[1]/@title")[0]
    else:
        shop_level = None
    if html.xpath("//*[@id='reviewCount']/text()"):
        reviewCount = html.xpath("//*[@id='reviewCount']/text()")[0]
    else:
        reviewCount = None
    if html.xpath("//*[@id='avgPriceTitle']/text()"):
        avgPrice = html.xpath("//*[@id='avgPriceTitle']/text()")[0]
    else:
        avgPrice = None
    if html.xpath("//*[@id='comment_score']/span[1]/text()"):
        taste_score = html.xpath("//*[@id='comment_score']/span[1]/text()")[0]
    else:
        taste_score = None
    if html.xpath("//*[@id='comment_score']/span[2]/text()"):
        environment_score = html.xpath("//*[@id='comment_score']/span[2]/text()")[0]
    else:
        environment_score = None
    if html.xpath("//*[@id='comment_score']/span[3]/text()"):
        server_score = html.xpath("//*[@id='comment_score']/span[3]/text()")[0]
    else:
        server_score = None
    if html.xpath("//*[@class='expand-info address']/span[2]/text()"):
        address = html.xpath("//*[@class='expand-info address']/span[2]/text()")[0].replace('\n','')
    else:
        address = None
    if html.xpath("//*[@class='expand-info tel']/span[2]/text()"):
        tel = html.xpath("//*[@class='expand-info tel']/span[2]/text()")[0]
    else:
        tel = None
    if html.xpath("//*[@class='info info-indent']/span[2]/text()"):
        business_hours = html.xpath("//*[@class='info info-indent']/span[2]/text()")[0].replace('\n','').replace(' ','')
    else:
        business_hours = None
    shop_summarize_info = pd.DataFrame({'shop_name':[shop_name],'fullName':[shop_config_dict['fullName'].replace('|','').replace('/','')],'shopLat':[shop_config_dict['shopGlat']],
                                        'shopLng':[shop_config_dict['shopGlng']],'shopScore':[shop_config_dict['shopPower']],
                                        'shop_level':[shop_level],'reviewCount':[reviewCount],'avePrice':[avgPrice],'mainCategoryName':[shop_config_dict['mainCategoryName']],
                                        'taste_score':[taste_score],'environment_score':[environment_score],'server_score':[server_score],
                                        'address':[address],'tel':[tel],'business_hours':[business_hours]})
    shop_summarize_info.to_csv('%sS.csv'%shopId,index=False)
    return shop_config_dict['fullName'].replace('|','').replace('/','')
'''
获得店铺评论页页数数量
'''
def get_review_page_count(html):
    html = etree.HTML(str(html))
    if html.xpath('//*[@class="reviews-pages"]/a[9]/text()') and html.xpath('//*[@class="reviews-pages"]/a[9]/text()')[0] != '下一页':
        page_num = html.xpath('//*[@class="reviews-pages"]/a[9]/text()')[0]
    elif html.xpath('//*[@class="reviews-pages"]/a[8]/text()') and html.xpath('//*[@class="reviews-pages"]/a[8]/text()')[0] != '下一页':
        page_num = html.xpath('//*[@class="reviews-pages"]/a[8]/text()')[0]
    elif html.xpath('//*[@class="reviews-pages"]/a[7]/text()') and html.xpath('//*[@class="reviews-pages"]/a[7]/text()')[0] != '下一页':
        page_num = html.xpath('//*[@class="reviews-pages"]/a[7]/text()')[0]
    elif html.xpath('//*[@class="reviews-pages"]/a[6]/text()') and html.xpath('//*[@class="reviews-pages"]/a[6]/text()')[0] != '下一页':
        page_num = html.xpath('//*[@class="reviews-pages"]/a[6]/text()')[0]
    elif html.xpath('//*[@class="reviews-pages"]/a[5]/text()') and html.xpath('//*[@class="reviews-pages"]/a[5]/text()')[0] != '下一页':
        page_num = html.xpath('//*[@class="reviews-pages"]/a[5]/text()')[0]
    elif html.xpath('//*[@class="reviews-pages"]/a[4]/text()') and html.xpath('//*[@class="reviews-pages"]/a[4]/text()')[0] != '下一页':
        page_num = html.xpath('//*[@class="reviews-pages"]/a[4]/text()')[0]
    elif html.xpath('//*[@class="reviews-pages"]/a[3]/text()') and html.xpath('//*[@class="reviews-pages"]/a[3]/text()')[0] != '下一页':
        page_num = html.xpath('//*[@class="reviews-pages"]/a[3]/text()')[0]
    elif html.xpath('//*[@class="reviews-pages"]/a[2]/text()') and html.xpath('//*[@class="reviews-pages"]/a[2]/text()')[0] != '下一页':
        page_num = html.xpath('//*[@class="reviews-pages"]/a[2]/text()')[0]
    elif html.xpath('//*[@class="reviews-pages"]/a[1]/text()') and html.xpath('//*[@class="reviews-pages"]/a[1]/text()')[0] != '下一页':
        page_num = html.xpath('//*[@class="reviews-pages"]/a[1]/text()')[0]
    else:
        page_num = 1
    return page_num
'''
解析店铺评论详细页信息
'''
def parse_review_info(html):
    html = etree.HTML(str(html))
    #一页最多含有20个评论内容
    goodComementCountList,middleCommentCountList,badCommentCountList = [],[],[]
    user_name_list,user_id_list,user_comment_score_list,user_taste_score_list,user_environment_score_list,user_server_score_list, \
    user_comment_text_list,user_comment_time_list= [],[],[],[],[],[],[],[]
    for i in range(1,21):
        if html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[2]/div[1]/label[3]/span/text()'):
            goodComementCount = html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[2]/div[1]/label[3]/span/text()')[0].replace('(', '').replace(')', '')
        else:
            goodComementCount = None
        if html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[2]/div[1]/label[4]/span/text()'):
            middleCommentCount = html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[2]/div[1]/label[4]/span/text()')[0].replace('(', '').replace(')', '')
        else:
            middleCommentCount = None
        if html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[2]/div[1]/label[5]/span/text()'):
            badCommentCount = html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[2]/div[1]/label[5]/span/text()')[0].replace('(', '').replace(')', '')
        else:
            badCommentCount = None
        if html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[%d]/div/div[1]/a/text()'%i):
            user_name = html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[%d]/div/div[1]/a/text()'%i)[0]
        else:
            break
        # user_id = html.xpath('//*[@class="comment-list"]/ul[1]/li[%d]/div[1]/a/@user-id'%i)[0]
        # 因为09年之前，大众点评上有些用户的评论会没有用户评分信息，因此需要判断
        if html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[%d]/div/div[2]/span[1]/@class'%i):
            user_comment_score = html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[%d]/div/div[2]/span[1]/@class'%i)[0]
        else:
            user_comment_score = None
        # 由于有极少一部分的用户，没有给味道环境和服务评分，所以需要判断
        if html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[%d]/div/div[2]/span[2]/span[1]/text()'%i):
            user_taste_score = html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[%d]/div/div[2]/span[2]/span[1]/text()'%i)[0]
        else:
            user_taste_score = None
        if html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[%d]/div/div[2]/span[2]/span[2]/text()'%i):
            user_environment_score = html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[%d]/div/div[2]/span[2]/span[2]/text()'%i)[0]
        else:
            user_environment_score = None
        if html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[%d]/div/div[2]/span[2]/span[3]/text()'%i):
            user_server_score = html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[%d]/div/div[2]/span[2]/span[3]/text()'%i)[0]
        else:
            user_server_score = None
        if html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[%d]/div/div[3]/text()'%i):
            user_comment_text = html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[%d]/div/div[3]/text()'%i)[0]
        else:
            user_comment_text = None
        if html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[%d]/div/div[4]/span[1]/text()'%i):
            user_comment_time = html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[%d]/div/div[4]/span[1]/text()'%i)[0].replace('\n', '').replace(' ', '')
        elif html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[%d]/div/div[5]/span[1]/text()'%i):
            user_comment_time = html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[%d]/div/div[5]/span[1]/text()'%i)[0].replace('\n', '').replace(' ', '')
        elif html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[%d]/div/div[3]/span[1]/text()'%i):
            user_comment_time = html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[%d]/div/div[3]/span[1]/text()'%i)[0].replace('\n', '').replace(' ', '')
        elif html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[%d]/div/div[6]/span[1]/text()'%i):
            user_comment_time = html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[%d]/div/div[6]/span[1]/text()'%i)[0].replace('\n', '').replace(' ', '')
        elif html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[%d]/div/div[7]/span[1]/text()'%i):
            user_comment_time = html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[%d]/div/div[7]/span[1]/text()'%i)[0].replace('\n', '').replace(' ', '')
        else:
            user_comment_time = html.xpath('//*[@id="review-list"]/div[2]/div[1]/div[3]/div[3]/ul/li[%d]/div/div[2]/span[1]/text()' % i)[0].replace('\n','').replace(' ', '')
        goodComementCountList.append(goodComementCount)
        middleCommentCountList.append(middleCommentCount)
        badCommentCountList.append(badCommentCount)
        user_name_list.append(user_name)
        user_comment_score_list.append(user_comment_score)
        user_taste_score_list.append(user_taste_score)
        user_environment_score_list.append(user_environment_score)
        user_server_score_list.append(user_server_score)
        user_comment_text_list.append(user_comment_text)
        user_comment_time_list.append(user_comment_time)
    one_page_data = pd.DataFrame({'goodComementCount':goodComementCountList,'middleCommentCount':middleCommentCountList,'badCommentCount':badCommentCountList,
                                  'user_name':user_name_list,
                                  'user_comment_score':user_comment_score_list,'user_taste_score':user_taste_score_list,
                                  'user_environment_score':user_environment_score_list,'user_server_score':user_server_score_list,
                                  'user_comment_text':user_comment_text_list,'user_comment_time':user_comment_time_list})
    return one_page_data
if __name__ == '__main__':
    url_data = pd.read_csv('url_data.csv', encoding='ISO-8859-1')
    urls = list(url_data.shop_url)
    shopCount = 0
    complete_shop = 0
    for url in urls:
        complete_shop +=1
        shopId = url.split('shop/')[1]
        if complete_shop >0:
            print(url)
            page_html = get_shop_html(url)
            full_shop_name = parse_shop_info(page_html)
            print('正在抓取%s详细信息...' % full_shop_name)
            review_url = url + '/' + 'review_all'
            review_page_html = get_shop_review_html(review_url)
            review_page_num = int(get_review_page_count(review_page_html))
            print('一共%d页评论页信息' % review_page_num)
            one_shop_comment_data = pd.DataFrame()
            for i in range(1, review_page_num + 1):
                print('正在抓取第%d页评论信息......' % i)
                review_page_url = review_url + '/' + 'p' + str(i)
                review_page_url_html = get_shop_review_html(review_page_url)
                one_page_data = parse_review_info(review_page_url_html)
                one_shop_comment_data = one_shop_comment_data.append(one_page_data)
            one_shop_comment_data.to_csv('%s.csv' % shopId, index=False)
            shopCount += 1
            print('已成功抓取%d个店铺评论信息' % shopCount)
