# -*- coding:utf-8 -*-
'''
# prerequisite:
#   based on Python 2.7

# Author : zhangfan (ninja_zfan@126.com)
# Created : 2016-12-21

# Other
    Any issues or improvements please contact ninja_zfan@126.com
'''

import gzip
import multiprocessing
import random
import os
import sys
import StringIO
import socket
import time
import urllib
import urllib2
from logger import Logger
from bs4 import BeautifulSoup
from constant import *

__LOG = Logger("ip_addr_crawler_logger", "ip_addr_crawler_log", "INFO", "ERROR")

def __check_ip_is_valid(proxy_info):
    socket.setdefaulttimeout(5)
    proxy = {proxy_info[0]:proxy_info[0]+'://'+proxy_info[1]+':'+proxy_info[2]}

    app_info_url = "https://itunes.apple.com/lookup?id=333206289"
    reviews_url = "https://itunes.apple.com/cn/rss/customerreviews/id=333206289/sortby=mostrecent/json"
    try:
        urllib.urlopen(app_info_url, proxies=proxy).read()
        urllib.urlopen(reviews_url, proxies=proxy).read()
    except (IOError, urllib2.URLError):
        __LOG.info(proxy_info[0] + "://"
                   + proxy_info[1] + ":"
                   + proxy_info[2] + " connect time out")
        return False, ':'.join(proxy_info)
    except Exception, excep:
        __LOG.error("Unknown Exception : " + excep.message)

    __LOG.info(proxy_info[0] + "://" + proxy_info[1] + ":" + proxy_info[2] + " connect successful")
    return True, ':'.join(proxy_info)

def __gzip_decode(data):
    html_code = ""
    try:
        compressed_stream = StringIO.StringIO(data)
        gzipper = gzip.GzipFile(fileobj=compressed_stream)
        html_code = gzipper.read()
        return True, html_code
    except IOError, excep:
        __LOG.error("Unzip data failed : " + excep.message)
    except Exception, excep:
        __LOG.error("Unknown Exception : " + excep.message)

    return False, html_code

def __get_whole_ip_list():
    reload(sys)
    sys.setdefaultencoding('utf-8')

    start_time = time.clock()
    ip_list = []
    for url_prefix in [IP_INLAND_URL_PREFIX, IP_FOREIGH_URL_PREFIX]:
        for page in range(1, 11):
            url = url_prefix + urllib2.quote(str(page))
            headers = {
                'User-Agent' : random.choice(USER_AGENT_LIST),
                'Host' : 'www.kuaidaili.com',
                'Referer' : url,
                'Accept-Encoding' : 'gzip,deflate'
            }
            __LOG.info("Request ip_list from url='" + url + "'")
            req = urllib2.Request(url, headers=headers)
            try:
                request = urllib2.urlopen(req)
                rtn_data = request.read()
            except urllib2.URLError, excep:
                print excep
                __LOG.error("get html code failed from url='" + url + "'")
                continue
            except Exception, excep:
                __LOG.error("Unknown Exception : " + excep.message)
                continue

            excute_status, html_code = __gzip_decode(rtn_data)
            if not excute_status:
                continue

            soup = BeautifulSoup(html_code, "html.parser")
            ip_struct_list = soup.find_all('tr')
            del ip_struct_list[0]
            for ip_struct in ip_struct_list:
                tds = ip_struct.find_all('td')
                if (tds[2].get_text().strip() != "高匿名"
                        or (tds[3].get_text().strip() != "HTTP"
                            and tds[3].get_text().strip() != "HTTPS")):
                    continue
                ip_list.append(
                    [
                        tds[3].get_text().strip().lower(),
                        tds[0].get_text().strip(),
                        tds[1].get_text().strip()
                    ]
                )
            # 短时间多次访问会失败
            time.sleep(1)

    end_time = time.clock()
    __LOG.info("get whole ip list (size : "
               + str(len(ip_list))
               + ") successful. excute time : "
               + str(float(end_time - start_time)) + "s")
    return ip_list

def get_valid_ip_list():
    """ get valid ip list """
    multiprocessing.freeze_support()
    whole_ip_list = __get_whole_ip_list()
    valid_ip_list = []

    __LOG.info("start multi process to check ip is valid or not")
    pool = multiprocessing.Pool(processes=50)
    result_list = []
    start = time.clock()
    for ip in whole_ip_list:
        result_list.append(pool.apply_async(__check_ip_is_valid, (ip, )))
    pool.close()
    pool.join()
    end = time.clock()
    __LOG.info("processes all done. excute time : " + str(float(end - start)) + "s")
    for process in result_list:
        try:
            result = process.get()
            if not result[0]:
                __LOG.info(result[1] + " is not valid")
                continue
            valid_ip_list.append(result[1])
        except TypeError:
            __LOG.error("find one process failed")

    __LOG.info(str(len(valid_ip_list)) + " is available")

    file_path = FILEPATH + "/data/valid_ip_list"
    valid_ip_file = open(file_path, 'w+')
    for valid_ip in valid_ip_list:
        print >> valid_ip_file, valid_ip

def main():
    """ unit testing """
    get_valid_ip_list()
    print "Done"

if __name__ == "__main__":
    main()
