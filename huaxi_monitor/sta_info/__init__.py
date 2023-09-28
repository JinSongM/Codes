#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta
from sta_info.Constants import *
import numpy as np
import os
from utils import arrays
import utils



class StationInfo_08:

    def __init__(self, sta_obj_dict, date_time, start_h, collect_fst_path):
        """

        Args:
            sta_obj_dict
            date_time
            start_h

        """
        self.sta_obj_dict = sta_obj_dict
        self.date_time = date_time
        self.start_h = start_h
        self.collect_fst_path = collect_fst_path

        self.begin_rainy_date = None

        self.obs_begin_rainy_day_n = None
        self.obs_begin_rainy_day_s = None
        self.fst_begin_rainy_day_n = None
        self.fst_begin_rainy_day_s = None

        self.sp_begin_rainy_date = None
        self.sp_begin_rainy_day = []
        self.sp_end_rainy_day = []

        self.end_rain_date = None
        self.end_rain_date_N = None
        self.end_rain_date_S = None
        self.rainy_day_len = 0
        self.total_rain = 0
        self.fst_dict_N, self.fst_dict_S  = dict(), dict()

        self._gain_collectfst('./file/huaxi_stations_north_info.txt', self.fst_dict_N)
        self._gain_collectfst('./file/huaxi_stations_south_info.txt', self.fst_dict_S)
        self._judge_rainy_day_begin()
        self._judge_rainy_day_end_North()
        self._judge_rainy_day_end_Sourth()
        self._judge_rainy_day_end()
        self._cal_rainy_day_len()
        self._calculate_rainy_day_begin_to_end_total()
        self._rain_period_len_index()
        self._rainfall_index()
        self._Comprehensive_intensity_index()
        self._rain_intensity_grade()


    def _judge_rainy_day_begin(self):
        """

        Returns:

        """

        judge_obs_s, begin_rain_date_obs_list_s = self._rainy_day_begin_obs(self.date_time, endloc='south')
        if judge_obs_s:
            self.obs_begin_rainy_day_s = begin_rain_date_obs_list_s

        if self.obs_begin_rainy_day_s is not None:
            start_beginTime_s = datetime.strptime(self.obs_begin_rainy_day_s[-1], '%y%m%d') + timedelta(days=5)
            judge_fst_s, begin_rain_date_fst_list_s = self._rainy_day_begin_fst(start_beginTime_s, self.date_time + timedelta(days=10), endloc='south')
            if judge_fst_s:
                self.fst_begin_rainy_day_s = begin_rain_date_fst_list_s
        else:
            judge_fst_s, begin_rain_date_fst_list_s = self._rainy_day_begin_fst(self.date_time, self.date_time + timedelta(days=10), endloc='south')
            if judge_fst_s:
                self.fst_begin_rainy_day_s = begin_rain_date_fst_list_s

        judge_obs_n, begin_rain_date_obs_list_n = self._rainy_day_begin_obs(self.date_time, endloc='north')
        if judge_obs_n:
            self.obs_begin_rainy_day_n = begin_rain_date_obs_list_n

        if self.obs_begin_rainy_day_n is not None:
            start_beginTime_n = datetime.strptime(self.obs_begin_rainy_day_n[-1], '%y%m%d') + timedelta(days=5)
            if start_beginTime_n <=  self.date_time:
                judge_fst_n, begin_rain_date_fst_list_n = self._rainy_day_begin_fst(start_beginTime_n, self.date_time + timedelta(days=10), endloc='north')
                if judge_fst_n:
                    self.fst_begin_rainy_day_n = begin_rain_date_fst_list_n
            else:
                judge_fst_n, begin_rain_date_fst_list_n = self._rainy_day_begin_fst(self.date_time,
                                                                                    self.date_time + timedelta(days=10),
                                                                                    endloc='north')
                if judge_fst_n:
                    self.fst_begin_rainy_day_n = begin_rain_date_fst_list_n
        else:
            judge_fst_n, begin_rain_date_fst_list_n = self._rainy_day_begin_fst(self.date_time, self.date_time + timedelta(days=10), endloc='north')
            if judge_fst_n:
                self.fst_begin_rainy_day_n = begin_rain_date_fst_list_n

        if self.obs_begin_rainy_day_n is None and self.fst_begin_rainy_day_n is None and self.obs_begin_rainy_day_s is None and self.fst_begin_rainy_day_s is None:
            sp_begin_rainy_day_n, sp_end_rainy_day_n = self._rainy_day_begin(datetime(self.date_time.year, 8, 21),
                                                                             datetime(self.date_time.year, 10, 31),
                                                                             endloc='north')
            sp_begin_rainy_day_s, sp_end_rainy_day_s = self._rainy_day_begin(datetime(self.date_time.year, 8, 21),
                                                                             datetime(self.date_time.year, 11, 30),
                                                                             endloc='south')
            if len(sp_begin_rainy_day_n) > 0 and len(sp_begin_rainy_day_s) > 0:
                if sp_begin_rainy_day_n[0] > sp_begin_rainy_day_s[0]:
                    self.sp_begin_rainy_day.append(sp_begin_rainy_day_s[0])
                    self.sp_begin_rainy_date = sp_begin_rainy_day_s[0]
                else:
                    self.sp_begin_rainy_day.append(sp_begin_rainy_day_n[0])
                    self.sp_begin_rainy_date = sp_begin_rainy_day_n[0]
            elif len(sp_begin_rainy_day_n) + len(sp_begin_rainy_day_s) == 1:
                if len(sp_begin_rainy_day_n) == 1:
                    self.sp_begin_rainy_day.append(sp_begin_rainy_day_n[0])
                    self.sp_begin_rainy_date = sp_begin_rainy_day_n[0]
                else:
                    self.sp_begin_rainy_day.append(sp_begin_rainy_day_s[0])
                    self.sp_begin_rainy_date = sp_begin_rainy_day_s[0]
            else:
                pass

            if len(sp_end_rainy_day_s) > 0 and len(sp_end_rainy_day_n) > 0:
                if sp_end_rainy_day_s[0] > sp_end_rainy_day_n[0]:
                    self.sp_end_rainy_day.append(sp_end_rainy_day_s[0])
                else:
                    self.sp_end_rainy_day.append(sp_end_rainy_day_n[0])
            elif len(sp_end_rainy_day_s) + len(sp_end_rainy_day_n) == 1:
                if len(sp_end_rainy_day_s) == 1:
                    self.sp_end_rainy_day.append(sp_end_rainy_day_s[0])
                else:
                    self.sp_end_rainy_day.append(sp_end_rainy_day_n[0])
            else:
                pass

        Have_value_list = []
        for i in [self.obs_begin_rainy_day_n, self.obs_begin_rainy_day_s, self.fst_begin_rainy_day_n,
                      self.fst_begin_rainy_day_s, self.sp_begin_rainy_day]:
            if i is not None and len(i) > 0:
                Have_value_list.append(i)
        Tmp_list = [i[0] for i in Have_value_list]
        BeginTime_list = [datetime.strptime(i, '%y%m%d') for i in Tmp_list if type(i) is str]
        if len(BeginTime_list) > 0:
            self.begin_rainy_date = min(BeginTime_list)

    def _rainy_day_begin(self, datetime_S, datetime_N, endloc):
        """
        判断华西秋雨开始——实况
        Args:
            date_time:

        Returns:

        """
        sp_begin_rainy_day = []
        sp_end_rainy_day = []
        cur_time = datetime_S
        end_time = datetime_N
        rain_date_list = {}
        begin_time1, begin_time2 = cur_time, cur_time
        while begin_time1 <= end_time:
            judge_bool, max_rain_date = self._judge_th(begin_time1, endloc)
            rain_date_list[begin_time1] = judge_bool
            begin_time1 += timedelta(days=1)

        while begin_time2 <= end_time:
            bool_T, bool_F = {}, {}
            for i in range(10):
                tmp_time = begin_time2 + timedelta(days=i)
                tmp_bool = rain_date_list.get(tmp_time)
                if tmp_bool:
                    bool_T[tmp_time] = tmp_bool
                else:
                    bool_F[tmp_time] = tmp_bool
            if len(bool_T) >= 5:
                sp_begin_rainy_day.append(begin_time2)
                sp_end_rainy_day.append(list(bool_T.keys())[-1])
                begin_time2 += timedelta(days=10)
            else:
                begin_time2 += timedelta(days=1)
        return sp_begin_rainy_day, sp_end_rainy_day


    def _rainy_day_begin_obs(self, datetime_obs, endloc):
        """
        判断秋雨多雨期开始——实况
        Args:
            date_time:

        Returns:

        """
        cur_time = datetime(datetime_obs.year, 8, 21)
        end_time = datetime_obs
        begin_rain_date_list = []
        while cur_time < end_time:
            judge_bool, begin_rain_date = self._calculate_5_day(cur_time, endloc)
            if judge_bool:
                begin_rain_date_list.append(begin_rain_date)
                cur_time += timedelta(days=6)
            else:
                cur_time += timedelta(days=1)

        if len(begin_rain_date_list) > 0:
            return True, begin_rain_date_list
        else:
            return False, None

    def _rainy_day_begin_fst(self, beginTime, datetime_fst, endloc):
        """
        判断秋雨多雨期开始——预报
        Args:
            date_time:

        Returns:

        """
        cur_time = beginTime
        end_time = datetime_fst
        begin_rain_date_list = []
        while cur_time <= end_time:
            if cur_time >= datetime(beginTime.year, 8, 21):
                judge_bool, max_rain_date = self._calculate_5_day(cur_time, endloc)
                if judge_bool:
                    begin_rain_date_list.append(max_rain_date)
                    cur_time += timedelta(days=6)
                else:
                    cur_time += timedelta(days=1)
            else:
                cur_time += timedelta(days=1)

        if len(begin_rain_date_list) > 0:
            return True, begin_rain_date_list
        else:
            return False, None

    def _calculate_5_day(self, curtime, endloc):
        """

        Args:
            date_time

        Returns:
            多雨期

        """

        max_rain_date_list = []
        cur_time = None
        for i in range(0, 5):
            cur_time = curtime + timedelta(days=i)
            judge_bool, max_rain_date = self._judge_th(cur_time, endloc)
            if judge_bool:
                max_rain_date_list.append(max_rain_date)

        if len(max_rain_date_list) >= 4 and cur_time.strftime('%y%m%d') in max_rain_date_list:
            return True, str(np.min([int(i) for i in max_rain_date_list]))
        else:
            return False, None

    def _judge_th(self, curtime, endloc):
        """

        Args:
            date_time

        Returns:
            秋雨日

        """

        key = curtime.strftime("%y%m%d")
        if endloc == 'All':
            if key in self.sta_obj_dict.keys():
                value = self.sta_obj_dict.get(key)
                cal_num = 0
                for i in value:
                    if i[2] >= 0.1:
                        cal_num +=1

                if cal_num / len(value) >= 0.5:
                    return True, key
                else:
                    return False, None
            else:
                return False, None
        elif endloc == 'south':
            if key in self.sta_obj_dict.keys():
                value = self.sta_obj_dict.get(key)
                value_select = []
                for i in value:
                    if i[3] == '南区':
                        value_select.append(i)

                cal_num = 0
                for j in value_select:
                    if j[2] >= 0.1:
                        cal_num += 1

                if cal_num / len(value_select) >= 0.5:
                    return True, key
                else:
                    return False, None
            else:
                return False, None

        elif endloc == 'north':
            if key in self.sta_obj_dict.keys():
                value = self.sta_obj_dict.get(key)
                value_select = []
                for i in value:
                    if i[3] == '北区':
                        value_select.append(i)

                cal_num = 0
                for j in value_select:
                    if j[2] >= 0.1:
                        cal_num += 1

                if cal_num / len(value_select) >= 0.5:
                    return True, key
                else:
                    return False, None
            else:
                return False, None

        else:
            return False, None


    def _judge_rainy_day_end_North(self):
        """

        Returns: 北区华西秋雨结束

        """
        end_time = datetime(self.date_time.year, 10, 31)
        judge_obs, end_rain_date_obs_list = self._rainy_day_begin_obs(end_time, endloc = 'north')
        if judge_obs:
            last_rain_date = end_rain_date_obs_list[-1]
            self.end_rain_date_N = datetime.strptime(last_rain_date, "%y%m%d") + timedelta(days=4)

    def _judge_rainy_day_end_Sourth(self):
        """

        Returns: 南区华西秋雨结束

        """
        cur_time = datetime(self.date_time.year, 11, 1)
        end_time = datetime(self.date_time.year, 11, 30)

        no_rain_date = None
        while cur_time <= end_time:
            tmp_time = None
            tmp_no_rain_list = []
            for i in range(10):
                tmp_time = cur_time + timedelta(days=i)
                judge_bool, max_rain_date = self._judge_th(tmp_time, endloc = 'south')
                if judge_bool:
                    cur_time += timedelta(days=1)
                    continue
                else:
                    tmp_no_rain_list.append(tmp_time)
            if len(tmp_no_rain_list) >= 8 and tmp_time in tmp_no_rain_list:
                no_rain_date = cur_time
                break

        judge_obs, end_rain_date_obs_list = self._rainy_day_begin_obs(no_rain_date, endloc = 'south')
        if judge_obs:
            last_rain_date = end_rain_date_obs_list[-1]
            self.end_rain_date_S = datetime.strptime(last_rain_date, "%y%m%d") + timedelta(days=4)


    def _judge_rainy_day_end(self):
        """

        Returns: 国家级华西秋雨结束时间

        """
        if self.end_rain_date_N and self.end_rain_date_S is not None:
            if self.end_rain_date_N >= self.end_rain_date_S:
                self.end_rain_date = self.end_rain_date_N
            else:
                self.end_rain_date = self.end_rain_date_S

        elif len(self.sp_end_rainy_day) > 0:
            self.end_rain_date = self.sp_end_rainy_day[-1]
        else:
            self.end_rain_date = None

    def _cal_rainy_day_len(self):
        """

        Returns: 华西秋雨期长度

        """
        if self.end_rain_date and self.begin_rainy_date is not None:
            self.rainy_day_len = (self.end_rain_date - self.begin_rainy_date).days
        else:
            self.rainy_day_len = None

    def _calculate_rainy_day_begin_to_end_total(self):
        """

        Returns: 华西秋雨量

        """
        total_rain = 0
        if self.end_rain_date is not None:
            start_time = self.begin_rainy_date
            end_time = self.end_rain_date

            while start_time <= end_time:
                start_time_str = start_time.strftime('%y%m%d')
                if start_time_str in self.sta_obj_dict.keys():
                    sta_rain_value = self.sta_obj_dict.get(start_time_str)
                    sta_mean_rain = np.mean([i[2] for i in sta_rain_value])
                    total_rain += sta_mean_rain
                    start_time += timedelta(days=1)
                else:
                    start_time += timedelta(days=1)
        self.total_rain = total_rain


    def _rain_period_len_index(self):
        """

        Returns: 华西秋雨期长度指数

        """
        L0 = Climatic_Mean_AutumnRain_08
        SL = Climatic_Std_AutumnRain_08
        if self.rainy_day_len is not None:
            self.I = (self.rainy_day_len - L0) / SL
        else:
            self.I = None
        print(self.I)

    def _rainfall_index(self):
        """

        Returns: 华西秋雨量指数

        """
        R0 = Climatic_Mean_AutumnRain_value_08
        SR  = Climatic_Std_AutumnRain_value_08
        if self.total_rain is not None:
            self.II = (self.total_rain - R0) / SR
        else:
            self.II = None
        print(self.II)

    def _Comprehensive_intensity_index(self):
        """

        Returns: 华西秋雨综合强度指数

        """
        if self.I is not None and self.II is not None:
            self.III = (self.I + self.II) / 2
        else:
            self.III = None
        print(self.III)

    def _rain_intensity_grade(self):
        """

        Returns: 华西秋雨强度等级

        """

        # if self.III is not None:
        #     if self.I >= 1.5 and self.II >= 1.5 and self.III >= 1.5:
        #         self.IIII = '显著偏强'
        #     elif 0.5 <= self.I < 1.5 and 0.5 <= self.II < 1.5 and 0.5 <= self.III < 1.5:
        #         self.IIII = '偏强'
        #     elif -0.5 < self.I < 0.5 and -0.5 < self.II < 0.5 and -0.5 < self.III < 0.5:
        #         self.IIII = '正常'
        #     elif -1.5 < self.I <= -0.5 and -1.5 < self.I <= -0.5 and -1.5 < self.I <= -0.5:
        #         self.IIII = '偏弱'
        #     elif self.I <= -1.5 and self.II <= -1.5 and self.III <= -1.5:
        #         self.IIII = '显著偏弱'
        #     else:
        #         self.IIII = '未检测出'
        # else:
        #     self.IIII = '未检测出'
        if self.III is not None:
            if self.III >= 1.5:
                self.IIII = '显著偏强'
            elif 0.5 <= self.III < 1.5:
                self.IIII = '偏强'
            elif -0.5 < self.III < 0.5:
                self.IIII = '正常'
            elif -1.5 < self.I <= -0.5:
                self.IIII = '偏弱'
            elif self.III <= -1.5:
                self.IIII = '显著偏弱'
            else:
                self.IIII = '未检测出'
        else:
            self.IIII = '未检测出'


    def _gain_collectfst(self, txt_path, dict):

        ids, lons, lats, data_value, province, city, local = utils.load_station_information(txt_path)
        for i in range(24, 384, 24):
            son_path = os.path.join(self.collect_fst_path, (self.date_time-timedelta(days=1)).strftime('%Y%m%d') + self.start_h, 'tp',
                                    (self.date_time-timedelta(days=1)).strftime('%Y%m%d') + self.start_h + '.' + '{i:03d}'.format(i=i))
            father_path = os.path.join(self.collect_fst_path, (self.date_time-timedelta(days=1)).strftime('%Y%m%d') + self.start_h, 'tp',
                                    (self.date_time-timedelta(days=1)).strftime('%Y%m%d') + self.start_h + '.' + '{i:03d}'.format(i=i-24))

            if os.path.exists(son_path) and os.path.exists(father_path):
                son_data = arrays.load_array(son_path)
                son_array = np.array(son_data).reshape((51, 101, 141))
                father_data = arrays.load_array(father_path)
                father_array = np.array(father_data).reshape((51, 101, 141))
                data = son_array - father_array
                for j in range(0, 51, 1):
                    sta_data_list = []
                    station_data = arrays.interpolation_linear_g_to_s(data[j], np.array(lons), np.array(lats), 70.0, 10.0, 140.0, 60.0, 0.5, 0.5)
                    for k in range(0, len(ids)):
                        sta_data_list.append([lons[k], lats[k], "%.2f" % (station_data[k]*1000), local[k]])

                    key = (self.date_time+timedelta(days=i/24-1)).strftime('%Y%m%d') + '_' + str(j)
                    dict[key] = sta_data_list


class StationInfo:

    def __init__(self, sta_id: str, sta_lon: float, sta_lat: float, sta_Loc: str, split_time: datetime, start_h: str, sta_data: list):
        """

        Args:
            sta_id:               站点号
            sta_lon:              站点经度
            sta_lat:              站点纬度
            split_time:           实况与预报数据分割点，当前时间为预报数据的第一天
            start_h:
            sta_data:
        """
        self.id = sta_id
        self.lon = sta_lon
        self.lat = sta_lat
        self.Loc = sta_Loc
        self.date_time = split_time
        self.start_h = start_h
        self.data = None
        self._set_data(sta_data)


    def _set_data(self, sta_data):
        """

        Args:
            sta_data:

        Returns:

        """
        kv = {}
        for i_data in sta_data:
            key, value = i_data.strip().split("\t")
            kv[key] = [self.lon, self.lat, float(value), self.Loc]
        self.data = kv