#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import datetime
import colorlog

# 日志配色
log_colors_config = {
    "DEBUG": "cyan",
    "INFO": "white",
    "WARNING": "yellow",
    "ERROR": "blue",
    "CRITICAL": "red",
}

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

console_Bool = True

if console_Bool:
    console_handler = colorlog.StreamHandler()
    formatter = colorlog.ColoredFormatter("%(log_color)s[%(asctime)s] [%(processName)s] [%(process)d] [%(levelname)s] [%(pathname)s:%(lineno)d] [%(funcName)s] - %(message)s", log_colors=log_colors_config)  # 日志输出格式
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# 文件日志
log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")

if not os.path.exists(log_path):
    os.makedirs(log_path)

time_str = datetime.datetime.now().strftime("%Y-%m-%d")
log_name = "{time}.log".format(time=time_str)

log_file_path = os.path.join(log_path, log_name)
log_handler = logging.FileHandler(log_file_path, encoding="utf-8")

file_formatter = "[%(asctime)s] [%(processName)s] [%(process)d] [%(levelname)s] [%(pathname)s:%(lineno)d] [%(funcName)s] - %(message)s"

log_handler.setFormatter(logging.Formatter(file_formatter))
logger.addHandler(log_handler)
