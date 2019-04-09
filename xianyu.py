import re
import time
import requests
import multiprocessing
from fake_useragent import UserAgent
from lxml import etree
from multiprocessing import Pool
# 不能从send_msg_with_mongo 导入  我就把这边的函数引过去。。。。
# from send_msg_with_mongo import config_list, friend_list

ua = UserAgent()
headers = {
    'User-Agent': ua.random
}

def get_you_want(query):
    url = f'https://s.2.taobao.com/list/?_input_charset=utf8&q={query}'
    resp = requests.get(url, headers=headers).text
    urls = []
    try:
        total_page = int(re.findall("共(\d+)页", resp)[0])
        # 我们这里返回前10页就够了， 100页的商品 后面基本都是没用的
        if total_page > 10:
            total_page = 10
        for i in range(1, total_page+1):
            url = f'https://s.2.taobao.com/list/?_input_charset=utf8&q={query}&page={i}'
            urls.append(url) 
        return urls
    except:
        return None




def parse_page(url, msg, query):
    resp = requests.get(url, headers=headers).text
    time.sleep(1)
    html = etree.HTML(resp)
    items = html.xpath("//div[contains(@class, 'ks-waterfall')]")[1:]
    for item in items:
        data = {
            'title' : item.xpath('.//div[@class="item-pic"]/a/@title')[0],
            'img' : item.xpath('.//div[@class="item-pic"]/a/img/@src')[0],
            'href' : 'https:' + item.xpath('.//div[@class="item-pic"]/a/@href')[0],
            'item_id': item.xpath('.//div[@class="item-pic"]/a/@href')[0].split('=')[-1],
            'desc' : item.xpath('.//div[@class="item-brief-desc"]/text()')[0],
            'price' : item.xpath('.//span[@class="price"]/em/text()')[0],
            'location' : item.xpath('.//div[@class="item-location"]/text()')[0],
            # 'is_sold': False
        }
        # 这里最好判断一下关键词在不在里面。。。 设置个办公自动化 美容美体床、自动双面激光打印机都给我出来了。。。
        if query in data['title'] or query in data['desc']:
            print(f"{query} 新发现一个盗版商品-{data['title']}-{data['href']}")
            print(data['item_id'])
            msg.reply(f"{query} 新发现一个盗版商品-{data['title']}-电脑链接为{data['href']}\n app链接为 https://market.m.taobao.com/app/idleFish-F2e/widle-taobao-rax/page-detail?wh_weex=true&wx_navbar_transparent=true&id={data['item_id']}")
            time.sleep(1)

            
def return_result(user, msg, config_list):
    # MAX_WORKER_NUM = multiprocessing.cpu_count()
    # pool = Pool(MAX_WORKER_NUM)
    query_list = user['query_list']
    print(query_list)           
    # query = '麻瓜编程'
    for query in query_list:
        urls = get_you_want(query)
        if urls:
            for url in urls:
                parse_page(url, msg, query)
            msg.reply('-----------------------')
                # 这里多进程好像用不了。。。。也不用了吧。。 爬取太快 发送的太快..号会不会被封。。。 
                # pool.apply_async(parse_page, args=(url, msg))
        #  不close 不join 程序运行不了。。
        # pool.close()
        # pool.join()
        else:
            msg.reply('没有找到相关的信息 %s' %query)
    msg.reply('回复完毕， 请查看！')
    # 更新用户 是否已经爬取 是 。这里不保存信息的话也可以从数据库直接删除
    config_list.update({'user_name':user['user_name'], 'is_sure': 1, 'is_crawled': False},{"$set":{'is_crawled': True}})
		