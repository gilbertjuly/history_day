# -*- coding: utf-8 -*-

import urllib, urllib2
import random
import re
import sys, os, shutil
import time
import string
import socket

#from bs4 import BeautifulSoup #for BS4
from BeautifulSoup import BeautifulSoup #for BS3
from define import *


#URL_GOOGLE = u'https://www.google.com.hk/search?hl=cn&lr=cn&ie=utf-8&oe=utf-8&q=%s&safe=high'
#URL_GOOGLE = u'http://www.google.com.hk/search?hl=cn&q=%s'
URL_GOOGLE = u'http://74.125.235.191/search?hl=cn&q=%s'
URL_BAIDU  = u'http://www.baidu.com/s?wd=%s&ie=utf-8'

MAX_SEARCH_ENG_RETRY = 3



def search_eng_query(event_str, search_eng):
    query_url = ''
    query = urllib2.quote(event_str)
    if search_eng == 'google':
        query_url = URL_GOOGLE % query
    elif search_eng == 'baidu':
        query_url = URL_BAIDU % query
    else:
        return None
    request = urllib2.Request(query_url)
    index = random.randint(0, 8)
    user_agent = user_agents[index]
    request.add_header('User-agent', user_agent)
    try:
        response = urllib2.urlopen(request, timeout=10)
    except urllib2.URLError, e:
        if hasattr(e, 'reason'):
            logger.error('We failed to reach a %s.' % search_eng)
        elif hasattr(e, 'code'):
            logger.error('The %s couldn\'t fulfill the request.' % search_eng)
        return None
    except socket.timeout:
        if IS_BAE == False:
            print 'failed to grab %, socket timeout' % search_eng
        logger.error('failed to grab %s page, timeout' % search_eng)
        return None
    except socket.error:
        if IS_BAE == False:
            print 'failed to grab %, socket error' % search_eng
        logger.error('failed to grab %s page, socket error' % search_eng)
        return None
    except:
        if IS_BAE == False:
            print 'failed to grab %, other error' % search_eng
        logger.error('failed to grab %s page, other error' % search_eng)
        return None
    html = response.read()
    #open('query.html', 'w').write(html)
    return html


def get_result_cnt(html, search_eng):
    if html == None:
        return 0
    if search_eng == 'google':
        soup = BeautifulSoup(html) 
        result_cnt = soup.find('div', id='resultStats')
        #print result_cnt
        #print result_cnt.text
        if result_cnt == None:
            return 0
        cnt_str = result_cnt.text[result_cnt.text.find(u' ') + 1 :]
        cnt_str = cnt_str[:cnt_str.find(u' ')]
        #print cnt_str
        #print cnt_str.split(',')
        #print type(cnt_str.split(','))
        final_cnt = ''
        for small_str in cnt_str.split(','):
            final_cnt += small_str
        #print string.atoi(final_cnt)
        return string.atoi(final_cnt)
    elif search_eng == 'baidu':
        soup = BeautifulSoup(html) 
        result_cnt = soup.find('span', attrs={'class':'nums'})
        if result_cnt == None:
            return 0
        #print result_cnt.text
        cnt_str = result_cnt.text[11:-1]
        final_cnt = ''
        for small_str in cnt_str.split(','):
            final_cnt += small_str
        #print string.atoi(final_cnt)
        return string.atoi(final_cnt)
    else:
        return 0


def get_search_eng_result(event, search_eng):
    result_cnt = 0
    i = 0
    while(i < MAX_SEARCH_ENG_RETRY):
        try:
            html = search_eng_query(event, search_eng)
        except:
            html = None
            logger.error('search %s query failed once' % search_eng)
            if IS_BAE == False:
                print 'search %s query failed once' % search_eng
        result_cnt = get_result_cnt(html, search_eng)
        if result_cnt != 0:
            break;
        time.sleep(0.1)
        i = i + 1
        if IS_BAE == True:
            logging.info("get searh_eng result %s at %d" % (search_eng, i))
        else:
            print "get searh_eng result %s at %d" % (search_eng, i)
    else:
        result_cnt = 0
    return result_cnt


def search_eng_rank(event):
    final_rank = 0
    #print event
    #event = event.encode('UTF-8')
    google_cnt = get_search_eng_result(event, 'google') 
    baidu_cnt = get_search_eng_result(event, 'baidu') 
    #print 'ranking : %d %d' % (google_cnt, baidu_cnt)
    if google_cnt == 0:
        if baidu_cnt > 1000000:
            baidu_cnt = 500000
        google_cnt = baidu_cnt
    elif baidu_cnt > (google_cnt * 2):
        baidu_cnt = google_cnt
    if baidu_cnt == 0:
        baidu_cnt = google_cnt
    elif google_cnt > (baidu_cnt * 5):
        google_cnt = google_cnt / 3
    final_rank = baidu_cnt + google_cnt
    #print '%s -- %d' % (event, final_rank)
    return final_rank


def parse_first_sentence(event):
    event_str = ''
    colon_loc = event.find(u'：')
    dot_loc = event.find(u'。')
    #print dot_loc
    #print event[:dot_loc]
    if colon_loc == -1:
        colon_loc = 0
    else:
        colon_loc = colon_loc + 1
    if dot_loc == -1:
        event_str = event[colon_loc:]
    else:
        event_str = event[colon_loc:dot_loc]
    return event_str.encode('UTF-8')


def test_event_rank(event_str):
    google_cnt = get_search_eng_result(event_str.encode("UTF-8"), 'google') 
    print google_cnt
    #html = search_eng_query(event_str.encode("UTF-8"), 'baidu') 
    #open('baidu.html', 'w').write(html)
    baidu_cnt = get_search_eng_result(event_str.encode("UTF-8"), 'baidu') 
    print baidu_cnt



if __name__ == '__main__':
    #test_event_rank(u"孙中山")
    #test_event_rank(u"台湾原住民泰雅族为捍卫土地及民族，发起抗日的枕头山事件")
    #test_event_rank(u"explorer")
    parse_first_sentence(u"台湾原住民泰雅族为捍卫土地及民族，发起抗日的枕头山事件。")
    parse_first_sentence(u"台湾原住民泰雅族为捍卫土地及民族，发起抗日的枕头山事件")



