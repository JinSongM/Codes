#!/usr/bin/env python
# -*- coding: UTF-8 -*-

def load_station_information(file_path):

    try:
        ids, lons, lats, data_value, province, city, local = [], [], [], [], [], [], []
        file = open(file_path, encoding="gbk")
        file_datas = file.readlines()
        file_datas = sorted(file_datas)
        file.close()
        for his_sta_data in file_datas:
            sta_info_arr = his_sta_data.split()
            ids.append(sta_info_arr[0])
            lats.append(float("%.2f" % (int(sta_info_arr[1]) // 100 + (int(sta_info_arr[1]) % 100) / 60)))
            lons.append(float("%.2f" % (int(sta_info_arr[2]) // 100 + (int(sta_info_arr[2]) % 100) / 60)))
            data_value.append(sta_info_arr[3])
            province.append(sta_info_arr[4])
            city.append(sta_info_arr[5])
            local.append(sta_info_arr[6])
        return ids, lons, lats, data_value, province, city, local
    except Exception as ex:
        print(ex)
        return None, None, None, None, None, None