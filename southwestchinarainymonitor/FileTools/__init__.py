#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
   @Project   ：Wiztek.MountainTorrent.SouthWestChina.Py 
   
   @File      ：__init__.py.py
   
   @Author    ：yhaoxian
   
   @Date      ：2022/3/23 19:53 
   
   @Describe  : 
   
"""


def read_station_information(file_path: str):
    """
    读取西南站点信息  ./file/rain_stations_history.txt
    Args:
        file_path:  文件路径

    Returns:
        sta_ids       站点号
        lons          经度
        lats          纬度

    """
    try:
        ids, lons, lats = [], [], []
        file = open(file_path)
        file_datas = file.readlines()
        file_datas = sorted(file_datas)
        file.close()
        for his_sta_data in file_datas:
            sta_info_arr = his_sta_data.split()
            if len(sta_info_arr) < 3:
                continue
            ids.append(sta_info_arr[0])
            lats.append(int(sta_info_arr[1]) // 100 + (int(sta_info_arr[1]) % 100) / 60)
            lons.append(int(sta_info_arr[2]) // 100 + (int(sta_info_arr[2]) % 100) / 60)
        return ids, lons, lats
    except Exception as ex:
        print(ex)
        return None, None, None


def read_station_information_dict(file_path: str):
    """
    读取西南站点信息  ./file/rain_stations_history.txt
    Args:
        file_path:  文件路径

    Returns:
        sta_ids       站点号
        lons          经度
        lats          纬度

    """
    try:
        sta_dict = {}
        file = open(file_path)
        file_datas = file.readlines()
        file_datas = sorted(file_datas)
        file.close()
        for his_sta_data in file_datas:
            sta_info_arr = his_sta_data.split()
            if len(sta_info_arr) < 3:
                continue
            sta_id = sta_info_arr[0]
            sta_lat = int(sta_info_arr[1]) // 100 + (int(sta_info_arr[1]) % 100) / 60
            sta_lon = int(sta_info_arr[2]) // 100 + (int(sta_info_arr[2]) % 100) / 60
            sta_dict[sta_id] = str(sta_lon) + "\t" + str(sta_lat)
        return sta_dict
    except Exception as ex:
        print(ex)
        return None


def get_obs_fst_statistics_station(file_path: str):
    """
    获取西南雨季实况达到雨季的站点信息和预报达到雨季的站点信息
    ./file/statistics/obs_statistics_begin_08.txt
    ./file/statistics/obs_statistics_end_08.txt
    Args:
        file_path:

    Returns:

    """
    kv = {}
    try:
        f = open(file_path, "r")
        d = f.readlines()
        if len(d) == 0:
            return kv
        else:
            for data in d:
                k, v = data.strip().split("\t")
                kv[k] = v
            return kv
    except Exception as ex:
        print(ex)
        exit(1)


def read_station_data(file_path: str):
    """
    读取站点数据，返回KV值
    Args:
        file_path:   站点文件路径

    Returns:
        kv          日期：降水量

    """
    try:
        kv = {}
        f = open(file_path, "r")
        datas = f.readlines()
        for data in datas:
            k, v = data.strip().split("\t")
            kv[k] = v
        return kv
    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    _ = get_obs_fst_statistics_station("../file/statistics/obs_statistics_begin_08.txt")
