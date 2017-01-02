# -*- coding:utf-8 -*-

import ConfigParser
import multiprocessing
import pymssql
from logger import Logger
from constant import FILEPATH

__LOG = Logger("database_handler_logger", "database_handler_log", "INFO", "ERROR")

class MsSqlConnection(object):
    """ class of database connection """
    WRITELOCK = multiprocessing.Lock()
    LOG = Logger("database_handler_logger", "database_handler_log", "INFO", "ERROR")
    def __init__(self):
        config = ConfigParser.ConfigParser()
        config.read(FILEPATH + '/config/database.conf')
        self.__host = config.get("MsSql", "host")
        self.__user = config.get("MsSql", "user")
        self.__pwd = config.get("MsSql", "pwd")
        self.__database = config.get("MsSql", "db")
        self.__conn = None
        self.__is_connected = False

    def connect(self):
        """ connect to database """
        if self.__is_connected:
            self.disconnect()
        try:
            self.__conn = pymssql.connect(server=self.__host,
                                          user=self.__user,
                                          password=self.__pwd,
                                          database=self.__database)
        except pymssql.DatabaseError, excep:
            MsSqlConnection.LOG.error("database connect failed."
                                      + " host : " + self.__host
                                      + " user : " + self.__user
                                      + " pwd : " + self.__pwd
                                      + " database : " + self.__database)
            return False
        self.__conn.autocommit(True)
        self.__is_connected = True
        MsSqlConnection.LOG.info("database connect successfully."
                                 + " host : " + self.__host
                                 + " user : " + self.__user
                                 + " pwd : " + self.__pwd
                                 + " database : " + self.__database)
        return True

    def disconnect(self):
        """ disconnect from database """
        if isinstance(self.__conn, pymssql.Connection):
            self.__conn.close()
        del self.__conn
        self.__conn = None
        self.__is_connected = False
        MsSqlConnection.LOG.info("database disconnect successfully."
                                 + " host : " + self.__host
                                 + " user : " + self.__user
                                 + " pwd : " + self.__pwd
                                 + " database : " + self.__database)

    def verify_connection(self):
        """ verify connection. usually use for test """
        try:
            if self.__host == '':
                return False
            if not self.connect():
                return False
            self.disconnect()
            return True
        except:
            return False

    def get_cursor(self):
        """ get a cursor of connection """
        if not self.__is_connected:
            raise pymssql.DatabaseError("haven't connectted to the database")
        cursor = self.__conn.cursor()
        return cursor


def select_query(conn, sql):
    """ execute query request. may throw pymssql.DatabaseError because of failed connection """
    if not isinstance(conn, MsSqlConnection):
        raise TypeError("parameter is not a MsSqlConnection object")
    if "select" not in sql:
        raise TypeError("sql is not a select query")

    cursor = conn.get_cursor()
    try:
        cursor.execute(sql)
        result_list = cursor.fetchall()
        __LOG.info("execute query sql successfully with sql : " + sql)
    except pymssql.DatabaseError, excep:
        __LOG.error("execute query sql failed with sql : " + sql)
        __LOG.error("Exception : " + excep.message())
        result_list = None
    return result_list

def non_select_query(conn, sql):
    """ execute non-query request. may throw pymssql.DatabaseError because of failed connection """
    if not isinstance(conn, MsSqlConnection):
        raise TypeError("parameter is not a MsSqlConnection object")
    if "insert" not in sql and "update" not in sql and "delete" not in sql:
        raise TypeError("sql format is not acceptable")

    cursor = conn.get_cursor()
    try:
        MsSqlConnection.WRITELOCK.acquire()
        cursor.execute(sql)
        MsSqlConnection.WRITELOCK.release()
        __LOG.info("execute non-query sql successfully with sql : " + sql)
    except pymssql.DatabaseError, excep:
        __LOG.error("execute non-query sql failed with sql : " + sql)
        __LOG.error("Exception : " + excep.message())
        return False
    return True

def main():
    conn = MsSqlConnection()
    conn.connect()
    sql = "select track_id from AppleInformation"
    rst_list = select_query(conn, sql)
    if not rst_list:
        print "ERROR"
    else:
        for track_id in rst_list:
            print track_id

if __name__ == "__main__":
    main()

