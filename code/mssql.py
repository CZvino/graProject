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

    def __connect(self):
        if self.__is_connected:
            self.disconnect()
        self.__conn = pymssql.connect(server=self.__host,
                                      user=self.__user,
                                      password=self.__pwd,
                                      database=self.__database)
        self.__conn.autocommit(True)
        self.__is_connected = True
        MsSqlConnection.LOG.info("database connect successfully."
                                 + " host : " + self.__host
                                 + " user : " + self.__user
                                 + " pwd : " + self.__pwd
                                 + " database : " + self.__database)

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
            self.__connect()
            self.disconnect()
            return True
        except:
            return False

    def get_cursor(self):
        """ get a cursor of connection """
        self.__connect()
        cursor = self.__conn.cursor()
        return cursor


def execute_query(conn, sql):
    """ execute query request. may throw pymssql.DatabaseError because of failed connection """
    if not isinstance(conn, MsSqlConnection):
        raise TypeError("parameter is not a MsSqlConnection object")

    cursor = conn.get_cursor()
    try:
        cursor.execute(sql)
        result_list = cursor.fetchall()
        __LOG.info("execute query sql successfully with sql : " + sql)
    except pymssql.DatabaseError, excep:
        __LOG.error("execute query sql failed with sql : " + sql)
        __LOG.error("Exception : " + excep.message())
        result_list = None

    conn.disconnect()
    return result_list

def execute_non_query(conn, sql):
    """ execute non-query request. may throw pymssql.DatabaseError because of failed connection """
    if not isinstance(conn, MsSqlConnection):
        raise TypeError("parameter is not a MsSqlConnection object")

    cursor = conn.get_cursor()
    try:
        MsSqlConnection.WRITELOCK.acquire()
        cursor.execute(sql)
        MsSqlConnection.WRITELOCK.release()
        __LOG.info("execute non-query sql successfully with sql : " + sql)
    except pymssql.DatabaseError, excep:
        __LOG.error("execute non-query sql failed with sql : " + sql)
        __LOG.error("Exception : " + excep.message())

    conn.disconnect()

def main():
    conn = MsSqlConnection()

if __name__ == "__main__":
    main()

