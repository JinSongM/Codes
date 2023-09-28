#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
   @Project   ：Wiztek.DataService.MountainTorrent.Py
   
   @File      ：calculate_rain_rolling_5days_mean.py
   
   @Author    ：yhaoxian
   
   @Date      ：2022/2/17 15:55 
   
   @Describe  : 
   
"""

from datetime import datetime, timedelta
import pandas as pd
from utils import log_configure as log

logger = log.Logger(log_path="../log/02")

daily_rain_avg_path = "../file/his_area_daily_mean_08_1991-2020.txt"


def read_tp_daily_mean():
    """
    读取1991-2020年日平均降水数据，并返回
    Returns:
        mean_data  dict

    """
    mean_data = {}
    try:
        dmr = pd.read_csv(daily_rain_avg_path, header=0, delimiter='\t', names=['month', 'day', 'rain'])
        for value in dmr.values:
            key = "{0:02d}{1:02d}".format(int(value[0]), int(value[1]))
            mean_data[key] = value[2]
    except Exception as ex:
        logger.error(ex)

    return mean_data


def calculate_5days_rolling_avg():
    """
    计算5天滑动平均
    :return:
    """
    date_start = datetime(2020, 1, 5)
    date_end = datetime(2021, 1, 1)
    daily_mean = read_tp_daily_mean()
    buffer = ["Month\tDay\tRain\n"]
    while date_start < date_end:
        key = date_start.strftime("%m%d")
        five_days_total = 0
        for i in range(4, -1, -1):
            key_tmp = (date_start - timedelta(days=i)).strftime("%m%d")
            five_days_total += daily_mean.get(key_tmp)
        avg_value = five_days_total / 5
        value = float('%.1f' % avg_value)
        buffer.append(key[0:2] + "\t" + key[2:4] + "\t" + str(value) + "\n")
        date_start = date_start + timedelta(days=1)
    f = open("../file/his_area_rolling_5_mean_1991_2020.txt", "w")
    f.writelines(buffer)
    f.close()


def calculate_5_10_month_avg():
    """
    计算5-10月侯降水量的气候平均值
    :return:
    """
    daily_mean = read_tp_daily_mean()
    rain_total = 0
    for month in range(5, 11):
        for day in range(1, 31):
            key = datetime(2020, month, day).strftime("%m%d")
            rain_total += daily_mean.get(key)
    rain_avg = rain_total / 36
    value = float('%.1f' % rain_avg)
    buffer = "5_10_avg\t" + str(value)
    return buffer


def calculate_1_12_month_avg():
    """
    计算1-12月侯降水量的气候平均值
    :return:
    """
    daily_mean = read_tp_daily_mean()
    rain_total = 0
    for month in range(1, 13):
        for day in range(1, 31):
            if month == 2 and day > 29:
                continue
            key = datetime(2020, month, day).strftime("%m%d")
            rain_total += daily_mean.get(key)
    rain_avg = rain_total / 72
    value = float('%.1f' % rain_avg)
    buffer = "1_12_avg\t" + str(value)
    return buffer


if __name__ == '__main__':
    # calculate_5days_rolling_avg()
    a = calculate_5_10_month_avg()
    b = calculate_1_12_month_avg()
    print(a,b)
