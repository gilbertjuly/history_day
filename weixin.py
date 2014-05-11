#-*- coding:utf-8 -*-
import hashlib
import time
import xml.etree.ElementTree as ET
from define import *

msg = {}
	
def check_signature(signature, timestamp, nonce):
    tmpList = [WEIXIN_TOKEN, timestamp, nonce]
    tmpList.sort()
    tmpstr = "%s%s%s" % tuple(tmpList)
    hashstr = hashlib.sha1(tmpstr).hexdigest()
    if hashstr == signature:
        return True
    else:
        return False


def parse_msg(req_msg):
    xml = ET.fromstring(req_msg)
    for child in xml:
        msg[child.tag] = child.text
    return msg


def get_msg_type(msg):
    return msg['MsgType']


def get_msg_event(msg):
    return msg['Event']


def get_msg_content(msg):
    return msg['Content']


def build_autoreply_msg(msg):
    content = msg['Content'] 
    msg_resp_str = WEIXIN_TEXT_TEMPLATE % \
            (msg['FromUserName'], msg['ToUserName'], str(int(time.time())), content)
    return msg_resp_str
 

def build_flex_msg(msg, content):
    msg_resp_str = WEIXIN_TEXT_TEMPLATE % \
            (msg['FromUserName'], msg['ToUserName'], str(int(time.time())), content)
    return msg_resp_str
 

def build_test_news_msg(msg):
    SUN_TITLE = u'孙中山'
    SUN_DESCP = u'这是孙中山'
    SUN_PICURL = u'http://upload.wikimedia.org/wikipedia/commons/8/80/Sun_Yat-sen_2.jpg'
    SUN_URL = u'http://zh.wikipedia.org/wiki/%E5%AD%99%E4%B8%AD%E5%B1%B1'
    msg_resp_str = WEIXIN_NEWS_TEST_TEMPLATE % \
            (msg['FromUserName'], msg['ToUserName'], str(int(time.time())), 
                   SUN_TITLE, SUN_DESCP, SUN_PICURL, SUN_URL,
                   SUN_TITLE, SUN_DESCP, SUN_PICURL, SUN_URL)
    return msg_resp_str
        

def build_one_news(title, detail_url, img_url, desp=''):
    news_item_str = WEIXIN_ONE_NEWS_TEMPLATE % \
            (title, desp, img_url, detail_url)
    return news_item_str


def build_news_msg(msg, content, num):
    msg_resp_str = WEIXIN_NEWS_TEMPLATE % \
            (msg['FromUserName'], msg['ToUserName'], str(int(time.time())), str(num), content)
    return msg_resp_str






