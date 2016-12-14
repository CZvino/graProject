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
REVIEWS_URL_PREFIX = 'https://itunes.apple.com/rss/customerreviews/'
REVIEWS_URL_SUFFIX = '/sortby=mostrecent/json?l=cn&cc=cn'

class Spider(object):
    """ encapsulate spider function """
    LOG = Logger("spider_logger", "spider_log", "INFO", "ERROR")
    @staticmethod
    def get_app_info_by_name(app_name, country='cn', limit=1):
        """ request app information with input restriction and return the data after unparsed. """
        reload(sys)
        sys.setdefaultencoding('utf-8')

        Spider.LOG.info("search app name is '" + app_name + "'")

        app_name_encoded = urllib2.quote(app_name)
        country_encoded = urllib2.quote(country)

        url = (SEARCH_URL_PREFIX
               + '&term=' + app_name_encoded
               + '&country=' + country_encoded
               + '&limit=' + str(limit))

        Spider.LOG.info("search url is '" + url + "'")
        try:
            req = urllib2.urlopen(url)
            rst_str = urllib2.unquote(req.read())
        except urllib2.URLError, excep:
            Spider.LOG.error("get response failed with parameter"
                             + " app_name=" + app_name
                             + " country=" + country
                             + " limit=" + str(limit))
            Spider.LOG.error("Exception : " + str(excep))
            return None

        try:
            rst_data = json.loads(rst_str)
        except ValueError, excep:
            Spider.LOG.error("tranfer data by json failed. msg: " + str(excep))
            return None

        Spider.LOG.info("search '" + app_name + "' success")
        return rst_data

    @staticmethod
    def get_app_info_by_id(track_id):
        """ request app information with input restriction and return the data after unparsed. """
        reload(sys)
        sys.setdefaultencoding('utf-8')

        Spider.LOG.info("search app id is '" +str(track_id)+ "'")

        track_id_encoded = urllib2.quote(str(track_id))
        url = LOOKUP_URL_PREFIX + '&id=' + track_id_encoded

        Spider.LOG.info("search url is '" + url + "'")
        try:
            req = urllib2.urlopen(url)
            rst_str = urllib2.unquote(req.read())
        except urllib2.URLError, excep:
            Spider.LOG.error("get response failed with parameter track_id=" + str(track_id))
            Spider.LOG.error("Exception : " + str(excep))
            return None

        try:
            rst_data = json.loads(rst_str)
        except ValueError, excep:
            Spider.LOG.error("tranfer data by json failed. msg: " + str(excep))
            return None

        Spider.LOG.info("search '" + str(track_id) + "' success")
        return rst_data

    @staticmethod
    def get_reviews_by_name(app_name):
        """ request app reviews with input app_name and return the data after unparsed. """
        reload(sys)
        sys.setdefaultencoding('utf-8')

        app_info = Spider.get_app_info_by_name(app_name)
        if (not app_info
                or not app_info.has_key("results")
                or len(app_info["results"]) == 0
                or not app_info["results"][0].has_key("trackId")):
            Spider.LOG.error("get reviews failed with parameter app_name=" + app_name)
            return None

        track_id = app_info["results"][0]["trackId"]
        return Spider.get_reviews_by_id(str(track_id))

    @staticmethod
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

    @staticmethod
    def get_reviews_by_id(track_id):
        """ request app reviews with input track_id and return the data after unparsed. """
        reload(sys)
        sys.setdefaultencoding('utf-8')

        if not track_id.isdigit():
            Spider.LOG.error("bad track_id: " + str(track_id))
            return None

        Spider.LOG.info("getting reviews with track_id=" + str(track_id))

        reviews_list = list()
        track_id_encoded = urllib2.quote(str(track_id))
        for page in range(1, 11):
            page_encoded = urllib2.quote(str(page))
            url = (REVIEWS_URL_PREFIX
                   + "page=" + page_encoded
                   + "/id=" + track_id_encoded
                   + REVIEWS_URL_SUFFIX)
            Spider.LOG.info("getting ")
            try:
                req = urllib2.urlopen(url)
                rst_str = urllib2.unquote(req.read())
            except urllib2.URLError, excep:
                Spider.LOG.error("get response failed with parameter track_id=" + track_id)
                Spider.LOG.error("Exception : " + str(excep))
                continue

            try:
                rst_data = json.loads(rst_str)
            except ValueError, excep:
                Spider.LOG.error("tranfer data by json failed. msg: " + str(excep))
                continue

            if (not rst_data.has_key("feed")
                    or not rst_data["feed"].has_key("entry")):
                Spider.LOG.error("url response has no attribute named 'feed' or 'entry'."
                                 + "The response is:\n    " + rst_str)
                continue

            for review in rst_data["feed"]["entry"]:
                if not Spider.__is_review_data(review):
                    continue
                user_name = review["author"]["name"]["label"]
                rating = review["im:rating"]["label"]
                title = review["title"]["label"]
                content = review["content"]["label"]
                reviews_list.append(
                    {
                        "user_name" : user_name,
                        "rating" : rating,
                        "title" : title,
                        "content" : content
                    }
                )

        return reviews_list

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
    reviews_list = Spider.get_reviews_by_name("支付宝")
    reviews_file = open('reviews.txt', 'w+')
    if reviews_list:
        print "reviews size : " + str(len(reviews_list))
        print >> reviews_file, "reviews size : " + str(len(reviews_list))
        for review in reviews_list:
            print >> reviews_file, "["
            print >> reviews_file, "  user name : " + review["user_name"]
            print >> reviews_file, "  rating    : " + review["rating"]
            print >> reviews_file, "  title     : " + review["title"]
            print >> reviews_file, "  content   : " + review["content"]
            print >> reviews_file, "]"
    else:
        print "sth error durning pulling reviews data"

    app_info_file = open('app_info.txt', 'w+')
    data = Spider.get_app_info_by_name("支付宝")
    if data:
        debug_print(data, 0, app_info_file)
        # pass
    else:
        print "return data is None"

    # data = Spider.get_app_info_by_id(333206289)
    # if data:
        # debug_print(data, 0)
    #     pass
    # else:
    #     print "return data is None"
    print "Done"

if __name__ == "__main__":
    main()
