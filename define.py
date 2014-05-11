#-*- coding:utf-8 -*-
import os
import sys
import logging
import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger()

################################################################################
################################################################################
################################################################################
import socket
import platform

MY_DELL = "dell"
MY_PRESARIO = "presario"

running_host = socket.gethostname() 
if (MY_DELL == running_host) or (MY_PRESARIO == running_host):
    IS_BAE = False
else:
    IS_BAE = True

################################################################################
################################################################################
################################################################################

user_agents = [ 
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0', \
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0', \
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533+ (KHTML, like Gecko) Element Browser 5.0', \
    'IBM WebExplorer /v0.94', 'Galaxy/1.0 [en] (Mac OS X 10.5.6; U; en)', \
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)', \
    'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14', \
    'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25', \
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1468.0 Safari/537.36', \
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; TheWorld)']


class HttpException(Exception):
    pass

################################################################################
################################################################################
################################################################################

WEIXIN_TOKEN = 'cruz_2009'

WEIXIN_TEXT_TEMPLATE = \
'''
<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[%s]]></Content>
</xml>'''

WEIXIN_NEWS_TEST_TEMPLATE = \
'''
<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[news]]></MsgType>
<ArticleCount>2</ArticleCount>
<Articles>
<item>
<Title><![CDATA[%s]]></Title> 
<Description><![CDATA[%s]]></Description>
<PicUrl><![CDATA[%s]]></PicUrl>
<Url><![CDATA[%s]]></Url>
</item>
<item>
<Title><![CDATA[%s]]></Title>
<Description><![CDATA[%s]]></Description>
<PicUrl><![CDATA[%s]]></PicUrl>
<Url><![CDATA[%s]]></Url>
</item>
</Articles>
</xml> 
'''

WEIXIN_ONE_NEWS_TEMPLATE = \
'''
<item>
<Title><![CDATA[%s]]></Title>
<Description><![CDATA[%s]]></Description>
<PicUrl><![CDATA[%s]]></PicUrl>
<Url><![CDATA[%s]]></Url>
</item>

'''

WEIXIN_NEWS_TEMPLATE = \
'''
<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[news]]></MsgType>
<ArticleCount>%s</ArticleCount>
<Articles>
%s
</Articles>
</xml> 
'''


MAX_EVENT_ENTRIES = 10


######### below is for testing ########
jiayan_latitude = "31.190191760237"
jiayan_longitude = "121.54451409752"
jiayan_baidu_key = "68c73dd79134ebf8f8574eed21f77f64"
jiayan_baidu_key = jiayan_baidu_key.encode("UTF-8")
baidu_shanghai_map = "http://api.map.baidu.com/staticimage?width=800&height=600&center=121.47894508654,31.236004921296&zoom=12"


####### for code backup #######


