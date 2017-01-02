# -*- coding:utf-8 -*-

'''
# prerequisite:
#   based on Python 2.7

# Author : zhangfan (ninja_zfan@126.com)
# Created : 2016-12-11

# Other
    Any issues or improvements please contact ninja_zfan@126.com
'''

import logging
import logging.handlers
import os
import sys

LOG_FILE_PATH = os.getcwd()[:os.getcwd().rfind('graProject')+10] + "/log/"

LOG_MAP = {
    "NOTSET"  : logging.NOTSET,
    "DEBUG"    : logging.DEBUG,
    "INFO"     : logging.INFO,
    "WARINING" : logging.WARNING,
    "ERROR"    : logging.ERROR,
    "CRITICAL" : logging.CRITICAL,
}

class Logger(object):
    """ custom class logger """
    __FILE_HANDLER = logging.handlers.RotatingFileHandler(LOG_FILE_PATH + "logger_log",
                                                          mode='a',
                                                          maxBytes=10*1024*1024,
                                                          backupCount=10,
                                                          encoding='UTF-8')
    __FILE_HANDLER.setLevel(logging.ERROR)
    __LOG_FORMAT = logging.Formatter("[%(levelname)s %(asctime)s %(process)d] %(message)s")
    __FILE_HANDLER.setFormatter(__LOG_FORMAT)
    __LOG = logging.getLogger("logger")
    __LOG.addHandler(__FILE_HANDLER)

    __slots__ = ('__logger', '__file_handler', '__console_handler')

    def __init__(self, logger_name, log_file, file_log_level, console_log_level):
        log_path = LOG_FILE_PATH + log_file
        self.config(logger_name, log_path, file_log_level, console_log_level)

    def config(self, logger_name, log_path, file_log_level, console_log_level):
        """ complete basic configuration """
        self.__logger = logging.getLogger(logger_name)
        self.__logger.setLevel(LOG_MAP[file_log_level])
        self.__file_handler = logging.handlers.RotatingFileHandler(log_path,
                                                                   mode='a',
                                                                   maxBytes=100*1024*1024,
                                                                   backupCount=10,
                                                                   encoding='UTF-8')
        self.__file_handler.setLevel(LOG_MAP[file_log_level])
        self.__console_handler = logging.StreamHandler()
        self.__console_handler.setLevel(LOG_MAP[console_log_level])
        log_format = logging.Formatter("[%(levelname)s %(asctime)s %(process)d] %(message)s")
        self.__file_handler.setFormatter(log_format)
        self.__console_handler.setFormatter(log_format)

        self.__logger.addHandler(self.__file_handler)
        self.__logger.addHandler(self.__console_handler)

    def __get_caller_info(self, depth=1):
        """ get information of caller of log funtion, including func name and lineno """
        try:
            file_name = sys._getframe(depth).f_code.co_filename
            file_name = file_name[file_name.rfind('\\')+1:]
            func_name = sys._getframe(depth).f_code.co_name
            line_no = sys._getframe(depth).f_lineno
            return '[' + file_name + ':' + str(line_no) + ' ' + func_name + '] '
        except ValueError, excep:
            Logger.__LOG.error(excep)
            return ""

    def debug(self, msg):
        """ log dubug msg """
        if msg:
            self.__logger.debug(self.__get_caller_info(2) + msg)

    def info(self, msg):
        """ log info msg """
        if msg:
            self.__logger.info(self.__get_caller_info(2) + msg)

    def warning(self, msg):
        """ log warning msg """
        if msg:
            self.__logger.warning(self.__get_caller_info(2) + msg)

    def error(self, msg):
        """ log error msg """
        if msg:
            self.__logger.error(self.__get_caller_info(2) + msg)

    def critical(self, msg):
        """ log fatal msg """
        if msg:
            self.__logger.critical(self.__get_caller_info(2) + msg)

def main():
    """ unit testing """
    # TODO(zhangfan) : unit test

    first_log = Logger("first_logger", "test_log_1", "INFO", "ERROR")

    first_log.debug("test 1 debug")
    first_log.info("test 1 info")
    first_log.warning("test 1 warning")
    first_log.error("test 1 error")
    first_log.critical("test 1 critical")

    second_log = Logger("second_logger", "test_log_2", "ERROR", "CRITICAL")

    second_log.debug("test 2 debug")
    second_log.info("test 2 info")
    second_log.warning("test 2 warning")
    second_log.error("test 2 error")
    second_log.critical("test 2 critical")

if __name__ == "__main__":
    main()
