# -*- coding:utf-8 -*-

'''
# prerequisite:
#   based on Python 2.7

# Author : zhangfan (ninja_zfan@126.com)
# Created : 2016-12-10

# Other
    Any issues or improvements please contact ninja_zfan@126.com
'''

import json
import sys
import urllib2
from logger import Logger

SEARCH_URL_PREFIX = 'https://itunes.apple.com/search?entity=software'
LOOKUP_URL_PREFIX = 'https://itunes.apple.com/lookup?entity=software'

class Spider(object):
    """ encapsulate spider function """
    LOG = Logger("spider_logger", "spider_log", "INFO", "ERROR")
    @staticmethod
    def get_app_info_by_name(app_name, country='cn', limit=1):
        """request information with input restriction and return the data after unparsed."""
        reload(sys)
        sys.setdefaultencoding('utf-8')

        Spider.LOG.info("[spider.py:31 get_app_info_by_name] search app name is '" + app_name + "'")

        app_name_encoded = urllib2.quote(app_name)
        country_encoded = urllib2.quote(country)

        url = (SEARCH_URL_PREFIX
               + '&term=' + app_name_encoded
               + '&country=' + country_encoded
               + '&limit=' + str(limit))

        Spider.LOG.info("[spider.py:41 get_app_info_by_name] search url is '" + url + "'")
        try:
            req = urllib2.urlopen(url)
            rst_str = urllib2.unquote(req.read()).decode('utf-8')
        except urllib2.URLError, excep:
            Spider.LOG.error("[spider.py:46 get_app_info_by_name]"
                             + "get response failed with parameter"
                             + "app_name=" + app_name
                             + "country=" + country
                             + "limit=" + str(limit))
            Spider.LOG.error("[spider.py:51 get_app_info_by_name] Exception : " + excep)
            return None

        rst_data = json.loads(rst_str.replace('\n', ' '))
        Spider.LOG.info("[spider.py:55 get_app_info_by_name] search '" + app_name + "' success")
        return rst_data

    @staticmethod
    def get_app_info_by_id(item_id):
        """request information with input restriction and return the data after unparsed."""
        reload(sys)
        sys.setdefaultencoding('utf-8')

        Spider.LOG.info("[spider.py:64 get_app_info_by_id] search app id is '" + str(item_id) + "'")

        url = LOOKUP_URL_PREFIX + '&id=' + str(item_id)

        Spider.LOG.info("[spider.py:68 get_app_info_by_id] search url is '" + url + "'")
        try:
            req = urllib2.urlopen(url)
            rst_str = urllib2.unquote(req.read()).decode('utf-8')
        except urllib2.URLError, excep:
            Spider.LOG.error("[spider.py:73 get_app_info_by_id] get response failed with parameter"
                             + "item_id=" + str(item_id))
            Spider.LOG.error("[spider.py:75 get_app_info_by_id] Exception : " + excep)
            return None

        rst_data = json.loads(rst_str.replace('\n', ' '))
        Spider.LOG.info("[spider.py:79 get_app_info_by_id] search '" + str(item_id) + "' success")
        return rst_data

def debug_print(data, depth):
    """used in debug mode, print the returned data"""
    space_num = 2 * depth
    if isinstance(data, dict):
        print (space_num * ' ') + '{'
        depth += 1
        space_num = 2 * depth
        for key in data.keys():
            if isinstance(data[key], dict):
                print (space_num * ' ') + str(key) + " :"
                debug_print(data[key], depth)
            elif isinstance(data[key], list):
                print (space_num * ' ') + str(key) + " :"
                print (space_num * ' ') + '['
                debug_print(data[key], depth)
                print (space_num * ' ') + ']'
            else:
                print (space_num * ' ') + str(key) + " : " + str(data[key]) + ','
        depth -= 1
        space_num = 2 * depth
        print (space_num * ' ') + '}'
    elif isinstance(data, list):
        for item in data:
            debug_print(item, depth+1)
    else:
        print (space_num * ' ') + str(data) + ','

def main():
    """ unit testing """
    data = Spider.get_app_info_by_name("支付宝")
    if data:
        debug_print(data, 0)
    else:
        print "return data is None"

    data = Spider.get_app_info_by_id(333206289)
    if data:
        debug_print(data, 0)
    else:
        print "return data is None"

if __name__ == "__main__":
    main()
