#-*- coding:utf-8 -*-

#tornado web site
 
import os
import urllib
import math
import time

import tornado.wsgi
import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.httpclient import HTTPClient
from tornado.escape import json_encode, json_decode

from define import *
from wikiToday import *
import weixin


###############################################################################
###############################################################################
###############################################################################
#todo:
# multi threads
# at least two famous people
# timer
# chat robot
# push-notification


#################################################################################
############################# Golbal data #######################################
#################################################################################


crawltoday = None # type is CrawlToday class 

#################################################################################
############################# Functions   #######################################
#################################################################################
def GetDistance( lng1,  lat1,  lng2,  lat2):
    '''
        from http://only-u.appspot.com/?p=36001 method#4
    '''
    EARTH_RADIUS = 6378.137 # 地球周长/2*pi 此处地球周长取40075.02km pi=3.1415929134165665
    from math import asin,sin,cos,acos,radians, degrees,pow,sqrt, hypot,pi

    d=acos(cos(radians(lat1))*cos(radians(lat2))*cos(radians(lng1-lng2))+sin(radians(lat1))*sin(radians(lat2)))*EARTH_RADIUS*1000
    return d




#################################################################################
############################# Classes   #########################################
#################################################################################
class RootHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("This is a BAE project: hostname: %s; platform %s;\
                Try to load \"historytoday.buapp.com\\test_where\"" % (socket.gethostname(), platform.platform()))

    def post(self):
        self.write("got the post")


class WhereHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("static/where_are_you.html")


class LocationHandler(tornado.web.RequestHandler):
    def post(self):
        global jiayan_baidu_key, jiayan_latitude, jiayan_longitude, baidu_shanghai_map
        street = self.get_argument("street")
        city = self.get_argument("city")
        street = street.encode("UTF-8")
        city = city.encode("UTF-8")
        street_string = urllib.quote(street)
        city_string = urllib.quote(city)
#       *TBD*, maybe can be replaced by tornado.escape.utf8.
#        self.GeoLocation_request(street_string, city_string)  ##the async method
        key = urllib.quote(jiayan_baidu_key)
        simple_client = HTTPClient()
        response = simple_client.fetch("http://api.map.baidu.com/geocoder/v2/?ak=%s&output=json&address=%s&city=%s" % (key, street, city))
        if  response.error:
            raise  tornado.web.HTTPError(500)
        location_json  =  tornado.escape.json_decode(response.body)
        if location_json['status'] == 0:
            try:
                ### this offset is added to fix people square can't display correctly, I think it's baidu's problem. ###
                location_json['result']['location']['lng'] = location_json['result']['location']['lng'] + 0.000001
#               print  location_json['result']['location']['lng'], location_json['result']['location']['lat']
                distance = GetDistance(float(jiayan_longitude), float(jiayan_latitude),\
                    float(location_json['result']['location']['lng']), float(location_json['result']['location']['lat']))
#               map_link = baidu_shanghai_map + "&labels=%s,%s&labelStyles=MARK,1,14,0xffffff,0xff0000,1" % \
#                        (location_json['result']['location']['lng'], location_json['result']['location']['lat'])
                map_link = baidu_shanghai_map + "&markers=%s,%s|%s,%s&marklStyles=s,A,0xff0000" % \
                        (location_json['result']['location']['lng'], location_json['result']['location']['lat'], \
                        jiayan_longitude, jiayan_latitude)
                self.render("static/map_static.html", 
                    latitude = location_json['result']['location']['lat'], \
                    longitude = location_json['result']['location']['lng'],\
                    map_img = map_link,\
                    distance = "%.2f" % distance,)
            except:
                self.write("<html><body><h2>Oops! Somthing Wrong! Havn't find your location!</h2></body><html>\n")
        else:
            self.write("<html><body><h2>Havn't find your location!</h2></body><html>\n")


class WeixinHandler(tornado.web.RequestHandler):
    def get(self):
        signature = self.get_argument(name='signature')  
        timestamp = self.get_argument(name='timestamp')
        nonce = self.get_argument(name='nonce')
        echostr = self.get_argument(name='echostr')
        checkSignatureResult = weixin.check_signature(signature, timestamp, nonce)
        if  checkSignatureResult == True:
            self.write(echostr)
        else:
            raise tornado.web.HTTPError(status_code=500,log_message="接入微信平台失败" )

    def post(self):
        global crawltoday
        #print self.request.body
        msg_req = self.request.body
        msg_req_xml = weixin.parse_msg(msg_req) # parse out the xml, assuming the msg_req is UTF8 encoded
        msg_type = weixin.get_msg_type(msg_req_xml)
        if msg_type == 'event':
            msg_event = weixin.get_msg_event(msg_req_xml)
            if msg_event == 'subscribe':
                msg_resp_str = weixin.build_flex_msg(msg_req_xml, u"欢迎关注，查看历史上的今天请发送\"今天\"两字")

        elif msg_type == 'text':
            msg_content = weixin.get_msg_content(msg_req_xml)
            if msg_content == u"今天2":
                content = ''
                index = 0
                for entry in crawltoday.eventEntries:
                    content += entry.title
                    index += 1
                    if index == MAX_EVENT_ENTRIES:
                        break
                msg_resp_str = weixin.build_flex_msg(msg_req_xml, content)

            elif msg_content == u"今天":
                content = ''
                index = 0
                for entry in crawltoday.eventEntries:
                    content += weixin.build_one_news(entry.title, entry.detail, entry.img_url) 
                    index += 1
                    if index == MAX_EVENT_ENTRIES:
                        break
                msg_resp_str = weixin.build_news_msg(msg_req_xml, content, index)

            elif msg_content == u"更新2":
                msg_resp_str = weixin.build_flex_msg(msg_req_xml, "updating at server..., try again after 10 mins!")
                del crawltoday
                crawltoday = CrawlToday()
                today_page = crawltoday.grab_page()
                crawltoday.parse_events(today_page)

            #elif msg_content == u"孙中山":
            #    msg_resp_str = weixin.build_test_news_msg(msg_req_xml)

            else:
                #msg_resp_str = weixin.build_autoreply_msg(msg_req_xml)
                msg_resp_str = weixin.build_flex_msg(msg_req_xml, u"本机器人不支持聊天，查看今天信息请发送\"今天\"两字")

        self.write(msg_resp_str.encode(encoding='UTF-8', errors='ignore'))


#################################################################################
############################# Timer   ###########################################
################################################################################# 
from datetime import datetime, timedelta
from threading import Timer

current = datetime.today()
#next_round = current.replace(day=current.day+1, hour=6, minute=30, second=0, microsecond=0)
#next_round = current.replace(day=current.day, hour=current.hour, minute=current.minute, second=current.second+2, microsecond=0)
#next_round = (current + timedelta(days=0)).replace(hour=current.hour, minute=current.minute, second=current.second+2)
next_round = (current + timedelta(days=1)).replace(hour=6, minute=30, second=0)

delta_t = next_round - current
secs = delta_t.seconds + 1

def update_today_events():
    t = Timer(secs, update_today_events)
    t.start()
    if IS_BAE == True:
        logger.info('updating eventEntries every day')
    else:
        print 'updaing eventEntries everyday'
    del crawltoday
    crawltoday = CrawlToday()
    today_page = crawltoday.grab_page()
    crawltoday.parse_events(today_page)


t = Timer(secs, update_today_events)
t.start()

if IS_BAE == True:
    logger.info('%s' % current)
else:
    print current


#################################################################################
############################# Main Entry   ######################################
################################################################################# 
settings = {
        'debug' : True,
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
    }

url_handlers = [
        (r"/", RootHandler),
	    (r"/weixin", WeixinHandler),
	    (r"/test_where", WhereHandler),        # a self-test for handler
	    (r"/test_location", LocationHandler),  # a self-test for handler
    ]

logger.info('starting to get wikiToday...')

crawltoday = CrawlToday()
today_page = crawltoday.grab_page()
crawltoday.parse_events(today_page)

logger.info('finish getting wikiToday...')

if IS_BAE == True:
    app = tornado.wsgi.WSGIApplication(url_handlers,**settings) 
    from bae.core.wsgi import WSGIApplication
    application = WSGIApplication(app)
else:
    class Application(tornado.web.Application):
        def __init__(self):
            tornado.web.Application.__init__(self, url_handlers, **settings)

    from tornado.options import define, options
    define("port", default=8008, help="run on the given port", type=int)

    if __name__ == "__main__":
        tornado.options.parse_command_line()
        http_server = tornado.httpserver.HTTPServer(Application())
        http_server.listen(options.port)
        print 'tornado listening at', options.port
        tornado.ioloop.IOLoop.instance().start()




