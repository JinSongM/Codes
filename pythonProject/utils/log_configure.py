# -- coding: utf-8 --
# @Time : 2023/5/11 9:57
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : log_configure.py
# @Software: PyCharm
import os
import sys
import datetime
import logging

path = "./logs/"


class Logger:
    def __init__(self, set_level="debug", name=os.path.split(os.path.splitext(sys.argv[0])[0])[-1], log_name=datetime.datetime.now().strftime("%Y-%m-%d.log"), log_path=path, use_console=True):
        self.logger = logging.getLogger(name)
        if set_level.lower() == "critical":
            self.logger.setLevel(logging.CRITICAL)
        elif set_level.lower() == "error":
            self.logger.setLevel(logging.ERROR)
        elif set_level.lower() == "warning":
            self.logger.setLevel(logging.WARNING)
        elif set_level.lower() == "info":
            self.logger.setLevel(logging.INFO)
        elif set_level.lower() == "debug":
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.NOTSET)
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        log_file_path = os.path.join(log_path, log_name)
        log_handler = logging.FileHandler(log_file_path)
        log_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        self.logger.addHandler(log_handler)
        if use_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
            self.logger.addHandler(console_handler)

    def add_handler(self, hdlr):
        self.logger.addHandler(hdlr)

    def remove_handler(self, hdlr):
        self.logger.removeHandler(hdlr)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        self.logger.log(level, msg, *args, **kwargs)
