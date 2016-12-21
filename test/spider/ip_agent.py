# -*- coding:utf-8 -*-

import fileinput
import multiprocessing
import random
import time
import urllib2

ip_list = []
for line in fileinput.input('data/valid_ip_list'):
    mode, ip, port = line.strip().split(':')
    ip_list.append({mode : mode + '://' + ip + ':' + port})

url = "https://itunes.apple.com/lookup?id=333206289"

def run():
    try:
        ip = random.choice(ip_list)
        proxy = urllib2.ProxyHandler(ip)
        opener = urllib2.build_opener(proxy)
        reponse = opener.open(url).read()
        print reponse
    except Exception, e:
        print e.message

def main():
    multiprocessing.freeze_support()
    pool = multiprocessing.Pool(processes=20)

    for i in range(50):
        pool.apply_async(run, )
    pool.close()
    pool.join()

if __name__ == "__main__":
    start = time.clock()
    main()
    end = time.clock()
    print "Done ", str(end-start), "s" 
