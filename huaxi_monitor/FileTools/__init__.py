#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import multiprocessing as mp
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def read_station_information(file_path_s: str, file_path_n: str):
    """
    读取华西站点信息
    Args:
        file_path:  文件路径

    Returns:
        sta_ids       站点号
        lons          经度
        lats          纬度

    """
    try:
        ids, lons, lats, Loc = [], [], [], []
        file_s = open(file_path_s,  encoding='gbk')
        file_datas_s = file_s.readlines()
        file_datas_s = sorted(file_datas_s)
        file_s.close()

        file_n = open(file_path_n,  encoding='gbk')
        file_datas_n = file_n.readlines()
        file_datas_n = sorted(file_datas_n)
        file_n.close()


        for his_sta_data_s in file_datas_s:
            sta_info_arr_s = his_sta_data_s.split()
            if len(sta_info_arr_s) < 3:
                continue
            ids.append(sta_info_arr_s[0])
            lats.append(int(sta_info_arr_s[1]) / 100)
            lons.append(int(sta_info_arr_s[2]) / 100)
            Loc.append('南区')

        for his_sta_data_n in file_datas_n:
            sta_info_arr_n = his_sta_data_n.split()
            if len(sta_info_arr_n) < 3:
                continue
            ids.append(sta_info_arr_n[0])
            lats.append(int(sta_info_arr_n[1]) / 100)
            lons.append(int(sta_info_arr_n[2]) / 100)
            Loc.append('北区')

        return ids, lons, lats, Loc
    except Exception as ex:
        print(ex)
        return None, None, None

def cal_Rain_HisMeanLen(file_path1, file_path2):
    """
    读取历年数据，计算华西秋雨长度的气候均值、均方差
    Args:
        file_path:   文件路径

    Returns:
        kv          降水量

    """

    try:
        kv_start = []
        kv_end = []
        sis_len = []

        f_start = open(file_path1, "r")
        datas_start = f_start.readlines()
        for data in datas_start:
            k, v = data.strip().split()
            kv_start.append(datetime.strptime(k + v, '%Y%m%d'))

        f_end = open(file_path2, "r")
        datas_end = f_end.readlines()
        for data in datas_end:
            k, v = data.strip().split()
            kv_end.append(datetime.strptime(k + v, '%Y%m%d'))

        if len(kv_start) == len(kv_end):
            for i in range(len(kv_start)):
                Length = kv_end[i] - kv_start[i]
                sis_len.append(Length.days)

        Hissq = []
        Hismean = np.mean(sis_len)
        for i in sis_len:
            sq = (i - Hismean) ** 2
            Hissq.append(sq)

        std = (np.sum(Hissq) / len(Hissq)) ** 0.5

        return Hismean, std
    except Exception as ex:
        print(ex)
class Statistics_raindays:

    def __init__(self, CSV_path, sta_path, date_path):
        """

        Args:
            sta_obj_list:
            date_time:
            start_h:
            pic_output_path:
        """
        self.CSV_path = CSV_path
        self.sta_path = sta_path
        self.date_path = date_path
        self.rain_sta_08 = []
        self.rain_sta_20 = []
        self.cal_Rain_HisMeanStr_multi(self.CSV_path, self.sta_path, self.date_path)

    def _cal_Rain_main(self, data_date, dataframe, stations_id):

        "多线程主函数"

        data_split_list_date = data_date.strip().split('\t')
        Year, Start, End = data_split_list_date[0], data_split_list_date[1], data_split_list_date[2]
        Start_dt = datetime.strptime(str(int(Year) * 10000 + int(Start)), '%Y%m%d')
        End_dt = datetime.strptime(str(int(Year) * 10000 + int(End)), '%Y%m%d')

        df = dataframe.copy()
        df['date'] = df['P_YEAR'] * 10000 + df['P_MON'] * 100 + df['P_DAY']

        sql_start = (df['date'] >= int(Year) * 10000 + int(Start))
        sql_end = (df['date'] <= int(Year) * 10000 + int(End))
        df_sta = df.loc[sql_start & sql_end]
        df_tur = df_sta.loc[df_sta['STATION_ID'].isin([int(i) for i in stations_id])]

        day_mean_08 = []
        day_mean_20 = []
        begin_dt = Start_dt
        while begin_dt < End_dt:
            begin_dt_str = int(begin_dt.strftime('%Y%m%d'))
            df_tur_copy = df_tur.copy()
            df_tur_copy_select = df_tur_copy.loc[df_tur_copy['date'] == begin_dt_str]

            array_08 = df_tur_copy_select['PRE_TIME_0808']
            array_20 = df_tur_copy_select['PRE_TIME_2020']
            array_08[array_08 > 9999] = np.nan
            array_20[array_20 > 9999] = np.nan

            day_mean_08.append(np.nanmean(array_08))
            day_mean_20.append(np.nanmean(array_20))
            begin_dt += timedelta(days=1)

        return np.sum(day_mean_08), np.sum(day_mean_20)

    def cal_Rain_HisMeanStr_multi(self, CSV_path, sta_path, date_path):

        stations_id = []
        dataframe = pd.read_csv(CSV_path)

        f_sta = open(sta_path, encoding='utf-8')
        datas_sta = f_sta.readlines()
        for data_sta in datas_sta:
            data_split_list_sta = data_sta.strip().split('\t')
            stations_id.append(data_split_list_sta[0])

        pool = mp.Pool()
        results = []

        f_date = open(date_path, encoding='utf-8')
        datas_date = f_date.readlines()
        for data_date in datas_date:
            res = pool.apply_async(self._cal_Rain_main, (data_date, dataframe, stations_id,))
            results.append(res)

        pool.close()
        pool.join()
        Result = [i.get() for i in results]

        self.rain_sta_08 = [i[0] for i in Result]
        self.rain_sta_20 = [i[1] for i in Result]


def cal_Rain_HisMeanStr(CSV_path, sta_path, date_path):

    stations_id = []
    rain_statistics_08 = []
    rain_statistics_20 = []

    dataframe = pd.read_csv(CSV_path)

    f_sta = open(sta_path, encoding='utf-8')
    datas_sta = f_sta.readlines()
    for data_sta in datas_sta:
        data_split_list_sta = data_sta.strip().split('\t')
        stations_id.append(data_split_list_sta[0])

    f_date = open(date_path, encoding='utf-8')
    datas_date = f_date.readlines()
    for data_date in datas_date:
        data_split_list_date = data_date.strip().split('\t')
        Year, Start, End = data_split_list_date[0], data_split_list_date[1], data_split_list_date[2]
        Start_dt = datetime.strptime(str(int(Year) * 10000 + int(Start)), '%Y%m%d')
        End_dt = datetime.strptime(str(int(Year) * 10000 + int(End)), '%Y%m%d')

        df = dataframe.copy()
        df['date'] = df['P_YEAR'] * 10000 + df['P_MON'] * 100 + df['P_DAY']

        sql_start = (df['date'] >= int(Year) * 10000 + int(Start))
        sql_end = (df['date'] <= int(Year) * 10000 + int(End))
        df_sta = df.loc[sql_start & sql_end]
        df_tur = df_sta.loc[df_sta['STATION_ID'].isin([int(i) for i in stations_id])]

        day_mean_08 = []
        day_mean_20 = []
        begin_dt = Start_dt
        while begin_dt < End_dt:
            begin_dt_str = int(begin_dt.strftime('%Y%m%d'))
            df_tur_copy = df_tur.copy()
            df_tur_copy_select = df_tur_copy.loc[df_tur_copy['date'] == begin_dt_str]

            array_08 = df_tur_copy_select['PRE_TIME_0808']
            array_20 = df_tur_copy_select['PRE_TIME_2020']
            array_08[array_08 > 9999] = np.nan
            array_20[array_20 > 9999] = np.nan

            day_mean_08.append(np.nanmean(array_08))
            day_mean_20.append(np.nanmean(array_20))
            begin_dt += timedelta(days=1)

        rain_statistics_08.append(np.sum(day_mean_08))
        rain_statistics_20.append(np.sum(day_mean_20))

    return rain_statistics_08, rain_statistics_20

if __name__ == '__main__':

    # path_dir_start = r'D:\Wiztek_Python\Framework_Python3\huaxiqiuyu\Files\华西秋雨执行方案\huaxi_start_date.txt'
    # path_dir_end = r'D:\Wiztek_Python\Framework_Python3\huaxiqiuyu\Files\华西秋雨执行方案\huaxi_end_date.txt'
    # Avg, Std = cal_Rain_HisMeanLen(path_dir_start, path_dir_end)
    # print(Avg, Std)

    path_dir_start = r'D:\Wiztek_Python\Framework_Python3\huaxiqiuyu\Files\ENV_T_R_NWST_D_DATA_TABLE.csv'
    sta_path = r'D:\Wiztek_Python\Framework_Python3\huaxiqiuyu\file\huaxi_stations_info.txt'
    date_path = r'D:\Wiztek_Python\Framework_Python3\huaxiqiuyu\file\huaxi_his_date.txt'
    obj = Statistics_raindays(path_dir_start, sta_path, date_path)
    # print(np.nanmean(year_rain_08), np.nanstd(year_rain_08))
    # print(np.nanmean(year_rain_20), np.nanstd(year_rain_20))