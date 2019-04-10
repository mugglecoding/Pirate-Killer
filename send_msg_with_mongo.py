import datetime
import time
from wxpy import *
from pymongo import MongoClient
from pymongo.collection import Collection
from xianyu import return_result, loop_reply


bot = Bot(cache_path = True)
friend_list = bot.friends()

client = MongoClient() # 里面什么都不填的话， 默认localhost, 27017
killer_test = client['killer_test']
config_list = Collection(killer_test, 'config_list')

# 这里配置我们想要什么信息 
# msg.text.startswith('搜索关键词：') 这个写在判断语句里， 也是我们想要的信息
WORD_DICT = {
    'keyword': ['配置信息', '配置', '1', '2']
}


@bot.register(friend_list, TEXT)
def auto_reply(msg):
    print(msg.text)
    if msg.text in WORD_DICT['keyword'] or msg.text.startswith('搜索关键词：'):
        # 如果用户输入 '配置信息' 或者 '配置' 
        if msg.text == '配置信息' or msg.text == "配置":
            print(msg.sender.name,':', msg.text, 'MSG_TYPE:', msg.type)
            return '请按格式回复你的配置信息，格式如下，请把内容替换成你的内容：\n搜索关键词：麻瓜编程、自动办公、实用主义学Python'
        
        # 如果用户输入的以搜索关键词：开头的储存进数据库
        if msg.text.startswith('搜索关键词：') and len(msg.text.strip()) > 6:
            print(msg.text)
            config = {}
            config['is_sure'] = 0
            config['user_name'] = msg.sender.name
            config['query_list'] = [i.strip() for i in msg.text.lstrip('搜索关键词：').split('、') if len(i.strip())>0]
            if len(config['query_list']) == 0:
                return '请按格式回复你的配置信息，格式如下，请把内容替换成你的内容：\n搜索关键词：麻瓜编程、自动办公、实用主义学Python'
            config['is_crawled'] = False
            config['crawled_time'] = None

            # 这里应该添加一个判断， 就比如用户 输入了两遍 搜索关键词：麻瓜编程、自动办公、实用主义学Python 
            # 搜索关键词：麻瓜编程、自动办公、实用主义学Python 
            # 如果数据库里有这个用户配置的信息 就让用户回复1 和 2 否则就插入数据库 
            print(config)
            # 我们先插数据库里是否有这个用户的设置记录， 若果有就让他按 2 清除
            user = config_list.find_one({'user_name':msg.sender.name, 'is_sure': 1, 'is_crawled': True})
            if user is not None:
                return f'你之前提交过配置 配置的信息如下：\n搜索关键词：{"、".join(user["query_list"])}\n如需修改请回复 2'
            # else 证明数据库里没有这个用户的爬取数据 则判断用户是否已经设置过一次
            else:
                user = config_list.find_one({'user_name':msg.sender.name, 'is_sure': 0, 'is_crawled': False})
                if user is not None:
                    # if len(user) > 0 :
                    return f'你之前提交过配置 配置的信息如下：\n搜索关键词：{"、".join(user["query_list"])}\n确认请回复 1\n如需修改请回复 2'
                else:
                    config_list.insert(config)

            return f'你配置的信息如下：\n {msg.text}\n确认请回复 1\n如需修改请回复 2'
       

        # 如果用户会回复的是1 就说明要 确认 搜索关键词
        if msg.text == '1':
            print('am in msg.text == 1')
            user = config_list.find_one({'user_name':msg.sender.name, 'is_sure': 1, 'is_crawled': True})
            print(' hi am here')
            if user is not None:
                return f'你之前提交过配置 配置的信息如下：\n搜索关键词：{"、".join(user["query_list"])}\n如需重新配置请回复 2'
            # else 证明数据库里没有这个用户的爬取数据 则判断用户是否已经设置过一次
            else:
                user = config_list.find_one({'user_name':msg.sender.name, 'is_sure': 0, 'is_crawled': False})
                if user is not None:
                    print('找到了该用户%s' %msg.sender.name)
                    config_list.update({'user_name':msg.sender.name, 'is_sure': 0, 'is_crawled': False}, {'$set': {'is_sure': 1}})
                    msg.reply('配置成功，请稍后')
                    return_result(user, msg, config_list)
                else:
                    return '你还没有配置\n请按格式回复你的配置信息，格式如下，请把内容替换成你的内容：\n搜索关键词：麻瓜编程、自动办公、实用主义学Python'
        
        # 如果用户输入的是2 就要删除数据库中的记录 可以做逻辑删除， 我这里直接物理删除了
        if msg.text == '2':
            user = config_list.find_one({'user_name':msg.sender.name})
            if user is not None:
                config_list.remove({'user_name':msg.sender.name})
                return '请按格式回复你的配置信息，格式如下，请把内容替换成你的内容：\n搜索关键词：麻瓜编程、自动办公、实用主义学Python'
            else:                    
                return '你还没有配置\n请按格式回复你的配置信息，格式如下，请把内容替换成你的内容：\n搜索关键词：麻瓜编程、自动办公、实用主义学Python'
    # 如果输入的文本 不在 WORD_DICT 中或者 不是以搜索关键词：开头的话
    # 这里如果是自己的微信号的话 建议注释掉。。。。
    # else:
    #     return '少侠你又调皮了 配置信息有误\n请按格式回复你的配置信息，格式如下，请把内容替换成你的内容：\n搜索关键词：麻瓜编程、自动办公、实用主义学Python'


# 自动添加好友并回复 我是盗版杀手机器人，请通过回复 "配置" 来配置你的信息
@bot.register(msg_types=FRIENDS)
def auto_accept_friends(msg):
    # 接受好友请求
    new_friend = msg.card.accept()
    # 向新的好友发送消息
    new_friend.send('我是一个没有感情的盗版杀手机器人，请通过回复 "配置" 来配置你的信息')

# 每日自动发送
# 测试用的 每隔5分钟。。。 
while True:
    for user in config_list.find({}):
        time_now = datetime.datetime.now()
        if user['is_crawled'] == True and  time_now > user['crawled_time'] + datetime.timedelta(minutes=5):
        # if user['is_crawled'] == True and user['crawled_time'] + datetime.timedelta(hours=24) > time_now:
            friend = bot.friends().search(name=user['user_name'])[0]
            loop_reply(friend, user, config_list)
        time.sleep(60)

embed()
# bot.join()