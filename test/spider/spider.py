# -*- coding:utf-8 -*-

'''
# prerequisite:
#   based on Python 2.7

# Author : zhangfan (ninja_zfan@126.com)
# Created : 2016-12-10

# Other
    Any issues or improvements please contact ninja_zfan@126.com
'''

import logging
import json
import sys
import urllib2

URL_PREFIX = 'https://itunes.apple.com/search?entity=software'

def get_app_info_by_name(app_name, country='cn', limit=1):
    """request information with input restriction and return the data after unparsed."""
    reload(sys)
    sys.setdefaultencoding('utf-8')

    logging.info("search app name is '" + app_name + "'")

    app_name_encoded = urllib2.quote(app_name)
    country_encoded = urllib2.quote(country)

    url = (URL_PREFIX
           + '&term=' + app_name_encoded
           + '&country=' + country_encoded
           + '&limit=' + str(limit))

    logging.info("search url is '" + url + "'")
    try:
        req = urllib2.urlopen(url)
        rst_str = urllib2.unquote(req.read()).decode('utf-8')
    except urllib2.URLError, excep:
        logging.error("get response failed with parameter"
                      + "app_name=" + app_name
                      + "country=" + country
                      + "limit=" + str(limit))
        logging.error("Exception : " + excep)
        return None

    rst_data = json.loads(rst_str.replace('\n', ' '))
    logging.info("search '" + app_name + "' success")
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
    """debug mode main function"""
    data = get_app_info_by_name("支付宝")
    if data:
        debug_print(data, 0)
    else:
        print "return data is None"

if __name__ == "__main__":
    main()
