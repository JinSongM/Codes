#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
   @Project   ：Wiztek.MountainTorrent.SouthWestChina.Py 

   @File      ：__init__.py.py

   @Author    ：yhaoxian

   @Date      ：2022/3/23 18:08

   @Describe  :

"""

from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from collections import Counter
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from draw import figure_pic
from utils import log_configure as log

plt.rcParams['font.sans-serif'] = ['SIMHEI']  # 显示中文标签
plt.rcParams['axes.unicode_minus'] = False

logger = log.Logger(log_path="./log/pic_draw_tasks")


class PictureDrawTask:

    def __init__(self, sta_obj_list: list, date_time: datetime, start_h: str, pic_output_path: str):
        """

        Args:
            sta_obj_list:
            date_time:
            start_h:
            pic_output_path:
        """
        self.sta_obj_list = sta_obj_list
        self.date_time = date_time
        self.start_h = start_h
        self.pic_output_path = pic_output_path
        self.region_rainy_day_begin = None
        self.region_rainy_day_end = None
        self._save_rainy_days_begin_to_file()
        self._save_rainy_days_end_to_file()

    def _save_rainy_days_begin_to_file(self):
        results = []
        for sta_obj in self.sta_obj_list:
            if sta_obj.obs_begin_rainy_day is not None:
                results.append(sta_obj.id + "\t" + sta_obj.obs_begin_rainy_day + "\n")
        if "08" == self.start_h:
            with open("./file/statistics/obs_statistics_begin_08.txt", "w") as f:
                f.writelines(results)
        if "20" == self.start_h:
            with open("./file/statistics/obs_statistics_begin_20.txt", "w") as f:
                f.writelines(results)

    def _save_rainy_days_end_to_file(self):
        results = []
        for sta_obj in self.sta_obj_list:
            if sta_obj.obs_end_rainy_day is not None:
                results.append(sta_obj.id + "\t" + sta_obj.obs_end_rainy_day + "\n")
        if "08" == self.start_h:
            with open("./file/statistics/obs_statistics_end_08.txt", "w") as f:
                f.writelines(results)
        if "20" == self.start_h:
            with open("./file/statistics/obs_statistics_end_20.txt", "w") as f:
                f.writelines(results)

    def pic_draw_1(self):
        """

        Returns:

        """
        sta_data_kv = {}
        for sta_obj in self.sta_obj_list:
            kv = sta_obj.data
            for k, v in kv.items():
                if k in sta_data_kv.keys():
                    sta_data_kv.get(k).append(v)
                else:
                    arr = [v]
                    sta_data_kv[k] = arr
        labels, obs_data, fst_data, date_times = [], [], [], []
        for i in range(-50, 0, 1):
            tmp_time = self.date_time + timedelta(days=i)
            key = tmp_time.strftime("%y%m%d")
            obs_data.append(np.nanmean(sta_data_kv.get(key)))
            fst_data.append(float(0))
            labels.append(tmp_time.strftime("%d%b"))
            date_times.append(tmp_time)
        for i in range(0, 10, 1):
            tmp_time = self.date_time + timedelta(days=i)
            key = tmp_time.strftime("%y%m%d")
            obs_data.append(float(0))
            fst_data.append(np.nanmean(sta_data_kv.get(key)))
            labels.append(tmp_time.strftime("%d%b"))
            date_times.append(tmp_time)

        line_data_1 = self.read_tp_daily_mean()
        line_data_mean_1 = [line_data_1[cd.strftime('%m%d')] for cd in date_times]

        line_data_2 = self.read_tp_rolling_mean()
        line_data_mean_2 = [line_data_2[cd.strftime('%m%d')] for cd in date_times]

        pic_name = (self.date_time - timedelta(days=1)).strftime("%y%m%d") + self.start_h + "_西南地区降雨量监测和预报-集合平均.png"
        file_output_path = self.pic_output_path.format((self.date_time - timedelta(days=1)).strftime("%Y%m%d"))
        if not os.path.exists(file_output_path):
            os.makedirs(file_output_path)
        fig = plt.figure(figsize=(10, 5))
        ax1 = plt.subplot(111)

        # 先画实况
        plt.bar(labels, obs_data, color='b', label='Observed')

        # 再画预报
        plt.bar(labels, fst_data, color='r', label='Forecast')

        # 气候日平均
        plt.plot(labels, line_data_mean_1, color='k', label='气候日平均')

        # 气候5天滑动平均
        plt.plot(labels, line_data_mean_2, color='c', linestyle='dashed', label='气候5天滑动平均')

        plt.legend(loc='upper left', fontsize=10)

        x_major_locator = MultipleLocator(5)
        ax1.xaxis.set_major_locator(x_major_locator)
        plt.title('西南地区降雨量监测和预报   {}'.format(
            (self.date_time - timedelta(days=1)).strftime("%Y-%m-%d ") + self.start_h + "起报"))
        plt.legend()  # 显示图例

        plt.savefig(os.path.join(file_output_path, pic_name), bbox_inches='tight', dpi=300)
        plt.close(fig)

    def pic_draw_2(self):
        """

        Returns:

        """
        obs_lons, obs_lats = [], []
        fst_lons, fst_lats = [], []
        other_lons, other_lats = [], []
        for sta_obj in self.sta_obj_list:
            if sta_obj.obs_begin_rainy_day is not None:
                obs_lons.append(sta_obj.lon)
                obs_lats.append(sta_obj.lat)
            elif sta_obj.fst_begin_rainy_day is not None:
                fst_lons.append(sta_obj.lon)
                fst_lats.append(sta_obj.lat)
            else:
                other_lons.append(sta_obj.lon)
                other_lats.append(sta_obj.lat)

        pic_name = "{}_西南雨季开始站点监测和预报.png".format((self.date_time - timedelta(days=1)).strftime("%y%m%d") + self.start_h)
        file_output_path = self.pic_output_path.format((self.date_time - timedelta(days=1)).strftime("%Y%m%d"))
        if not os.path.exists(file_output_path):
            os.makedirs(file_output_path)

        draw = figure_pic.DrawImages(extent=[80, 110, 20, 35], x_scale=5, y_scale=5)
        draw.set_title(
            "西南雨季开始站点监测和预报  {}".format((self.date_time - timedelta(days=1)).strftime("%y%m%d") + self.start_h))
        draw.add_one_or_multi_province(add_china_shp=True, add_world_shp=False, add_sub_nine_dashed=False)

        scatter_style_1 = [other_lons, other_lats, 20, '*', "r", '未开始']
        scatter_style_2 = [fst_lons, fst_lats, 20, 'o', "g", '模式预报开始']
        scatter_style_3 = [obs_lons, obs_lats, 20, '^', "b", '已开始']
        scatter = [scatter_style_1, scatter_style_2, scatter_style_3]
        draw.add_scatter(scatter)

        sta_ids_start = len(obs_lons)
        sta_ids_fst = len(fst_lons)
        sta_ids_not = len(other_lons)

        per_1 = "%.1f%%" % (sta_ids_start / (sta_ids_fst + sta_ids_not + sta_ids_start) * 100)
        per_2 = "%.1f%%" % (sta_ids_fst / (sta_ids_fst + sta_ids_not + sta_ids_start) * 100)
        per_3 = "%.1f%%" % ((sta_ids_start + sta_ids_fst) / (sta_ids_fst + sta_ids_not + sta_ids_start) * 100)

        annotate_style_1 = [81, 23, "已开始站点数： {}\n已开始站比率： {}".format(sta_ids_start, per_1), "b", 15]
        annotate_style_2 = [81, 22, "模式预报开始站点数： {}\n模式预报开始站比率： {}".format(sta_ids_fst, per_2), "r", 15]
        annotate_style_3 = [81, 21, "总区域开始站点比率： {}\n".format(per_3), "k", 15]
        annotate = [annotate_style_1, annotate_style_2, annotate_style_3]
        draw.add_annotate(annotate)
        draw.add_legend()
        draw.save_fig(os.path.join(file_output_path, pic_name))

    def pic_draw_3(self):
        """

        Returns:

        """
        labels = []
        men_mean = {}
        women_mean = {}
        for i in range(-50, 0, 1):
            # if (self.date_time + timedelta(days=i)) >= datetime(self.date_time.year, 4, 21):
            labels.append((self.date_time + timedelta(days=i)).strftime("%d%b"))
            key = (self.date_time + timedelta(days=i)).strftime("%y%m%d")
            men_mean[key] = []
            women_mean[key] = []
            for sta_obj in self.sta_obj_list:
                if sta_obj.obs_begin_rainy_day is not None:
                    if sta_obj.obs_begin_rainy_day <= key:
                        men_mean[key].append(sta_obj.id)
        for i in range(0, 10, 1):
            # if (self.date_time + timedelta(days=i)) >= datetime(self.date_time.year, 4, 21):
            labels.append((self.date_time + timedelta(days=i)).strftime("%d%b"))
            key = (self.date_time + timedelta(days=i)).strftime("%y%m%d")
            men_mean[key] = []
            women_mean[key] = []
            for sta_obj in self.sta_obj_list:
                if sta_obj.obs_begin_rainy_day is not None:
                    if sta_obj.obs_begin_rainy_day <= key:
                        men_mean[key].append(sta_obj.id)
            for sta_obj in self.sta_obj_list:
                if sta_obj.fst_begin_rainy_day is not None:
                    if sta_obj.fst_begin_rainy_day <= key:
                        women_mean[key].append(sta_obj.id)
        men = []
        women = []
        for i in range(-50, 10, 1):
            # if (self.date_time + timedelta(days=i)) >= datetime(self.date_time.year, 4, 21):
            key = (self.date_time + timedelta(days=i)).strftime("%y%m%d")
            men.append(len(men_mean.get(key)) / 301 * 100)
            women.append(len(women_mean.get(key)) / 301 * 100)

        pic_name = "{}_西南雨季开始站点比率观测和预报.png".format(
            (self.date_time - timedelta(days=1)).strftime("%y%m%d") + self.start_h)
        file_output_path = self.pic_output_path.format((self.date_time - timedelta(days=1)).strftime("%Y%m%d"))
        if not os.path.exists(file_output_path):
            os.makedirs(file_output_path)

        fig, ax = plt.subplots(figsize=[12, 5])

        ax.plot([0, 59], [60, 60], linewidth=2, color='b')
        ax.bar(labels, men, 0.8, label='观测', color="g")
        ax.bar(labels, women, 0.8, bottom=men, label='预报', color="r")

        ax.set_xlabel('时间')
        ax.set_ylabel('百分比（%）')
        ax.set_title('西南雨季开始站点比率观测和预报')

        # 设置坐标
        ax.set_xticks(labels)
        ax.set_yticks(np.arange(0, 110))

        # 设置x轴主刻度间隔为5，设置x轴副刻度间隔为1
        ax.xaxis.set_major_locator(MultipleLocator(5))
        ax.xaxis.set_minor_locator(MultipleLocator(1))
        # 设置y轴主刻度间隔为20，设置y轴副刻度间隔为5
        ax.yaxis.set_major_locator(MultipleLocator(20))
        ax.yaxis.set_minor_locator(MultipleLocator(5))
        # 设置y轴数值范围
        plt.ylim(-5, 110)

        # 设置图例
        ax.legend(loc='upper left', fontsize=12)

        # 设置网格线
        ax.grid(True, linestyle='--', axis='y', which='major')
        plt.savefig(os.path.join(file_output_path, pic_name))
        plt.close(fig)

    def pic_draw_4(self):
        """

        Returns:

        """
        obs_lons, obs_lats = [], []
        fst_lons, fst_lats = [], []
        other_lons, other_lats = [], []
        for sta_obj in self.sta_obj_list:
            if sta_obj.obs_end_rainy_day is not None:
                obs_lons.append(sta_obj.lon)
                obs_lats.append(sta_obj.lat)
            elif sta_obj.fst_end_rainy_day is not None:
                fst_lons.append(sta_obj.lon)
                fst_lats.append(sta_obj.lat)
            else:
                other_lons.append(sta_obj.lon)
                other_lats.append(sta_obj.lat)

        pic_name = "{}_西南雨季结束站点监测和预报.png".format((self.date_time - timedelta(days=1)).strftime("%y%m%d") + self.start_h)
        file_output_path = self.pic_output_path.format((self.date_time - timedelta(days=1)).strftime("%Y%m%d"))
        if not os.path.exists(file_output_path):
            os.makedirs(file_output_path)
        draw = figure_pic.DrawImages(extent=[80, 110, 20, 35], x_scale=5, y_scale=5)
        draw.set_title(
            "西南雨季结束站点监测和预报  {}".format((self.date_time - timedelta(days=1)).strftime("%y%m%d") + self.start_h))
        draw.add_one_or_multi_province(add_china_shp=True, add_world_shp=False, add_sub_nine_dashed=False)

        scatter_style_1 = [other_lons, other_lats, 20, '*', "r", '未结束']
        scatter_style_2 = [fst_lons, fst_lats, 20, 'o', "g", '模式预报结束']
        scatter_style_3 = [obs_lons, obs_lats, 20, '^', "b", '已结束']
        scatter = [scatter_style_1, scatter_style_2, scatter_style_3]
        draw.add_scatter(scatter)

        sta_ids_end = len(obs_lons)
        sta_ids_fst = len(fst_lons)
        sta_ids_not = len(other_lons)

        per_1 = "%.1f%%" % (sta_ids_end / (sta_ids_fst + sta_ids_not + sta_ids_end) * 100)
        per_2 = "%.1f%%" % (sta_ids_fst / (sta_ids_fst + sta_ids_not + sta_ids_end) * 100)
        per_3 = "%.1f%%" % ((sta_ids_end + sta_ids_fst) / (sta_ids_fst + sta_ids_not + sta_ids_end) * 100)

        annotate_style_1 = [81, 23, "已结束站点数： {}\n已结束站比率： {}".format(sta_ids_end, per_1), "b", 15]
        annotate_style_2 = [81, 22, "模式预报结束站点数： {}\n模式预报结束站比率： {}".format(sta_ids_fst, per_2), "r", 15]
        annotate_style_3 = [81, 21, "总区域结束站点比率： {}\n".format(per_3), "k", 15]
        annotate = [annotate_style_1, annotate_style_2, annotate_style_3]
        draw.add_annotate(annotate)
        draw.add_legend()
        draw.save_fig(os.path.join(file_output_path, pic_name))

    def pic_draw_5(self):
        """

        Returns:

        """
        sta_datas = []
        sta_lons = []
        sta_lats = []
        for sta_obj in self.sta_obj_list:
            sta_lons.append(sta_obj.lon)
            sta_lats.append(sta_obj.lat)
            sta_datas.append(sta_obj.rainy_days_total_rain)

        pic_name = "{}_西南地区开始日期至当前日期的累计降水量分布预报产品.png".format(
            (self.date_time - timedelta(days=1)).strftime("%y%m%d") + self.start_h)
        file_output_path = self.pic_output_path.format((self.date_time - timedelta(days=1)).strftime("%Y%m%d"))
        if not os.path.exists(file_output_path):
            os.makedirs(file_output_path)
        draw = figure_pic.DrawImages(extent=[80, 110, 20, 35], x_scale=5, y_scale=5)
        draw.set_title("西南地区开始日期至当前日期的累计降水量分布预报产品  {}".format(
            (self.date_time - timedelta(days=1)).strftime("%y%m%d") + self.start_h))
        draw.add_one_or_multi_province(add_china_shp=True, add_world_shp=False, add_sub_nine_dashed=False)
        v_min, v_max = 0, 60

        scatter_style_1 = [sta_lons, sta_lats, sta_datas, v_min, v_max]
        scatter = [scatter_style_1]
        draw.add_scatter(scatter)
        draw.add_color_bar(v_min, v_max)
        draw.save_fig(os.path.join(file_output_path, pic_name))

    def pic_draw_6(self):
        """

        Returns:

        """
        lons_1, lats_1, datas_1 = list(), list(), list()
        lons_2, lats_2, datas_2 = list(), list(), list()
        lons_3, lats_3, datas_3 = list(), list(), list()
        lons_4, lats_4, datas_4 = list(), list(), list()
        lons_5, lats_5, datas_5 = list(), list(), list()
        lons_6, lats_6, datas_6 = list(), list(), list()
        for sta_obj in self.sta_obj_list:
            if sta_obj.future_ten_rain_total_historical_ranking == 1:
                lons_1.append(sta_obj.lon)
                lats_1.append(sta_obj.lat)
                datas_1.append(sta_obj.future_ten_days_total_rain)
            elif sta_obj.future_ten_rain_total_historical_ranking == 2:
                lons_2.append(sta_obj.lon)
                lats_2.append(sta_obj.lat)
                datas_2.append(sta_obj.future_ten_days_total_rain)
            elif sta_obj.future_ten_rain_total_historical_ranking == 3:
                lons_3.append(sta_obj.lon)
                lats_3.append(sta_obj.lat)
                datas_3.append(sta_obj.future_ten_days_total_rain)
            elif sta_obj.future_ten_rain_total_historical_ranking == 4:
                lons_4.append(sta_obj.lon)
                lats_4.append(sta_obj.lat)
                datas_4.append(sta_obj.future_ten_days_total_rain)
            elif sta_obj.future_ten_rain_total_historical_ranking == 5:
                lons_5.append(sta_obj.lon)
                lats_5.append(sta_obj.lat)
                datas_5.append(sta_obj.future_ten_days_total_rain)
            else:
                lons_6.append(sta_obj.lon)
                lats_6.append(sta_obj.lat)
                datas_6.append(sta_obj.future_ten_days_total_rain)
        pic_name = "{}_西南地区未来10天累计降水量与历史上每年相比的排名分布预报产品.png".format(
            (self.date_time - timedelta(days=1)).strftime("%y%m%d") + self.start_h)
        file_output_path = self.pic_output_path.format((self.date_time - timedelta(days=1)).strftime("%Y%m%d"))
        if not os.path.exists(file_output_path):
            os.makedirs(file_output_path)
        draw = figure_pic.DrawImages(extent=[80, 110, 20, 35], x_scale=5, y_scale=5)
        draw.set_title("西南地区未来10天累计降水量与历史上每年相比的排名分布预报产品  {}".format(
            (self.date_time - timedelta(days=1)).strftime("%y%m%d") + self.start_h))
        draw.add_one_or_multi_province(add_china_shp=True, add_world_shp=False, add_sub_nine_dashed=False)
        v_min, v_max = 0, 60

        scatter_style_1 = [lons_1, lats_1, datas_1, v_min, v_max, plt.get_cmap("Set1"), "1"]
        scatter_style_2 = [lons_2, lats_2, datas_2, v_min, v_max, plt.get_cmap("Set1"), "2"]
        scatter_style_3 = [lons_3, lats_3, datas_3, v_min, v_max, plt.get_cmap("Set1"), "3"]
        scatter_style_4 = [lons_4, lats_4, datas_4, v_min, v_max, plt.get_cmap("Set1"), "4"]
        scatter_style_5 = [lons_5, lats_5, datas_5, v_min, v_max, plt.get_cmap("Set1"), "5"]
        scatter_style_6 = [lons_6, lats_6, datas_6, v_min, v_max, plt.get_cmap("Set1"), ""]
        scatter = [scatter_style_1, scatter_style_2, scatter_style_3, scatter_style_4, scatter_style_5, scatter_style_6]
        draw.add_scatter(scatter)
        draw.add_color_bar_set(v_min, v_max)
        draw.save_fig(os.path.join(file_output_path, pic_name))

    def pic_draw_7(self):
        """

        Returns:

        """
        start, end = [], []
        region_begin_rainy_day = None
        region_end_rainy_day = None
        for sta_obj in self.sta_obj_list:
            if sta_obj.obs_begin_rainy_day is not None:
                start.append(sta_obj.obs_begin_rainy_day)
            else:
                if sta_obj.fst_begin_rainy_day is not None:
                    start.append(sta_obj.fst_begin_rainy_day)
            if sta_obj.obs_end_rainy_day is not None:
                end.append(sta_obj.obs_end_rainy_day)
            else:
                if sta_obj.fst_end_rainy_day is not None:
                    end.append(sta_obj.fst_end_rainy_day)

        rate_begin = dict(Counter(i for i in sorted([str(a) for a in ['20' + a for a in start]], reverse=False)))
        end_begin = dict(Counter(i for i in sorted([str(b) for b in end], reverse=False)))
        sum_vb, sum_ve = 0, 0
        for k_b, v_b in rate_begin.items():
            if datetime.strptime(k_b, '%Y%m%d') >= datetime(self.date_time.year, 4, 17):
                sum_vb += v_b
                if sum_vb >= int(len(self.sta_obj_list) * 0.6):
                    region_begin_rainy_day = k_b
                    break
        for k_e, v_e in end_begin.items():
            if datetime.strptime(k_e, '%Y%m%d') >= datetime(self.date_time.year, 9, 17):
                sum_ve += v_e
                if sum_ve >= int(len(self.sta_obj_list) * 0.6):
                    region_end_rainy_day = k_e
                    break
        # 计算雨季持续时间和降水强度
        if region_begin_rainy_day:
            pre_start = region_begin_rainy_day
        else:
            pre_start = '未检测出'
        if region_end_rainy_day:
            pre_end = region_end_rainy_day
        else:
            pre_end = '未检测出'
        if region_begin_rainy_day and region_end_rainy_day:
            pre_lenth = (pd.to_datetime(pre_end) - pd.to_datetime(pre_start)).days
            pre_strength, pre_strength_class = self.calculate_pre_strength(region_begin_rainy_day, region_end_rainy_day)
        else:
            pre_lenth = '未检测出'
            pre_strength, pre_strength_class = 0, 0

        pic_name = "{}_西南地区监测图.png".format((self.date_time - timedelta(days=1)).strftime("%y%m%d") + self.start_h)
        file_output_path = self.pic_output_path.format((self.date_time - timedelta(days=1)).strftime("%Y%m%d"))
        fig = plt.figure(figsize=(8, 5))
        plt.text(0.01, 0.95, "监测指标：", size=30, rotation=0, ha="left", va="top")
        plt.text(0.01, 0.80, "雨季开始日期为： {}".format(pre_start), size=15, rotation=0, ha="left", va="top")
        plt.text(0.01, 0.70, "雨季结束日期为： {}".format(pre_end), size=15, rotation=0, ha="left", va="top")
        plt.text(0.01, 0.60, "雨季长度为： {} 天".format(pre_lenth), size=15, rotation=0, ha="left", va="top")
        plt.text(0.01, 0.50, "雨季总降水量为： {} mm".format('%.1f' % self.region_pre()), size=15, rotation=0, ha="left",
                 va="top")
        plt.text(0.01, 0.40, "雨季降水强度为： {}  强度等级： {}".format('%.1f' % pre_strength, pre_strength_class), size=15,
                 rotation=0, ha="left", va="top")
        plt.text(0.01, 0.30, "===================================", size=15, rotation=0, ha="left", va="top")
        plt.text(0.01, 0.20, "气候降水标准偏差为： {} mm".format('%.1f' % self.calculate_std()), size=15, rotation=0, ha="left",
                 va="top")
        plt.text(0.01, 0.10, "气候平均降水量为： {} mm".format('%.1f' % np.sum(list(self.read_tp_daily_mean().values()))),
                 size=15, rotation=0, ha="left", va="top")
        plt.xticks([])
        plt.yticks([])
        plt.gca().spines['bottom'].set_linewidth(2)
        plt.gca().spines['left'].set_linewidth(2)
        plt.gca().spines['top'].set_linewidth(2)
        plt.gca().spines['right'].set_linewidth(2)
        plt.savefig(os.path.join(file_output_path, pic_name))
        plt.close(fig)

    def read_tp_daily_mean(self):
        """
        读取1991-2020年日平均降水数据，并返回
        Returns:
            mean_data  dict

        """
        mean_data = {}
        try:
            dmr = pd.read_csv('./file/his_area_daily_mean_{}_1991-2020.txt'.format(self.start_h), header=0,
                              delimiter='\t', names=['month', 'day', 'rain'])
            for value in dmr.values:
                key = "{0:02d}{1:02d}".format(int(value[0]), int(value[1]))
                mean_data[key] = value[2]
        except Exception as ex:
            logger.error(ex)
        return mean_data

    def calculate_std(self):
        """
        计算1990-2020年降水量标准差
        Returns:
            std_pre   value
        """
        std_pre = 0
        try:
            sum = 0
            pre_values = list(self.read_tp_daily_mean().values())
            for i in pre_values:
                sum += pow((i - np.mean(list(self.read_tp_daily_mean().values()))), 2)
            std_pre = pow(sum / len(pre_values), 1 / 2)
        except Exception as ex:
            logger.error(ex)

        return std_pre

    def region_pre(self):
        """
        计算区域雨季降水量
        Returns:
             total_pre  value
        """

        total_pre = 0
        try:
            temp_datas = []
            for sta_obj in self.sta_obj_list:
                if sta_obj.obs_end_rainy_day is not None or sta_obj.fst_end_rainy_day is not None:
                    temp_datas.append(sta_obj.rainy_days_total_rain)
            if len(temp_datas) > 0:
                sta_datas = list(filter(lambda x: x > 0, temp_datas))
                total_pre = sum(sta_datas) / len(sta_datas)
            else:
                total_pre = 0
        except Exception as ex:
            logger.error(ex)

        return total_pre

    def calculate_pre_strength(self, region_begin_rainy_day, region_end_rainy_day):
        """
        计算区域雨季降水强度
        Returns:

        """
        Z = 0
        Class = 0
        try:
            P = self.region_pre()
            P_Mean, std_pre = self.read_pre_daily_mean(region_begin_rainy_day, region_end_rainy_day)

            Z = (P - P_Mean) / std_pre
            if Z <= -1.5:
                Class = 1
            elif Z <= -0.5 and Z > -1.5:
                Class = 2
            elif Z < 0.5 and Z > -0.5:
                Class = 3
            elif Z < 1.5 and Z >= 0.5:
                Class = 4
            else:
                Class = 5

        except Exception as ex:
            logger.error(ex)
        return Z, Class

    def read_pre_daily_mean(self, region_begin_rainy_day, region_end_rainy_day):
        """
        读取区域雨季降水气候平均值，并返回
        Returns:

        """
        region_pre_mean = None
        region_pre_std = None
        try:
            region_mean_data = []
            dmr = pd.read_csv('./file/his_area_daily_mean_{}_1991-2020.txt'.format(self.start_h), header=0,
                              delimiter='\t', names=['month', 'day', 'rain'])
            for value in dmr.values:
                key = "{0:02d}{1:02d}".format(int(value[0]), int(value[1]))
                if key >= region_begin_rainy_day[4:] and key <= region_end_rainy_day[4:]:
                    region_mean_data.append(value[2])
            region_pre_mean = np.sum(region_mean_data)
            region_pre_std = np.std(region_mean_data)
        except Exception as ex:
            logger.error(ex)
        return region_pre_mean, region_pre_std

    def read_tp_rolling_mean(self):
        """
        读取降水5天滑动平均数据，并返回
        Returns:
            mean_data

        """
        mean_data = {}
        try:
            rmr = pd.read_csv('./file/his_area_rolling_5_mean_1991_2020.txt', header=0, delimiter='\t',
                              names=['month', 'day', 'rain'])
            for value in rmr.values:
                key = "{0:02d}{1:02d}".format(int(value[0]), int(value[1]))
                mean_data[key] = value[2]
        except Exception as ex:
            logger.error(ex)
        return mean_data


if __name__ == '__main__':
    obj = PictureDrawTask(list(), datetime(2022, 4, 24), "08", "../output/pic/{}/")
    obj.pic_draw_7()