#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
   @Project   ：Wiztek.MountainTorrent.SouthWestChina.Py 
   
   @File      ：__init__.py.py
   
   @Author    ：yhaoxian
   
   @Date      ：2022/3/23 18:09 
   
   @Describe  : 
   
"""

from datetime import datetime, timedelta
from sta_info import Constants
import numpy as np
import FileTools


def calculate_dict_max_key(datas: dict):
    """

    Args:
        datas:

    Returns:

    """
    max_value = max(datas.values())
    for key, value in datas.items():
        if value == max_value:
            return key, value


class StationInfo:

    def __init__(self, sta_id: str, sta_lon: float, sta_lat: float, split_time: datetime, start_h: str, sta_data: list, his_data: list):
        """

        Args:
            sta_id:               站点号
            sta_lon:              站点经度
            sta_lat:              站点纬度
            split_time:           实况与预报数据分割点，当前时间为预报数据的第一天
            start_h:
            sta_data:
            his_data:
        """
        self.id = sta_id
        self.lon = sta_lon
        self.lat = sta_lat
        self.date_time = split_time
        self.start_h = start_h
        self.his_data = his_data
        self.data = None
        self.obs_begin_rainy_day = None
        self.fst_begin_rainy_day = None
        self.obs_end_rainy_day = None
        self.fst_end_rainy_day = None
        self.min_date = None
        self.max_date = None
        self.rainy_days_total_rain = 0
        self.future_ten_days_total_rain = 0
        self.future_ten_rain_total_historical_ranking = 0
        self._set_data(sta_data)
        self._judge_rainy_day_begin()
        self._judge_rainy_day_end()
        self._calculate_rainy_day_begin_to_now_total()
        self._calculate_future_ten_days_rainy_sum()
        self._judge_the_order_in_his_year()

    def _calculate_future_ten_days_rainy_sum(self):
        """
        计算当前日期和之后日期的数据之和

        Returns:

        """
        try:
            total = 0
            for i in range(0, 10):
                key = (self.date_time + timedelta(days=i)).strftime("%y%m%d")
                if key in self.data.keys():
                    total += float(self.data.get(key))
                else:
                    total += 0
            self.future_ten_days_total_rain = total
        except Exception as ex:
            print(ex)

    def write_data_to_file(self, output_path: str):
        """

        Args:
            output_path:

        Returns:

        """
        pass

    def get_five_rolling_day_rainy_sum(self, date_time: datetime):
        """
        获取当前日期的五天滑动累积量
        Args:
            date_time:

        Returns:
            五天滑动累积量

        """
        rainy_sum = 0
        for i in range(0, 5):
            time_str = (date_time - timedelta(days=i)).strftime("%y%m%d")
            if time_str in self.data.keys():
                rainy_sum += self.data.get(time_str)
        return rainy_sum

    def _set_data(self, sta_data):
        """

        Args:
            sta_data:

        Returns:

        """
        kv = {}
        for i_data in sta_data:
            key, value = i_data.strip().split("\t")
            kv[key] = float(value)
        self.data = kv

    def _judge_rainy_day_begin(self):
        """

        Returns:

        """
        start_sta_ids = FileTools.get_obs_fst_statistics_station("./file/statistics/obs_statistics_begin_{}.txt".format(self.start_h))
        if self.id in start_sta_ids.keys():
            self.obs_begin_rainy_day = start_sta_ids.get(self.id)
        else:
            judge_obs, begin_date_obs = self._rainy_day_begin_obs(self.date_time)
            if judge_obs:
                if begin_date_obs < self.date_time.strftime('%y%m%d'):
                    self.obs_begin_rainy_day = begin_date_obs
                else:
                    self.fst_begin_rainy_day = begin_date_obs
            else:
                for i in range(0,11):
                    judge_fst, begin_date_fst = self._rainy_day_begin_fst(self.date_time + timedelta(days=i))
                    if judge_fst:
                        if begin_date_fst >= self.date_time.strftime('%y%m%d'):
                            self.fst_begin_rainy_day = begin_date_fst
                        else:
                            self.obs_begin_rainy_day = begin_date_fst


    def _rainy_day_begin_obs(self, datetime_obs):
        """
        判断雨季开始降水
        Args:
            date_time:

        Returns:

        """
        cur_time = datetime(datetime_obs.year, 4, 21)
        end_time = datetime_obs
        while cur_time < end_time:
            judge_bool, max_rain_date = self._calculate_5_day_sum(cur_time)
            if judge_bool:
                begin_rain_data = max_rain_date
                return True, begin_rain_data
            else:
                cur_time += timedelta(days=1)
        return False, None

    def _rainy_day_begin_fst(self, datetime_fst):
        """
        判断雨季开始降水
        Args:
            date_time:

        Returns:

        """
        cur_time = self.date_time
        end_time = datetime_fst
        while cur_time < end_time:
            judge_bool, max_rain_date = self._calculate_5_day_sum(cur_time)
            if judge_bool:
                    begin_rain_data = max_rain_date
                    return True, begin_rain_data
            else:
                cur_time += timedelta(days=1)
        return False, None

    def _calculate_5_day_sum(self, curtime):
        """

        Args:
            date_time:

        Returns:

        """
        if "08" == self.start_h:
            avg_data = Constants.PENTAD_ACCUMLATED_PRECIPITATION_5_10_08
        else:
            avg_data = Constants.PENTAD_ACCUMLATED_PRECIPITATION_5_10_20

        max_rain_date_list = []
        for i in range(0, 20):
            cur_time = curtime + timedelta(days=i)
            judge_bool, max_rain_date = self._judge_th(cur_time, avg_data)
            if judge_bool:
                max_rain_date_list.append(max_rain_date)
        if len(max_rain_date_list) >= 2:
            return True, max_rain_date_list[0]
        else:
            return False, None

    def _judge_th(self, curtime, avg_data):
        tp_sum = 0
        value_dict = {}
        for i in range(0, 5):
            tmp_time = curtime - timedelta(days=i)
            key = tmp_time.strftime("%y%m%d")
            if key in self.data.keys():
                value = float(self.data.get(key))
                value_dict[key] = value
                tp_sum += value
            else:
                tp_sum += 0
                value_dict[key] = 0
        if tp_sum >= avg_data:
            max_rain_date, _ = calculate_dict_max_key(value_dict)
            return True, max_rain_date
        else:
            return False, None

    def _judge_rainy_day_end(self):
        """
        判断西南雨季
        Returns:

        """
        start_sta_ids = FileTools.get_obs_fst_statistics_station("./file/statistics/obs_statistics_end_{}.txt".format(self.start_h))
        if self.id in start_sta_ids.keys():
            self.obs_end_rainy_day = start_sta_ids.get(self.id)
        else:
            judge_obs, end_date_obs = self._rainy_day_end(self.date_time)
            if judge_obs:
                self.obs_end_rainy_day = end_date_obs
            else:
                judge_fst, end_date_fst = self._rainy_day_end(self.date_time + timedelta(days=30))
                if judge_fst:
                    self.fst_end_rainy_day = end_date_fst


    def _rainy_day_end(self, curtime):
        """
        判断雨季结束降水
        Args:
            date_time:

        Returns:

        """
        if curtime > datetime(curtime.year, 9, 21, 0, 0, 0):
            if "08" == self.start_h:
                avg_data = Constants.PENTAD_ACCUMLATED_PRECIPITATION_1_12_08
            else:
                avg_data = Constants.PENTAD_ACCUMLATED_PRECIPITATION_1_12_20
            cur_time =  curtime - timedelta(days=20)
            end_time =  curtime
            while cur_time < end_time:
                tp_sum_20 = []
                for i in range(0, 20):
                    tp_sum_20.append(self._statistics_tp(curtime + timedelta(i)))
                if np.max(tp_sum_20) < avg_data:
                    return True, curtime.strftime("%Y%m%d")
                else:
                    cur_time += timedelta(days=1)
                    return False, None
        else:
            #print('输入时间节点不在雨季结束日期范围')
            return False, None


    def _statistics_tp(self, cur_time):
        tp_sum = 0
        for i in range(0, 5):
            time_tmp = cur_time - timedelta(days=i)
            key = time_tmp.strftime("%y%m%d")
            if key in self.data.keys():
                value = float(self.data.get(key))
                tp_sum += value
        return tp_sum


    def _calculate_rainy_day_begin_to_now_total(self):
        """
        计算站点雨季开始时间到当前时间的累计降水量
        Returns:

        """
        total = 0
        if self.obs_begin_rainy_day is not None:
            rainy_day_time = datetime.strptime(self.obs_begin_rainy_day, "%y%m%d")
            tmp_time = rainy_day_time
            while tmp_time < self.date_time:
                key = tmp_time.strftime("%y%m%d")
                total += self.data.get(key)
                tmp_time += timedelta(days=1)
            self.rainy_days_total_rain = total
        else:
            self.rainy_days_total_rain = 0

    def _judge_the_order_in_his_year(self):
        self.his_data.sort(reverse=True)
        for i in range(0, 5):
            if self.future_ten_days_total_rain > self.his_data[i]:
                self.future_ten_rain_total_historical_ranking = i + 1
                break
            elif self.future_ten_days_total_rain > self.his_data[i + 1]:
                self.future_ten_rain_total_historical_ranking = i + 2
                break