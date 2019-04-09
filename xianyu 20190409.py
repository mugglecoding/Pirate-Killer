import csv
import requests
import urllib
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from wxpy import *


def do_request(url_in):
    # 请求网页

    def get_fake_header():
        ua = UserAgent()
        fake_headers = {'User-Agent': ua.random}
        return fake_headers

    headers = get_fake_header()
    try:
        wb_data = requests.get(url_in, headers=headers)
        html_sp_out = BeautifulSoup(wb_data.text, 'lxml')
    except requests.RequestException as request_err:
        print('\n', '=' * 50, "\nrequest error:\n", request_err)
        html_sp_out = None

    return html_sp_out


def do_xianyu(xianyu_word='梁山泊'):

    url_0 = 'https://s.2.taobao.com/list/?q='
    url_key_word = urllib.parse.quote(xianyu_word, encoding='gbk')
    url_99 = '&search_type=item&app=shopsearch'
    url_full = url_0 + url_key_word + url_99

    html_soup = do_request(url_full)

    items = html_soup.select("div.item-pic > a")
    sellers = html_soup.select("div.seller-avatar > a")
    attention_list_out = [{
        'title': iItem.get('title'),
        'seller': iSeller.get('title'),
        'link': 'https:' + iItem.get('href')
    } for iItem, iSeller in zip(items, sellers)]

    return attention_list_out

def save_xianyu_info(data_list, filepath_write='./xianyu_info.txt'):

    with open(filepath_write, "w", encoding='utf8', newline='') as xianyu_file:
        file_header = ['title', 'seller', 'link']
        csv_dict_writer = csv.DictWriter(xianyu_file, file_header)
        csv_dict_writer.writeheader()
        csv_dict_writer.writerows(data_list)
        xianyu_file.close()

    return 0


def send_wechat_notice(filepath_send, receiver='林茜茜-麻瓜编程'):

    wechat_bot = Bot()
    wechat_talk = wechat_bot.friends().search(receiver)[0]
    wechat_talk.send_msg('发现如下的商品，请看一下哦')
    wechat_talk.send_file(filepath_send)

    return 0


# 主函数
if __name__ == '__main__':

    keyword = '麻瓜编程'
    attention_list = do_xianyu(xianyu_word=keyword)

    data_path = './xianyu_info.txt'
    save_xianyu_info(data_list=attention_list, filepath_write=data_path)

    wechat_name = '林茜茜-麻瓜编程'
    send_wechat_notice(filepath_send=data_path, receiver=wechat_name)





