# -*- coding:utf-8 -*-

import multiprocessing
import os
import sys
import time
import Queue
import random
import app_info_crawler
import ip_addr_crawler
import mssql
from logger import Logger
from constant import SUCCESS, FAIL, TIMEOUT

TRACK_ID_LIST = []
ARTIST_ID_LIST = []
GENRE_ID_LIST = []
ADVISORY_ID_LIST = []
ADVISORY_ID_DICT = dict()

CATEGORY_LIST = [
    "游戏",
    "体育",
    "动作游戏",
    "娱乐场游戏",
    "家庭游戏",
    "小游戏",
    "扑克牌游戏",
    "探险游戏",
    "教育游戏",
    "文字游戏",
    "智力游戏",
    "桌面游戏",
    "街机游戏",
    "赛车游戏",
    "音乐",
    "骰子游戏",
    "儿童",
    "教育",
    "购物",
    "摄影与录像",
    "效率",
    "美食佳饮",
    "生活",
    "健康健美",
    "旅游",
    "音乐",
    "体育",
    "商务",
    "新闻",
    "工具",
    "娱乐",
    "社交",
    "报刊杂志",
    "健康、心理与生理",
    "儿童杂志",
    "历史",
    "商务与投资",
    "地方新闻",
    "女士兴趣",
    "娱乐",
    "子女教养与家庭",
    "宠物",
    "家居与园艺",
    "户外与自然",
    "手工艺与爱好",
    "文学杂志与期刊",
    "新娘与婚礼",
    "新闻与政治",
    "旅游与地域",
    "汽车",
    "流行与时尚",
    "烹饪与饮食",
    "电子产品与音响",
    "电影与音乐",
    "电脑与网络",
    "男士兴趣",
    "科学",
    "职业与技能",
    "艺术与摄影",
    "运动与休闲",
    "青少年",
    "财务",
    "参考",
    "导航",
    "医疗",
    "图书",
    "天气",
    "商品指南",
]

LOG = Logger("data_acquisition_logger", "data_acquisition_log", "INFO", "ERROR")

def init_id_list():
    """ init id list """
    try:
        conn = mssql.MsSqlConnection()
        if not conn.connect():
            LOG.error("connect to database failed")
            os._exit(0)
        sql = "select trackId from AppInformation"
        track_id_rst = mssql.select_query(conn, sql)
        for element in track_id_rst:
            TRACK_ID_LIST.append(str(element[0]).strip())
        LOG.info("load track_id list succ")

        sql = "select artistId from Artist"
        artist_id_rst = mssql.select_query(conn, sql)
        for element in artist_id_rst:
            ARTIST_ID_LIST.append(str(element[0]).strip())
        LOG.info("load artist_id list succ")

        sql = "select genreId from Genre"
        genre_id_rst = mssql.select_query(conn, sql)
        for element in genre_id_rst:
            GENRE_ID_LIST.append(str(element[0]).strip())
        LOG.info("Get genre_id list succ")

        sql = "select advisoryId,advisoryContent from Advisory"
        advisory_id_list = mssql.select_query(conn, sql)
        for element in advisory_id_list:
            ADVISORY_ID_DICT[str(element[1]).strip()] = str(element[0]).strip()
            ADVISORY_ID_LIST.append(str(element[0]).strip())
        LOG.info("Get advisroy dict succ")
        conn.disconnect()
    except:
        LOG.error("execute select failed")
        print "execute select failed"
        os._exit(0)

def get_app_info(data_queue, queue_lock):
    """ get app info """
    term_q = Queue.Queue()
    # for category in CATEGORY_LIST:
    #     term_q.put(category)
    for index in range(40, 68):
        term_q.put(CATEGORY_LIST[index])

    LOG.info("get app info begin.")
    while not term_q.empty():
        category = term_q.get()
        status, result = app_info_crawler.get_app_info_by_term(term=category,
                                                               country='cn',
                                                               limit=200)
        if status == TIMEOUT:
            term_q.put(category)
        elif status == SUCCESS:
            if (not result.has_key("resultCount")
                    or not result.has_key("results")):
                continue
            queue_lock.acquire()
            for index in range(int(result["resultCount"])):
                data_queue.put(result["results"][index])
            queue_lock.release()
            print (category.decode('utf-8') + " done " + str(result["resultCount"]) + "; "
                   + str(term_q.qsize()) + " remains")
            LOG.info("get '" + category + "' info succ")
        elif status == FAIL:
            LOG.error("get '" + category + "' info failed")

    queue_lock.acquire()
    data_queue.put("Done")
    queue_lock.release()
    LOG.info("get app info finish.")

def insert_into_artist_table(conn, app_info_data):
    """ insert into artist table """
    if (not app_info_data.has_key("artistId")
            or not app_info_data.has_key("artistName")):
        LOG.error(str(app_info_data["trackId"]) + " has no member named 'artistId' or 'artistName'")
        return False

    artist_id = str(app_info_data["artistId"]).strip()
    artist_name = str(app_info_data["artistName"]).strip().replace("'", "''")
    if artist_id in ARTIST_ID_LIST:
        return True
    sql = ("insert into Artist(artistId,artistName) values ("
           + "'" + artist_id + "', "
           + "'" + artist_name + "'"
           + ")")
    if not mssql.non_select_query(conn, sql):
        LOG.error("insert new artist info failed on track_id=" + str(app_info_data["trackId"]))
        return False
    ARTIST_ID_LIST.append(artist_id)
    LOG.info("insert artist_id=" + artist_id +
             ", artist_name=" + artist_name + " into database")
    return True

def insert_into_genre_table(conn, app_info_data):
    """ insert into genre table """
    if (not app_info_data.has_key("genreIds")
            or not app_info_data.has_key("genres")):
        LOG.error(str(app_info_data["trackId"]) + " has no member named 'genreIds' or 'genres'")
        return False

    for index in range(len(app_info_data["genreIds"])):
        genre_id = str(app_info_data["genreIds"][index]).strip()
        genre = str(app_info_data["genres"][index]).strip().replace("'", "''")
        if genre_id in GENRE_ID_LIST:
            continue
        sql = ("insert into Genre(genreId,genreName) values ("
               + "'" + genre_id + "', "
               + "'" + genre + "'"
               + ")")
        if not mssql.non_select_query(conn, sql):
            LOG.error("insert new genre info failed on track_id=" + str(app_info_data["trackId"]))
            return False
        GENRE_ID_LIST.append(genre_id)
        LOG.info("insert genre_id=" + genre_id +
                 ", genre_name=" + genre + " into database")
    return True

def __gen_rand_id():
    new_id = random.randint(1, 9)*1000 + random.randint(0, 999)
    return str(new_id)

def insert_into_advisory_table(conn, app_info_data):
    """ insert into genre table """
    if not app_info_data.has_key("advisories"):
        LOG.error(str(app_info_data["trackId"]) + " has no member named 'advisroies'")
        return False

    for index in range(len(app_info_data["advisories"])):
        advisory = str(app_info_data["advisories"][index]).strip()
        if ADVISORY_ID_DICT.has_key(advisory):
            continue
        new_id = __gen_rand_id()
        while new_id in ADVISORY_ID_LIST:
            new_id = __gen_rand_id()
        sql = ("insert into Advisory(advisoryId,advisoryContent) values ("
               + "'" + new_id + "', "
               + "'" + advisory + "'"
               + ")")
        if not mssql.non_select_query(conn, sql):
            LOG.error("insert new advisory info failed on track_id="
                      + str(app_info_data["trackId"]))
            return False
        ADVISORY_ID_LIST.append(new_id)
        ADVISORY_ID_DICT[advisory] = new_id
        LOG.info("insert advisory_id=" + new_id +
                 ", advisory_content=" + advisory + " into database")
    return True

def __format_date(key, app_info):
    result = '1970-01-01 00:00:00'
    if app_info.has_key(key):
        result = str(app_info[key]).strip().replace("'", "''")
    return result.strip()[:10] + " " + result.strip()[11:19]

def __format_str(key, default, app_info):
    result = default
    if app_info.has_key(key):
        result = app_info[key]
    return str(result).strip().replace("'", "''")

def __format_list(key, app_info):
    result = ''
    if app_info.has_key(key):
        for element in app_info[key]:
            element = str(element)
        result = ",".join(app_info[key])
    return str(result).strip().replace("'", "''")

def insert_into_appinfo_table(conn, app_info_data):
    """ insert into apple information table """
    try:
        track_id = str(app_info_data["trackId"]).strip().replace("'", "''")
        if track_id in TRACK_ID_LIST:
            return True
        track_name = str(app_info_data["trackName"]).strip().replace("'", "''")
        bundle_id  = str(app_info_data["bundleId"]).strip().replace("'", "''")
        primary_genre_id = str(app_info_data["primaryGenreId"]).strip().replace("'", "''")
        artist_id = str(app_info_data["artistId"]).strip().replace("'", "''")
        keywords = ""
        topic = ""
        release_date = __format_date("releaseDate", app_info_data)
        user_rating_count = __format_str("userRatingCount", '0', app_info_data)
        average_user_rating = __format_str("averageUserRating", '0.0', app_info_data)
        currency = __format_str("currency", 'None', app_info_data)
        formatted_price = __format_str("formattedPrice", 'None', app_info_data)
        price = __format_str("price", '0', app_info_data)
        file_size_bytes = __format_str("fileSizeBytes", '0', app_info_data)
        wrapper_type = __format_str("wrapperType", '', app_info_data)
        is_game_center_enabled = __format_str("isGameCenterEnabled", 'False', app_info_data)
        is_vpp_device_vased_licensing_enabled = __format_str("isVppDeviceBasedLicensingEnabled", 'False', app_info_data)
        minimum_os_version = __format_str("minimumOsVersion", '0.0', app_info_data)
        supported_devices = __format_list("supportedDevices", app_info_data)
        genre_ids = __format_list("genreIds", app_info_data)
        description = __format_str("description", '', app_info_data)
        language_codes_iso2a = __format_list("languageCodesISO2A", app_info_data)
        version = __format_str("version", '', app_info_data)
        current_version_release_date = __format_date("currentVersionReleaseDate", app_info_data)
        user_rating_count_for_current_version = __format_str("userRatingCountForCurrentVersion", '0', app_info_data)
        average_user_rating_for_current_version = __format_str("averageUserRatingForCurrentVersion", '0.0', app_info_data)
        release_notes = __format_str("releaseNotes", '', app_info_data)
        seller_name = __format_str("sellerName", '', app_info_data)
        track_censored_name = __format_str("trackCensoredName", '', app_info_data)
        content_advisory_rating = __format_str("contentAdvisoryRating", '', app_info_data)
        track_content_rating = __format_str("trackContentRating", '', app_info_data)
        advisories = ""
        for advisory in app_info_data["advisories"]:
            advisory = str(advisory).strip()
            advisories += (ADVISORY_ID_DICT[advisory] + ",")
        if len(app_info_data["advisories"]) > 0:
            advisories = advisories[:-1].replace("'", "''")
        sql = ("insert into AppInformation("
               + "trackId,"
               + "trackName,"
               + "bundleId,"
               + "keywords,"
               + "topic,"
               + "releaseDate,"
               + "userRatingCount,"
               + "averageUserRating,"
               + "currency,"
               + "formattedPrice,"
               + "price,"
               + "fileSizeBytes,"
               + "wrapperType,"
               + "isGameCenterEnabled,"
               + "isVppDeviceBasedLicensingEnabled,"
               + "minimumOsVersion,"
               + "supportedDevices,"
               + "primaryGenreId,"
               + "genreIds,"
               + "description,"
               + "languageCodesISO2A,"
               + "version,"
               + "currentVersionReleaseDate,"
               + "userRatingCountForCurrentVersion,"
               + "averageUserRatingForCurrentVersion,"
               + "releaseNotes,"
               + "artistId,"
               + "sellerName,"
               + "trackCensoredName,"
               + "contentAdvisoryRating,"
               + "trackContentRating,"
               + "advisories"
               + ") values ("
               + "'" + track_id + "',"
               + "'" + track_name + "',"
               + "'" + bundle_id + "',"
               + "'" + keywords + "',"
               + "'" + topic + "',"
               + "'" + release_date + "',"
               + "'" + user_rating_count + "',"
               + "'" + average_user_rating + "',"
               + "'" + currency + "',"
               + "'" + formatted_price + "',"
               + "'" + price + "',"
               + "'" + file_size_bytes + "',"
               + "'" + wrapper_type + "',"
               + "'" + is_game_center_enabled + "',"
               + "'" + is_vpp_device_vased_licensing_enabled + "',"
               + "'" + minimum_os_version + "',"
               + "'" + supported_devices + "',"
               + "'" + primary_genre_id + "',"
               + "'" + genre_ids + "',"
               + "'" + description + "',"
               + "'" + language_codes_iso2a + "',"
               + "'" + version + "',"
               + "'" + current_version_release_date + "',"
               + "'" + user_rating_count_for_current_version + "',"
               + "'" + average_user_rating_for_current_version + "',"
               + "'" + release_notes + "',"
               + "'" + artist_id + "',"
               + "'" + seller_name + "',"
               + "'" + track_censored_name + "',"
               + "'" + content_advisory_rating + "',"
               + "'" + track_content_rating + "',"
               + "'" + advisories + "'"
               + ")")
        conn.connect()
        if not mssql.non_select_query(conn, sql):
            LOG.error("insert new app info failed on track_id=" + str(app_info_data["trackId"]))
            return True
        TRACK_ID_LIST.append(track_id)
        LOG.info("insert appinformation with track_id=" + track_id)
    except Exception, excep:
        LOG.error(str(len(TRACK_ID_LIST)))
        LOG.error("insert data into application information failed")
        LOG.error("Exception : " + excep.message)
        return False
    return True

def insert_data_into_database(data_queue, queue_lock):
    """ insert or update data into database """
    init_id_list()
    conn = mssql.MsSqlConnection()
    while True:
        queue_lock.acquire()
        if not data_queue.empty():
            app_info_data = data_queue.get()
            queue_lock.release()
            if app_info_data == "Done":
                break
            conn.connect()
            if (insert_into_artist_table(conn, app_info_data)
                    and insert_into_genre_table(conn, app_info_data)
                    and insert_into_advisory_table(conn, app_info_data)
                    and insert_into_appinfo_table(conn, app_info_data)):
                pass
            conn.disconnect()
        else:
            queue_lock.release()

def main():
    """ main """
    reload(sys)
    sys.setdefaultencoding('utf-8')
    start = time.clock()
    # ip_addr_crawler.get_valid_ip_list()
    app_info_q = multiprocessing.Queue()
    q_lock = multiprocessing.Lock()
    get_app_info(app_info_q, q_lock)
    print "tot_size", app_info_q.qsize()
    insert_data_into_database(app_info_q, q_lock)
    end = time.clock()
    print "execute time : " + str(float(end - start)) + "s"
    print "Done"

if __name__ == "__main__":
    main()
