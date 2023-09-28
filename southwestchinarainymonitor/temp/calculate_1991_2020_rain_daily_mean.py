#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
   @Project   ：Wiztek.DataService.MountainTorrent.Py
   
   @File      ：calculate_1991_2020_rain_daily_mean.py
   
   @Author    ：yhaoxian
   
   @Date      ：2022/2/17 15:54 
   
   @Describe  : 梅双丽老师
                统计西南雨季日均降水  数据时间  1991-2020年
   
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from utils import log_configure as log
from netCDF4 import Dataset
from utils import LatLonData as lld
from multiprocessing import Pool

logger = log.Logger(log_path="../log/01")

data_path = "E:/09.ProjectData/05.products/EAR5/tp/{}/{}"
year_mean_path = "file/year/his_area_daily_mean_{}.txt"
output_path = "../file/his_area_daily_mean_1991-2020.txt"


def read_station_information():
    """

    Returns:

    """
    f = open("../file/southwest_stations_info.txt", "r", encoding="utf8")
    lines = f.read().split("\n")
    sta_id = []
    lons = []
    lats = []
    for line in lines:
        arr_info = line.split("\t")
        if len(arr_info) < 3:
            continue
        sta_id.append(arr_info[0])
        lats.append(int(arr_info[1]) // 100 + (int(arr_info[1]) % 100) / 60)
        lons.append(int(arr_info[2]) // 100 + (int(arr_info[2]) % 100) / 60)
    return sta_id, lons, lats


def calculate_30_year_daily_rain_mean():
    """

    :return:
    """
    mean_data = {}
    data_mean = {}
    for year in range(1991, 2021):
        file_path = year_mean_path.format(year)
        dmr = pd.read_csv(file_path, header=0, delimiter='\t', names=['Month', 'Day', 'Rain'])
        for value in dmr.values:
            key = "{0:02d}{1:02d}".format(int(value[0]), int(value[1]))
            if key in mean_data.keys():
                mean_data.get(key).append(value[2])
            else:
                arr = [value[2]]
                mean_data[key] = arr
    print(mean_data)
    result = ["Month\tDay\tRain\n"]
    for key in mean_data.keys():
        value = np.mean(mean_data.get(key))
        value = float('%.1f' % value)
        data_mean[key] = value
        result.append(key[0:2] + "\t" + key[2:4] + "\t" + str(value) + "\n")
    print(data_mean)
    f = open(output_path, "w")
    f.writelines(result)
    f.close()


def process(date_start: datetime, date_end: datetime):
    sta_id, lons, lats = read_station_information()
    temp = 0

    lat_lon_data = lld.LatLonData(0, 359.75, 90, -90, 0.25, -0.25, 1440, 721)

    file_date = {}

    temp_time = date_start

    while temp_time < date_end:
        temp += 1
        year = temp_time.year
        key = temp_time.strftime("%m%d")

        data_total = np.zeros((721, 1440), dtype=float)

        time_yesterday = temp_time - timedelta(days=1)
        file_name_yesterday = time_yesterday.strftime("%Y%m%d") + ".nc"
        file_path_yesterday = data_path.format(time_yesterday.year, file_name_yesterday)

        dataset_yesterday = Dataset(file_path_yesterday, "r", format='NETCDF4')
        tp_yesterday_data = dataset_yesterday.variables["tp"]

        if "expver" in dataset_yesterday.variables:
            for i in range(20, 24):
                data_total += np.reshape(tp_yesterday_data[i, 1, :, :], (721, 1440)) * 1000
        else:
            for i in range(20, 24):
                data_total += np.reshape(tp_yesterday_data[i, :, :], (721, 1440)) * 1000

        file_name = temp_time.strftime("%Y%m%d") + ".nc"
        file_path = data_path.format(year, file_name)

        logger.info("开始处理：" + temp_time.strftime("%Y-%m-%d %H:%M:%S") + " 路径：" + file_path)

        dataset = Dataset(file_path, "r", format='NETCDF4')
        tp_data = dataset.variables["tp"]

        if "expver" in dataset.variables:
            for i in range(0, 7):
                data_total += np.reshape(tp_data[i, 0, :, :], (721, 1440)) * 1000
            for i in range(7, 20):
                data_total += np.reshape(tp_data[i, 1, :, :], (721, 1440)) * 1000
        else:
            for i in range(0, 20):
                data_total += np.reshape(tp_data[i, :, :], (721, 1440)) * 1000

        lat_lon_data.data = data_total

        tp_day_total = 0
        for i in range(0, len(sta_id)):
            tp_day_total += lat_lon_data.get_data(lats[i], lons[i], bilinear=False)

        tp_avg = tp_day_total / len(sta_id)

        if key in file_date.keys():
            file_date.get(key).append(tp_avg)
        else:
            file_date[key] = []
            file_date.get(key).append(tp_avg)

        temp_time = temp_time + timedelta(days=1)

    buffer = ["Month\tDay\tRain\n"]
    for key in file_date.keys():
        mean_data = np.mean(file_date.get(key))
        value = float('%.1f' % mean_data)
        buffer.append(key[0:2] + "\t" + key[2:4] + "\t" + str(value) + "\n")

    f = open("./file/year/his_area_daily_mean_{}.txt".format(date_start.strftime("%Y")), "w")
    f.writelines(buffer)
    f.close()


if __name__ == '__main__':
    ps = Pool(1)
    for date_year in range(1991, 2021):
        ps.apply_async(process, args=(datetime(date_year, 1, 1), datetime(date_year + 1, 1, 1)))
    ps.close()
    ps.join()

    # calculate_30_year_daily_rain_mean()
