# -*- coding:utf-8 -*-

import ConfigParser
import pymssql
from logger import Logger

class MsSql:
    def __init__(self):
        config = ConfigParser.ConfigParser()
        config.read('database.conf')
        self.__host = config.get("MsSql", "host")
        self.__user = config.get("MsSql", "user")
        self.__pwd = config.get("MsSql", "pwd")
        self.__database = config.get("MsSql", "db")
        self.__conn = None

    def __connect(self):
        self.__conn = pymssql.connect(self.__host, self.__user, self.__pwd, self.__database, 5)

    def disconnect(self):
        if self.__conn:
            self.__conn.close()

