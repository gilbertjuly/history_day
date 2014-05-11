# -*- coding: utf-8 -*-

import urllib, urllib2
import random
import re
import sys, os, shutil
import time
import socket

#from bs4 import BeautifulSoup #for BS4
from BeautifulSoup import BeautifulSoup #for BS3

import eventRank
from define import *



URL_WIKI = u'http://zh.wikipedia.org/zh-cn/' # convert to chinese page
URL_DATE = u'%s月%s日'
#URL_TODAY2 = u'http://www.todayonhistory.com/%s/%s/index.htm' # %(month, day)
#URL_TODAY3 = u'http://www1.wst.net.cn/scripts/flex/TodayOnHistory/'
# choose a good web to crawl, because it has title and  content link, photo as well.
# the other two are for backup purpose.
# the class is particularly built for this link only.
#URL_TODAY = URL_TODAY1 

URL_DEBUG = 0
RANK_DEBUG = 0

class EventEntry(object):
    title   = None
    img     = None
    img_url = None
    detail  = None
    rank    = 0 
    
    def __init__(self, title, detail=None, rank=0, img_url=None, img=None):
        self.title = title
        self.detail = detail
        self.rank = rank
        self.img_url = img_url
        self.img = img


class CrawlToday(object): # object is for new-style class in python2.2+.?
    month = 0
    day = 0
    url_today = None # the class is built for URL_TODAY
    eventEntries = []

    def __init__(self, month=None, day=None):
        if(month == None) or (day == None):
            #print time.localtime(time.time())
            self.month = time.localtime(time.time()).tm_mon
            self.day = time.localtime(time.time()).tm_mday
        else:
            self.month = month
            self.day = day
        #print "crawling month: %d, day: %d" % (self.month, self.day)
        url_date = URL_DATE % (self.month, self.day)
        url_date = url_date.encode("UTF-8")
        self.url_today = URL_WIKI + urllib.quote(url_date) # quote -- convert chinese to url
        #print url_today

        http_handler = urllib2.HTTPHandler(debuglevel=URL_DEBUG)
        opener = urllib2.build_opener(http_handler)
        urllib2.install_opener(opener)


    def __del__(self):
        del self.eventEntries[:]
 

    def grab_page_once(self, url_req):
        try:
            url_resp = urllib2.urlopen(url_req, timeout=10)
        except urllib2.URLError, e:
            if hasattr(e, 'reason'):
                logger.error('We failed to reach a server.')
                #logger.error('Reason: %s' % e.reason)
            elif hasattr(e, 'code'):
                logger.error('The server couldn\'t fulfill the request.')
                #logger.error('Error code: %d' % e.code)
            #exit() # do something here, notify the admin
            logger.error('failed to gabe wiki page, urllib fail')
            return None
        except socket.timeout:
            if IS_BAE == False:
                print 'failed to grab wiki page, socket timeout'
            logger.error('failed to grab wiki page, socket timeout')
            return None
        except socket.error:
            if IS_BAE == False:
                print 'failed to grab wiki page, socket error'
            logger.error('failed to grab wiki page, socket error')
            return None
        except:
            if IS_BAE == False:
                print 'failed to grab wiki page, other error'
            logger.error('failed to grab wiki page, other error')
            return None
        return url_resp.read()


    def grab_page(self, page_url=None):
        user_agent_index = random.randint(0, 8)
        user_agent = user_agents[user_agent_index]

        if page_url == None:
            page_url = self.url_today

        #print page_url
        url_req = urllib2.Request(page_url)
        url_req.add_header('User-agent', user_agent)

        url_content = None
        i = 0
        while(i < 5):
            try:
                url_content = self.grab_page_once(url_req)
            except:
                url_content == None
                logger.error('grab wiki failed once')
                if IS_BAE == False:
                    print 'grab wiki failed once'
            if url_content != None:
                break;
            time.sleep(0.1)
            i = i + 1
            if IS_BAE == True:
                logger.info('get wiki today at %d' % (i))
            else:
                print 'get wiki today at %d' % (i)
        else:
            url_content = 'error happen during grabing wiki today! url=%s' 
            if IS_BAE == True:
                logger.info('failed to get wiki at %s' % page_url)
            else:
                print 'failed to get wiki at %s' % page_url
        return url_content


    def parse_events(self, page):
        soup = BeautifulSoup(page)
        h2_lists = soup.findAll('h2')
        del h2_lists[0]
        del h2_lists[-1]
        for h2_item in h2_lists:
            #print h2_item
            #print h2_item.contents[0] #contents[] is the child tag
            if h2_item.contents[0].name == 'span':
                ul_list = h2_item.findNextSibling("ul")
                #print ul_list
                if type(ul_list) != type(h2_item): # they should be the same type
                    continue
                eventEntry_cnt = 0
                for li_item in ul_list.contents:
                    if type(li_item) == type(ul_list): # they should be the same type
                        #print li_item
                        eventEntry = None
                        li_str = ''
                        max_a_str_len = 0   # to find out the max len of a <a> string in html tag
                        max_a_str_href = ''
                        a_item_cnt = 0
                        for a_item in li_item.contents:
                            #print a_item
                            if type(a_item) != type(li_item): # html text
                                li_str = li_str + a_item.string
                            elif a_item.name == 'a': # html a tag
                                li_str = li_str + a_item.string
                                a_item_cnt = a_item_cnt + 1
                                if a_item_cnt == 1:
                                    continue # this is the first a href, always a year, skipping...
                                if len(a_item.string) > max_a_str_len:
                                    max_a_str_len = len(a_item.string)
                                    max_a_str_href = a_item['href']
                                #print a_item['href']
                                #print a_item.string
                            #print a_item.string
                        li_str = li_str + '\n\n'
                        li_href = URL_WIKI + max_a_str_href[6:]
                        #print li_str
                        #print max_a_str_href
                        #print li_href
                        eventEntry = EventEntry(title=li_str, detail=li_href)
                        self.eventEntries.append(eventEntry)
                        eventEntry_cnt = eventEntry_cnt + 1
                    if (RANK_DEBUG == 1) and (eventEntry_cnt > 2):
                        break
            break # just parse '大事记', skipping others 

        # the ranking method is too slow, maybe we can apply multi-threads for this
        # too damn slow!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        for eventEntry in self.eventEntries:
            event_rank = eventRank.search_eng_rank(eventRank.parse_first_sentence(eventEntry.title))
            eventEntry.rank = event_rank
            if IS_BAE == False:
                print '%s -- %d' % (eventEntry.title[:-2], eventEntry.rank)
            #logger.info('ranking: %s -- %d' % (eventEntry.title[:-2], eventEntry.rank))
        self.eventEntries = sorted(self.eventEntries, key=lambda x:x.rank) # list sorting, lambda
        self.eventEntries.reverse() # we could sort by year finally

        #print '#$!@#$!#%@$%^%^#@%^#%'

        # get event imgs for each event
        # too damn slow!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        #for eventEntry in self.eventEntries[:MAX_EVENT_ENTRIES]: # only process minimun event entries to save time
        for eventEntry in self.eventEntries: # only process minimun event entries to save time
            print eventEntry.detail
            img_url = self.get_event_img(eventEntry.detail)
            eventEntry.img_url = img_url

        #print '#$@#$!#$!#$!#$!#@$!#@$'

        # just for logging
        for eventEntry in self.eventEntries:
            if IS_BAE == True:
                logger.info('------------------------------')
                logger.info('ranking: %s -- %d' % (eventEntry.title[:-2], eventEntry.rank))
                logger.info('%s' % eventEntry.detail)
                logger.info('%s' % eventEntry.img_url)
            else:
                print '-------------------------------'
                print '%s -- %d' % (eventEntry.title[:-2], eventEntry.rank)
                print '%s' % eventEntry.detail
                print '%s' % eventEntry.img_url
				

    def get_event_img(self, event_url):
        #print event_url
        event_page = self.grab_page(event_url)
        soup = BeautifulSoup(event_page)
        img_tag = soup.find('a', attrs={'href':re.compile(r'.*png|jpg$')})
        if img_tag == None:
            return None
        #print img_tag
        #print img_tag['href']
        #print img_tag.contents
        #print img_tag.contents[0]
        #print img_tag.contents[0]['src']
        img_url = img_tag.contents[0]['src']
        if img_url.find('upload') != -1:
            return ('http:' + img_url)
        else:
            return None


def test_crawl_today(month = None, day = None):
    crawltoday = None
    if(month == None) or (day == None):
        crawltoday = CrawlToday()
    else:
        crawltoday = CrawlToday(month, day)
    print "crawling month: %d, day: %d" % (crawltoday.month, crawltoday.day)
    test_page = crawltoday.grab_page()
    #open('%s_%s.html'%(crawltoday.month, crawltoday.day), 'w').write(test_page)
    crawltoday.parse_events(test_page)
    print '**************************************************'
    for item in  crawltoday.eventEntries:
        print '%s -- %d' % (item.title[:-2], item.rank)


def test_crawl_wiki_img(page_url):
    crawltoday = CrawlToday()
    img_url = crawltoday.get_event_img(page_url)
    print img_url


if __name__ == '__main__':
    if len(sys.argv) == 1:
        test_crawl_today()
    elif len(sys.argv) == 3:
        month = int(sys.argv[1])
        day = int(sys.argv[2])
        if ((month > 0) and (month < 13)) and ((day >0) and (day < 32)):
            if (month !=2) or ((month == 2) and (day < 30)):
                test_crawl_today(month, day)
            else:
                print 'month and day should match'
        else:
            print 'month and day should match'
    elif (len(sys.argv) == 4) and (sys.argv[1] == 'test'):
        if sys.argv[2] == '1': # for calling 'test_crawl_wiki_img'
            test_crawl_wiki_img(u'http://zh.wikipedia.org/wiki/%E5%B8%83%E9%B2%81%E5%A1%9E%E5%B0%94')
    else:
        print '''
        Command Paramters Error!
        Command Usage:
        No paramters input will crawl today by default:
            python crawl_today.py 
        or [month] and [day] could be specified to crawl any day you like:
            python crawl_today.py [month] [day]
        '''



CODE_BACKUP_BS4_PARSING=\
'''
                h2_lists = soup.findAll('h2')
                for h2_item in h2_lists:
                    #print h2_item
                    #print h2_item.contents[0] #contents[] is the child tag
                    if h2_item.contents[0].name == 'span':
                        ul_list = h2_item.find_next_sibling("ul")
                        #print ul_list
                        for li_item in ul_list.children:
                            if type(li_item) == type(ul_list): # they should be the same type
                                #print li_item
                                eventEntry = None
                                li_str = ''
                                for a_item in li_item.children:
                                    #print a_item
                                    if a_item.name == 'a': # html a tag
                                        li_str = li_str + a_item.string
                                    elif type(a_item) != type(li_item): # html text
                                        li_str = li_str + a_item.string
                                    #print a_item.string
                                #print li_str
                                li_str = li_str + '\n\n'
                                eventEntry = EventEntry(title=li_str)
                                # give each entry a rank
                                self.eventEntries.append(eventEntry)

'''


