import re
import time
import requests
import datetime
from fake_useragent import UserAgent
from lxml import etree
# 不能从send_msg_with_mongo 导入  我就把这边的函数引过去。。。。
# from send_msg_with_mongo import config_list, friend_list

ua = UserAgent()
headers = {
    'User-Agent': ua.random
}

def get_you_want(query):
    url = f'https://s.2.taobao.com/list/?_input_charset=utf8&ist=1&q={query}'
    resp = requests.get(url, headers=headers).text
    urls = []
    try:
        total_page = int(re.findall("共(\d+)页", resp)[0])
        # 我们这里返回前10页就够了， 100页的商品 后面基本都是没用的
        if total_page > 10:
            total_page = 10
        for i in range(1, total_page+1):
            url = f'https://s.2.taobao.com/list/?_input_charset=utf8&ist=1&q={query}&page={i}'
            urls.append(url) 
        return urls
    except:
        return None

def parse_pub_time(pub_time):
    if '分钟' in pub_time:
        num = int(re.search('\d+', pub_time).group())
        pub_time = datetime.datetime.now() - datetime.timedelta(minutes=num)
    elif '小时' in pub_time:
        num = int(re.search('\d+', pub_time).group())
        pub_time = datetime.datetime.now() - datetime.timedelta(hours=num)
    elif '天' in pub_time:
        num = int(re.search('\d+', pub_time).group())
        pub_time = datetime.datetime.now() - datetime.timedelta(days=num)
    elif '月' in pub_time:
        num = int(re.search('\d+', pub_time).group())
        pub_time = datetime.datetime.now() - datetime.timedelta(days=30*num)
    elif '年' in pub_time:
        num = int(re.search('\d+', pub_time).group())
        pub_time = datetime.datetime.now() - datetime.timedelta(days=365*num)
    return pub_time


def parse_page_auto(url, data_list, query, user):
    resp = requests.get(url, headers=headers).text
    time.sleep(1)
    html = etree.HTML(resp)
    items = html.xpath("//div[contains(@class, 'ks-waterfall')]")[1:]
    for item in items:
        item_id = item.xpath('.//div[@class="item-pic"]/a/@href')[0].split('=')[-1]
        data = {
            'title': item.xpath('.//div[@class="item-pic"]/a/@title')[0],
            'img': item.xpath('.//div[@class="item-pic"]/a/img/@src')[0],
            'href': 'https:' + item.xpath('.//div[@class="item-pic"]/a/@href')[0],
            'item_id': item_id,
            'desc': item.xpath('.//div[@class="item-brief-desc"]/text()')[0],
            'price': item.xpath('.//span[@class="price"]/em/text()')[0],
            'location': item.xpath('.//div[@class="item-location"]/text()')[0],
            'pub_time': parse_pub_time(item.xpath('.//span[@class="item-pub-time"]/text()')[0]),
            'app_link': 'https://market.m.taobao.com/app/idleFish-F2e/widle-taobao-rax/page-detail?wh_weex=true&wx_navbar_transparent=true&id=' + item_id
            # 'is_sold': False
        }
        # 这里最好判断一下关键词在不在里面。。。 设置个办公自动化 美容美体床、自动双面激光打印机都给我出来了。。。
        # 如果第一爬的话 就全部返回 第一次爬 
        if query in data['title'] or query in data['desc']:
            # if user['crawled_time'] is None:
            print(f"{query} 新发现一个盗版商品-{data['title']}-{data['href']}")
            data_list.append(data)
         
def return_result(user, msg, config_list):
    query_list = user['query_list']
    print(query_list)           
    # query = '麻瓜编程'
    for query in query_list:
        data_list = []
        urls = get_you_want(query)
        if urls:
            for url in urls:
                parse_page_auto(url, data_list, query, user)
        if len(data_list) > 0:
            for data in data_list:
                msg.reply(f"{query} 新发现一个盗版商品-{data['title']}-{data['href']}\napp链接为:{data['app_link']}")
                time.sleep(1)
            msg.reply('-----------------------')
        else:
            msg.reply('没有找到相关的信息 %s' %query)
    msg.reply('回复完毕， 请查看！')
    # 更新用户 是否已经爬取 是 。这里不保存信息的话也可以从数据库直接删除
    config_list.update({'user_name':user['user_name'], 'is_sure': 1, 'is_crawled': False},{"$set":{'is_crawled': True, 'crawled_time':datetime.datetime.now()}})
		

def parse_page(url, data_list, query, user):
    resp = requests.get(url, headers=headers).text
    time.sleep(1)
    html = etree.HTML(resp)
    items = html.xpath("//div[contains(@class, 'ks-waterfall')]")[1:]
    for item in items:
        item_id = item.xpath('.//div[@class="item-pic"]/a/@href')[0].split('=')[-1]
        data = {
            'title': item.xpath('.//div[@class="item-pic"]/a/@title')[0],
            'img': item.xpath('.//div[@class="item-pic"]/a/img/@src')[0],
            'href': 'https:' + item.xpath('.//div[@class="item-pic"]/a/@href')[0],
            'item_id': item_id,
            'desc': item.xpath('.//div[@class="item-brief-desc"]/text()')[0],
            'price': item.xpath('.//span[@class="price"]/em/text()')[0],
            'location': item.xpath('.//div[@class="item-location"]/text()')[0],
            'pub_time': parse_pub_time(item.xpath('.//span[@class="item-pub-time"]/text()')[0]),
            'app_link': 'https://market.m.taobao.com/app/idleFish-F2e/widle-taobao-rax/page-detail?wh_weex=true&wx_navbar_transparent=true&id=' + item_id
            # 'is_sold': False
        }
        print(f"pub_time:{data['pub_time']}, crawled_time:{user['crawled_time']}")
        # 这里最好判断一下关键词在不在里面。。。 设置个办公自动化 美容美体床、自动双面激光打印机都给我出来了。。。
        # 如果第一爬的话 就全部返回 第一次爬 
        if query in data['title'] or query in data['desc']:
            if data['pub_time'] > user['crawled_time']:
                print(f"{query} 新发现一个盗版商品-{data['title']}-{data['href']}")
                data_list.append(data)

                    
                               

def loop_reply(friend, user, config_list):
	# 更新用户 是否已经爬取 是 。这里不保存信息的话也可以从数据库直接删除
    config_list.update({'user_name':user['user_name'], 'is_sure': 1, 'is_crawled': True},{"$set":{'crawled_time':datetime.datetime.now()}})

    query_list = user['query_list']
    print(query_list)           
    # query = '麻瓜编程'
    for query in query_list:
        data_list = []
        urls = get_you_want(query)
        print(urls)
        if urls:
            for url in urls:
                parse_page(url, data_list, query, user)
        if len(data_list) > 0:
            for data in data_list:
                friend.send(f"{query} 新发现一个盗版商品-{data['title']}-{data['href']}\napp链接为:{data['app_link']}")
                time.sleep(1)
            friend.send('-----------------------')
        else:
            friend.send('没有找到相关的信息 %s' %query)
    friend.send('回复完毕， 请查看！')
    	

