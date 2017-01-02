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
import multiprocessing
import os
import random
import socket
import sys
import urllib2
from ssl import SSLError
from constant import *
from logger import Logger

__LOCK = multiprocessing.Lock()
__IS_INIT = False
__IP_LIST = []
__LOG = Logger("app_info_crawler_logger", "app_info_crawler_log", "INFO", "ERROR")

def __init_ip_list():
    local_ip = socket.gethostbyname(socket.gethostname())
    del __IP_LIST[:]
    __IP_LIST.append({'http':'http://'+local_ip+':8080'})
    if not os.path.exists(FILEPATH + "/data/valid_ip_list"):
        return
    ip_file = open(FILEPATH + "/data/valid_ip_list")
    line = ip_file.readline()
    while line:
        mode, ip, port = line.strip().split(':')
        __IP_LIST.append({mode : mode + '://' + ip + ':' + port})
        line = ip_file.readline()

def __build_opener():
    ip = random.choice(__IP_LIST)
    proxy = urllib2.ProxyHandler(ip)
    opener = urllib2.build_opener(proxy)
    return opener

def get_app_info_by_term(term, country='cn', limit=1):
    """ request app information with input restriction and return the data after unparsed. """
    reload(sys)
    sys.setdefaultencoding('utf-8')
    __LOCK.acquire()
    global __IS_INIT
    if not __IS_INIT:
        __init_ip_list()
        __IS_INIT = True
        __LOG.info("init ip list successfully")
    __LOCK.release()

    __LOG.info("search app name is '" + term + "'")

    term_encoded = urllib2.quote(term)
    country_encoded = urllib2.quote(country)

    url = (SEARCH_URL_PREFIX
           + '&term=' + term_encoded
           + '&country=' + country_encoded
           + '&limit=' + str(limit))

    __LOG.info("search url is '" + url + "'")
    try:
        opener = __build_opener()
        json_rst = opener.open(url, timeout=5)
        rst_str = urllib2.unquote(json_rst.read())
    except urllib2.URLError, excep:
        __LOG.error("get response failed with parameter"
                    + " term=" + term
                    + " country=" + country
                    + " limit=" + str(limit))
        __LOG.error("Exception : " + str(excep))
        return FAIL, None
    except SSLError, excep:
        __LOG.warning("get response timeout with parameter"
                      + " term=" + term
                      + " country=" + country
                      + " limit=" + str(limit))
        __LOG.warning("Exception : " + str(excep))
        return TIMEOUT, None

    try:
        rst_data = json.loads(rst_str)
    except ValueError, excep:
        __LOG.error("tranfer data by json failed. msg: " + str(excep))
        return FAIL, None

    __LOG.info("search '" + term + "' success")
    return SUCCESS, rst_data

def get_app_info_by_id(track_id):
    """ request app information with input restriction and return the data after unparsed. """
    reload(sys)
    sys.setdefaultencoding('utf-8')

    __LOCK.acquire()
    global __IS_INIT
    if not __IS_INIT:
        __init_ip_list()
        __IS_INIT = True
        __LOG.info("init ip list successfully")
    __LOCK.release()

    __LOG.info("search app id is '" +str(track_id)+ "'")

    track_id_encoded = urllib2.quote(str(track_id))
    url = LOOKUP_URL_PREFIX + '&id=' + track_id_encoded

    __LOG.info("search url is '" + url + "'")
    try:
        opener = __build_opener()
        json_rst = opener.open(url, timeout=5)
        rst_str = urllib2.unquote(json_rst.read())
    except urllib2.URLError, excep:
        __LOG.error("get response failed with parameter track_id=" + str(track_id))
        __LOG.error("Exception : " + str(excep))
        return FAIL, None
    except SSLError, excep:
        __LOG.warning("get response timeout with parameter track_id=" + str(track_id))
        __LOG.warning("Exception : " + str(excep))
        return TIMEOUT, None

    try:
        rst_data = json.loads(rst_str)
    except ValueError, excep:
        __LOG.error("tranfer data by json failed. msg: " + str(excep))
        __LOG.error(rst_str)
        return FAIL, None

    __LOG.info("search '" + str(track_id) + "' success")
    return SUCCESS, rst_data

def get_reviews_by_name(app_name):
    """ request app reviews with input app_name and return the data after unparsed. """
    reload(sys)
    sys.setdefaultencoding('utf-8')

    __LOCK.acquire()
    global __IS_INIT
    if not __IS_INIT:
        __init_ip_list()
        __IS_INIT = True
        __LOG.info("init ip list successfully")
    __LOCK.release()

    flag, app_info = get_app_info_by_term(app_name)
    if flag == TIMEOUT:
        return TIMEOUT, None
    if (not app_info
            or not app_info.has_key("results")
            or len(app_info["results"]) == 0
            or not app_info["results"][0].has_key("trackId")):
        __LOG.error("get reviews failed with parameter app_name=" + app_name)
        return FAIL, None

    track_id = app_info["results"][0]["trackId"]
    return get_reviews_by_id(str(track_id))

def __is_review_data(review):
    """ judge the data whether is a review data or not """
    if (not review.has_key("author")
            or not review["author"].has_key("name")
            or not review["author"]["name"].has_key("label")):
        return False
    if (not review.has_key("im:rating")
            or not review["im:rating"].has_key("label")):
        return False
    if (not review.has_key("title")
            or not review["title"].has_key("label")):
        return False
    if (not review.has_key("content")
            or not review["content"].has_key("label")
            or not review["content"].has_key("attributes")
            or not review["content"]["attributes"].has_key("type")
            or review["content"]["attributes"]["type"] != "text"):
        return False
    return True

def get_reviews_by_id(track_id):
    """ request app reviews with input track_id and return the data after unparsed. """
    reload(sys)
    sys.setdefaultencoding('utf-8')

    __LOCK.acquire()
    global __IS_INIT
    if not __IS_INIT:
        __init_ip_list()
        __IS_INIT = True
        __LOG.info("init ip list successfully")
    __LOCK.release()

    if not track_id.isdigit():
        __LOG.error("bad track_id: " + str(track_id))
        return FAIL, None

    __LOG.info("getting reviews with track_id=" + str(track_id))

    reviews_list = list()
    track_id_encoded = urllib2.quote(str(track_id))
    opener = __build_opener()
    for page in range(1, 11):
        page_encoded = urllib2.quote(str(page))
        url = (REVIEWS_URL_PREFIX
               + "page=" + page_encoded
               + "/id=" + track_id_encoded
               + REVIEWS_URL_SUFFIX)

        __LOG.info("getting page=" + str(page) + " with url='" + url + "'")

        try:
            rst_str = urllib2.unquote(opener.open(url).read())
            # NOTE(zhangfan) : uncomment next line to output return string
            # print rst_str
        except urllib2.URLError, excep:
            __LOG.error("get response failed with parameter track_id=" + track_id)
            __LOG.error("Exception : " + str(excep))
            continue

        try:
            rst_data = json.loads(rst_str)
        except ValueError, excep:
            __LOG.error("tranfer data by json failed. msg: " + str(excep))
            __LOG.error(rst_str)
            continue

        if (not rst_data.has_key("feed")
                or not rst_data["feed"].has_key("entry")):
            __LOG.error("url response has no attribute named 'feed' or 'entry'."
                        + "The response is:\n    " + rst_str)
            continue

        for review in rst_data["feed"]["entry"]:
            if not __is_review_data(review):
                continue
            reviews_list.append(review)

    __LOG.info("get reviews of '" + str(track_id) + "' success")
    return SUCCESS, reviews_list

def debug_print(data, depth, app_info_file):
    """ used in debug mode, print the returned data """
    space_num = 2 * depth
    if isinstance(data, dict):
        print >> app_info_file, (space_num * ' ') + '{'
        depth += 1
        space_num = 2 * depth
        for key in data.keys():
            if isinstance(data[key], dict):
                print >> app_info_file, (space_num * ' ') + str(key) + " :"
                debug_print(data[key], depth, app_info_file)
            elif isinstance(data[key], list):
                print >> app_info_file, (space_num * ' ') + str(key) + " :"
                print >> app_info_file, (space_num * ' ') + '['
                debug_print(data[key], depth, app_info_file)
                print >> app_info_file, (space_num * ' ') + ']'
            else:
                print >> app_info_file, (space_num * ' ') + str(key) + " : " + str(data[key]) + ','
        depth -= 1
        space_num = 2 * depth
        print >> app_info_file, (space_num * ' ') + '}'
    elif isinstance(data, list):
        for item in data:
            debug_print(item, depth+1, app_info_file)
    else:
        print >> app_info_file, (space_num * ' ') + str(data) + ','

def main():
    """ unit testing """
    # TODO(zhangfan) : unit test

    file_path_prefix = os.getcwd()[:os.getcwd().rfind('graProject')+10] + "/result/"

    flag, reviews_list = get_reviews_by_name("支付宝")

    reviews_file = open(file_path_prefix+'reviews_list.txt', 'w+')
    if reviews_list:
        print "reviews size : " + str(len(reviews_list))
        print >> reviews_file, "reviews size : " + str(len(reviews_list))
        for review in reviews_list:
            print >> reviews_file, review
    else:
        print "sth error during pulling reviews data"

    app_info_file = open(file_path_prefix+'app_info.txt', 'w+')
    flag, data = get_app_info_by_term("支付宝")
    if data:
        debug_print(data, 0, app_info_file)
        # pass
    else:
        print "return data is None"

    # data = get_app_info_by_id(333206289)
    # if data:
        # debug_print(data, 0)
    #     pass
    # else:
    #     print "return data is None"
    print "Done"

if __name__ == "__main__":
    main()
