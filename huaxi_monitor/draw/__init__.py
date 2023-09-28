#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta
import numpy as np
import os
import cfg
import seaborn as sns
from utils import MICAPS4 as M4
import pandas as pd
from sta_info.Constants import *
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from draw import figure_pic
from utils import log_configure as log

plt.rcParams['font.sans-serif'] = ['SIMHEI']  # 显示中文标签
plt.rcParams['axes.unicode_minus'] = False

logger = log.Logger(log_path="./log/pic_draw_tasks")

def read_m4_file(filedata):
    '''
    Infile：M4文件
    Outfile：
    '''
    lat_lon_data = M4.open_m4(filedata, 'GBK')
    latitudes_file = np.linspace(lat_lon_data.start_lat, lat_lon_data.end_lat, lat_lon_data.lat_count)
    longitudes_file = np.linspace(lat_lon_data.start_lon, lat_lon_data.end_lon, lat_lon_data.lon_count)
    data_file = lat_lon_data.data

    return data_file, longitudes_file, latitudes_file

class PictureDrawTask:

    def __init__(self, sta_obj_list_08, date_time, start_h, pic_output_path):
        """

        Args:
            sta_obj_list:
            date_time:
            start_h:
            pic_output_path:
        """
        self.sta_obj_list_08 = sta_obj_list_08
        self.date_time = date_time
        self.start_h = start_h
        self.pic_output_path = pic_output_path
        self._save_rainy_days_begin_to_file()
        self._save_rainy_days_end_to_file()

    def pic_draw_1(self):
        """

        Returns:

        """
        South_Y_lons, South_Y_lats = [], []
        South_N_lons, South_N_lats = [], []

        North_Y_lons, North_Y_lats = [], []
        North_N_lons, North_N_lats = [], []

        First_rain_values = self.sta_obj_list_08.sta_obj_dict.get(self.date_time.strftime('%y%m%d'))
        for i in First_rain_values:
            if i[2] >= 0.1:
                if i[3] == '南区':
                    South_Y_lons.append(i[0])
                    South_Y_lats.append(i[1])
                else:
                    North_Y_lons.append(i[0])
                    North_Y_lats.append(i[1])
            else:
                if i[3] == '南区':
                    South_N_lons.append(i[0])
                    South_N_lats.append(i[1])
                else:
                    North_N_lons.append(i[0])
                    North_N_lats.append(i[1])

        pic_name = "{}_华西秋雨未来24h降雨站分布.png".format((self.date_time - timedelta(days=1)).strftime("%y%m%d") + self.start_h)
        file_output_path = self.pic_output_path.format((self.date_time - timedelta(days=1)).strftime("%Y%m%d"))
        if not os.path.exists(file_output_path):
            os.makedirs(file_output_path)

        draw = figure_pic.DrawImages(extent=[101, 113, 25, 37], x_scale=3, y_scale=3)
        draw.set_title(
            "华西秋雨{}时24h降雨站（绿色）分布监测".format((self.date_time - timedelta(days=1)).strftime("%y%m%d") + self.start_h))
        draw.add_one_or_multi_province(add_china_shp=True, add_world_shp=False, add_sub_nine_dashed=False)

        scatter_style_1 = [South_N_lons, South_N_lats, 100, '*', "r", '南区日雨量<0.1mm']
        scatter_style_2 = [South_Y_lons, South_Y_lats, 100, '*', "g", '南区日雨量>=0.1mm']
        scatter_style_3 = [North_N_lons, North_N_lats, 100, '^', "r", '北区区日雨量<0.1mm']
        scatter_style_4 = [North_Y_lons, North_Y_lats, 100, '^', "g", '北区日雨量>=0.1mm']
        scatter = [scatter_style_1, scatter_style_2, scatter_style_3, scatter_style_4]
        draw.add_scatter(scatter)

        num_s_y, num_s_n = len(South_Y_lons), len(South_N_lons)
        num_n_y, num_n_n = len(North_Y_lons), len(North_N_lons)
        per_1 = "%.1f%%" % (num_s_y / (num_s_y + num_s_n) * 100)
        per_2 = "%.1f%%" % (num_n_y / (num_n_y + num_n_n) * 100)
        per_3, per_4 = None, None
        if num_s_y / (num_s_y + num_s_n) >= 0.5:
            per_3 = '秋雨日'
        else:
            per_3 = '非秋雨日'

        if num_n_y / (num_n_y + num_n_n) >= 0.5:
            per_4 = '秋雨日'
        else:
            per_4 = '非秋雨日'

        annotate_style_1 = [101.2, 36.6, "南区日雨量>=0.1mm站数比率为:{}".format(per_1), "black", 18]
        annotate_style_2 = [101.2, 36.2, "北区日雨量>=0.1mm站数比率为:{}".format(per_2), "black", 18]
        annotate_style_3 = [101.2, 35.8, "南区:{} 北区:{}".format(per_3, per_4), "black", 18]

        annotate = [annotate_style_1, annotate_style_2, annotate_style_3]
        draw.add_annotate(annotate)
        draw.add_legend()
        draw.save_fig(os.path.join(file_output_path, pic_name))

    def pic_draw_2(self):
        """

        Returns:

        """
        labels = []
        rain_day_obs = []
        rain_days_obs, rainys = None, None
        rain_day_fst = []
        rain_days_fst = []
        for i in range(-30, 0, 1):
            rain_days_list, no_rain_days_list = [], []
            labels.append((self.date_time + timedelta(days=i)).strftime("%d%b"))
            Input_time = (self.date_time + timedelta(days=i)).strftime('%y%m%d')
            rain_values = self.sta_obj_list_08.sta_obj_dict.get(Input_time)
            for i in rain_values:
                if i[3] == '南区':
                    if i[2] >= 0.1:
                        rain_days_list.append(i[2])
                    else:
                        no_rain_days_list.append(i[2])
            rain_days, no_rain_days = len(rain_days_list), len(no_rain_days_list)
            rain_per = 100 * rain_days / (rain_days + no_rain_days)
            rain_day_obs.append(rain_per)
            rain_day_fst.append(None)
            rain_days_fst.append(None)
            if self.sta_obj_list_08.obs_begin_rainy_day_s is not None \
                    and Input_time == self.sta_obj_list_08.obs_begin_rainy_day_s[0]:
                rainys = datetime.strptime(self.sta_obj_list_08.obs_begin_rainy_day_s[0], '%y%m%d').strftime("%d%b")
                rain_days_obs = rain_per

        for i in range(0, 15, 1):
            rain_per_f_list = []
            labels.append((self.date_time + timedelta(days=i)).strftime("%d%b"))
            Input_time = (self.date_time + timedelta(days=i)).strftime('%Y%m%d')
            for j in range(0, 51, 1):
                rain_days_list_f, no_rain_days_list_f = [], []
                rain_values = self.sta_obj_list_08.fst_dict_S.get(Input_time + '_' +  str(j))
                if rain_values is not None:
                    for k in rain_values:
                        if float(k[2]) >= 0.1:
                            rain_days_list_f.append(float(k[2]))
                        else:
                            no_rain_days_list_f.append(float(k[2]))
                    rain_days_f, no_rain_days_f = len(rain_days_list_f), len(no_rain_days_list_f)
                    rain_per_f = 100 * rain_days_f / (rain_days_f + no_rain_days_f)
                    rain_per_f_list.append(rain_per_f)
                else:
                    rain_per_f_list.append(0)

            rain_day_obs.append(0)
            rain_day_fst.append(np.mean(rain_per_f_list))
            rain_days_fst.append(rain_per_f_list)


        pic_name = "{}_华西秋雨秋雨日监测及未来15天预报.png".format(
            (self.date_time - timedelta(days=1)).strftime("%y%m%d") + self.start_h)
        file_output_path = self.pic_output_path.format((self.date_time - timedelta(days=1)).strftime("%Y%m%d"))
        if not os.path.exists(file_output_path):
            os.makedirs(file_output_path)
        plt.figure(figsize=(16, 10), dpi=300)
        ax1 = plt.subplot(211)
        ax1.plot([0, 45], [50, 50], linewidth=2, color='r', linestyle='--')
        ax1.bar(labels, rain_day_obs, 0.6, label='Observed', color="b")
        if rainys is not None:
            ax1.quiver(rainys, rain_days_obs + 20, 0, -1, color="r", scale=20)
        ax1.plot(labels,rain_day_fst, linewidth=1, label='ensemble mean', color="r",marker='o',markersize=2)
        sns.boxplot(data=rain_days_fst, width = 0.5, fliersize=1, linewidth = 1.0, flierprops={'color':'darkred','marker':'o'},
                    medianprops = {'linestyle':'--', 'color':'sandybrown'}, boxprops = {'facecolor':'steelblue'})
        ax1.set_ylabel('监测区日雨量>=0.1站数比率（%）')
        ax1.set_xticklabels(labels)
        ax1.set_title('华西秋雨南区秋雨日监测及未来15天预报')

        # 设置坐标
        ax1.set_xticks(labels)
        ax1.set_yticks(np.arange(0, 101))

        # 设置x轴主刻度间隔为5，设置x轴副刻度间隔为1
        ax1.xaxis.set_major_locator(MultipleLocator(5))
        ax1.xaxis.set_minor_locator(MultipleLocator(1))
        # 设置y轴主刻度间隔为20，设置y轴副刻度间隔为5
        ax1.yaxis.set_major_locator(MultipleLocator(20))
        ax1.yaxis.set_minor_locator(MultipleLocator(5))
        # 设置y轴数值范围
        plt.ylim(-5, 109)
        # 设置图例
        ax1.legend(loc='upper left', fontsize=10, ncol=2)
        #plt.savefig(os.path.join(file_output_path, pic_name), bbox_inches='tight')


        labels = []
        rain_day_obs = []
        rain_days_obs, rainys = None, None
        rain_day_fst = []
        rain_days_fst = []
        for i in range(-30, 0, 1):
            rain_days_list, no_rain_days_list = [], []
            labels.append((self.date_time + timedelta(days=i)).strftime("%d%b"))
            Input_time = (self.date_time + timedelta(days=i)).strftime('%y%m%d')
            rain_values = self.sta_obj_list_08.sta_obj_dict.get(Input_time)
            for i in rain_values:
                if i[3] == '北区':
                    if i[2] >= 0.1:
                        rain_days_list.append(i[2])
                    else:
                        no_rain_days_list.append(i[2])
            rain_days, no_rain_days = len(rain_days_list), len(no_rain_days_list)
            rain_per = 100 * rain_days / (rain_days + no_rain_days)
            rain_day_obs.append(rain_per)
            rain_day_fst.append(None)
            rain_days_fst.append(None)
            if self.sta_obj_list_08.obs_begin_rainy_day_n is not None  \
                    and Input_time == self.sta_obj_list_08.obs_begin_rainy_day_n[0]:
                rainys = datetime.strptime(self.sta_obj_list_08.obs_begin_rainy_day_n[0], '%y%m%d').strftime("%d%b")
                rain_days_obs = rain_per

        for i in range(0, 15, 1):
            rain_per_f_list = []
            labels.append((self.date_time + timedelta(days=i)).strftime("%d%b"))
            Input_time = (self.date_time + timedelta(days=i)).strftime('%Y%m%d')
            for j in range(0, 51, 1):
                rain_days_list_f, no_rain_days_list_f = [], []
                rain_values = self.sta_obj_list_08.fst_dict_N.get(Input_time + '_' +  str(j))
                if rain_values is not None:
                    for k in rain_values:
                        if float(k[2]) >= 0.1:
                            rain_days_list_f.append(float(k[2]))
                        else:
                            no_rain_days_list_f.append(float(k[2]))
                    rain_days_f, no_rain_days_f = len(rain_days_list_f), len(no_rain_days_list_f)
                    rain_per_f = 100 * rain_days_f / (rain_days_f + no_rain_days_f)
                    rain_per_f_list.append(rain_per_f)
                else:
                    rain_per_f_list.append(0)

            rain_day_obs.append(0)
            rain_day_fst.append(np.mean(rain_per_f_list))
            rain_days_fst.append(rain_per_f_list)

        ax2 = plt.subplot(212)
        ax2.plot([0, 45], [50, 50], linewidth=2, color='r', linestyle='--')
        ax2.bar(labels, rain_day_obs, 0.6, label='Observed', color="b")
        if rainys is not None:
            ax2.quiver(rainys, rain_days_obs + 20, 0, -1, color="r", scale=20)
        ax2.plot(labels,rain_day_fst, linewidth=1, label='ensemble mean', color="r",marker='o',markersize=2)
        sns.boxplot(data=rain_days_fst, width = 0.5, fliersize=1, linewidth = 1.0, flierprops={'color':'darkred','marker':'o'},
                    medianprops = {'linestyle':'--', 'color':'sandybrown'}, boxprops = {'facecolor':'steelblue'})
        ax2.set_ylabel('监测区日雨量>=0.1站数比率（%）')
        ax2.set_xticklabels(labels)
        ax2.set_title('华西秋雨北区秋雨日监测及未来15天预报')

        # 设置坐标
        ax2.set_xticks(labels)
        ax2.set_yticks(np.arange(0, 101))

        # 设置x轴主刻度间隔为5，设置x轴副刻度间隔为1
        ax2.xaxis.set_major_locator(MultipleLocator(5))
        ax2.xaxis.set_minor_locator(MultipleLocator(1))
        # 设置y轴主刻度间隔为20，设置y轴副刻度间隔为5
        ax2.yaxis.set_major_locator(MultipleLocator(20))
        ax2.yaxis.set_minor_locator(MultipleLocator(5))
        # 设置y轴数值范围
        plt.ylim(-5, 109)
        # 设置图例
        ax2.legend(loc='upper left', fontsize=10, ncol=2)

        plt.savefig(os.path.join(file_output_path, pic_name), bbox_inches='tight')
        plt.close()

    def pic_draw_7(self):
        """

        Returns:

        """
        labels = [] #x轴日期
        rain_day_obs = [] #实况日降水量
        rain_date = []
        fst_box = []#雨日
        rain_day_fst = []

        for j in range(-30, 0, 1):
            rain_days_list, no_rain_days_list = [], []
            labels.append((self.date_time + timedelta(days=j)).strftime("%d%b"))
            Input_time = (self.date_time + timedelta(days=j)).strftime('%y%m%d')
            rain_values = self.sta_obj_list_08.sta_obj_dict.get(Input_time)
            for i in rain_values:
                if i[3] == '南区' and i[2] >= 0.1:
                    rain_days_list.append(i[2])
                elif i[3] == '南区':
                    no_rain_days_list.append(i[2])
            rain_sth = (np.mean(rain_days_list) * len(rain_days_list) + np.mean(no_rain_days_list) * len(no_rain_days_list))/(len(rain_days_list)+len(no_rain_days_list))
            rain_days, no_rain_days = len(rain_days_list), len(no_rain_days_list)
            rain_per = 100 * rain_days / (rain_days + no_rain_days)
            if rain_per >= 50:
                rain_date.append(26)
            else:
                rain_date.append(None)
            rain_day_obs.append(rain_sth)
            rain_day_fst.append(None)
            fst_box.append([])

        for j in range(0, 15, 1):
            rain_days_list_f, no_rain_days_list_f = [], []
            sta_allT = []
            labels.append((self.date_time + timedelta(days=j)).strftime("%d%b"))
            Input_time = (self.date_time + timedelta(days=j)).strftime('%y%m%d')
            rain_values = self.sta_obj_list_08.sta_obj_dict.get(Input_time)
            for i in rain_values:
                if i[3] == '南区' and i[2] >= 0.1:
                    rain_days_list_f.append(i[2])
                elif i[3] == '南区':
                    no_rain_days_list_f.append(i[2])
            if len(rain_days_list_f) == 0:
                rain_sth = 0
            else:
                rain_sth = np.mean(rain_days_list_f)
            rain_day_fst.append(rain_sth)
            rain_day_obs.append(0)
            rain_date.append(None)
            value_l = self.sta_obj_list_08.sta_obj_dict.get(Input_time)
            for K in range(373):
                if value_l[K][3] == '南区':
                    sta_allT.append(value_l[K][2])
            fst_box.append(sta_allT)

        pic_name = "{}_华西秋雨降雨量监测及预报.png".format(
            (self.date_time - timedelta(days=1)).strftime("%y%m%d") + self.start_h)
        file_output_path = self.pic_output_path.format((self.date_time - timedelta(days=1)).strftime("%Y%m%d"))
        if not os.path.exists(file_output_path):
            os.makedirs(file_output_path)
        plt.figure(figsize=(16, 10), dpi=300)
        ax1 = plt.subplot(211)
        ax1.set_yticks(np.arange(0, 30))
        ax1.bar(labels, rain_day_obs, 0.6, label='obs', color="b")
        ax1.scatter(labels, rain_date, label='obs_rainday', color="black")
        ax1.plot(labels,rain_day_fst, linewidth=1, label='ensemble mean', color="r",marker='o',markersize=2)
        sns.boxplot(data=fst_box, width = 0.5, fliersize=1, linewidth = 1.0, flierprops={'color':'darkred','marker':'o'},
                    medianprops = {'linestyle':'--', 'color':'sandybrown'}, boxprops = {'facecolor':'steelblue'})


        #boxplot(fst_box, widths = 0.5, flierprops={'markersize': '1'}, showfliers=True, patch_artist=True)
        ax1.set_xticklabels(labels)
        ax1.set_ylabel('rainfall (mm)')
        ax1.set_title('华西秋雨南区降雨量监测')
        # 设置x轴主刻度间隔为5，设置x轴副刻度间隔为1
        ax1.xaxis.set_major_locator(MultipleLocator(2))
        # 设置y轴主刻度间隔为20，设置y轴副刻度间隔为5
        ax1.yaxis.set_major_locator(MultipleLocator(5))
        # 设置y轴数值范围
        plt.ylim(0, 30)
        # 设置图例
        ax1.legend(loc='upper left', fontsize=10, ncol=1)


        labels = [] #x轴日期
        rain_day_obs = [] #实况日降水量
        rain_date = []
        fst_box = []#雨日
        rain_day_fst = []
        for j in range(-30, 0, 1):
            rain_days_list, no_rain_days_list = [], []
            labels.append((self.date_time + timedelta(days=j)).strftime("%d%b"))
            Input_time = (self.date_time + timedelta(days=j)).strftime('%y%m%d')
            rain_values = self.sta_obj_list_08.sta_obj_dict.get(Input_time)
            for i in rain_values:
                if i[3] == '北区' and i[2] >= 0.1:
                    rain_days_list.append(i[2])
                elif i[3] == '北区':
                    no_rain_days_list.append(i[2])
            rain_sth = (np.mean(rain_days_list) * len(rain_days_list) + np.mean(no_rain_days_list) * len(no_rain_days_list))/(len(rain_days_list)+len(no_rain_days_list))
            rain_days, no_rain_days = len(rain_days_list), len(no_rain_days_list)
            rain_per = 100 * rain_days / (rain_days + no_rain_days)
            if rain_per >= 50:
                rain_date.append(26)
            else:
                rain_date.append(None)
            rain_day_obs.append(rain_sth)
            rain_day_fst.append(None)
            fst_box.append([])

        for j in range(0, 15, 1):
            rain_days_list_f, no_rain_days_list_f = [], []
            sta_allT = []
            labels.append((self.date_time + timedelta(days=j)).strftime("%d%b"))
            Input_time = (self.date_time + timedelta(days=j)).strftime('%y%m%d')
            rain_values = self.sta_obj_list_08.sta_obj_dict.get(Input_time)
            for i in rain_values:
                if i[3] == '北区' and i[2] >= 0.1:
                    rain_days_list_f.append(i[2])
                elif i[3] == '北区':
                    no_rain_days_list_f.append(i[2])
            if len(rain_days_list_f) == 0:
                rain_sth = 0
            else:
                rain_sth = np.mean(rain_days_list_f)
            rain_day_fst.append(rain_sth)
            rain_day_obs.append(0)
            rain_date.append(None)
            value_l = self.sta_obj_list_08.sta_obj_dict.get(Input_time)
            for K in range(373):
                if value_l[K][3] == '北区':
                    sta_allT.append(value_l[K][2])
            fst_box.append(sta_allT)
        ax2 = plt.subplot(212)
        ax2.set_yticks(np.arange(0, 30))
        ax2.bar(labels, rain_day_obs, 0.6, label='obs', color="b")
        ax2.scatter(labels, rain_date, label='obs_rainday', color="black")
        ax2.plot(labels,rain_day_fst, linewidth=1, label='ensemble mean', color="r",marker='o',markersize=2)
        sns.boxplot(data=fst_box, width = 0.5, fliersize=1, linewidth = 1.0, flierprops={'color':'darkred','marker':'o'},
                    medianprops = {'linestyle':'--', 'color':'sandybrown'}, boxprops = {'facecolor':'steelblue'})
        ax2.set_xticklabels(labels)
        ax2.set_ylabel('rainfall (mm)')
        ax2.set_title('华西秋雨北区降雨量监测')
        # 设置x轴主刻度间隔为5，设置x轴副刻度间隔为1
        ax2.xaxis.set_major_locator(MultipleLocator(2))
        # 设置y轴主刻度间隔为20，设置y轴副刻度间隔为5
        ax2.yaxis.set_major_locator(MultipleLocator(5))
        # 设置y轴数值范围
        plt.ylim(0, 30)
        # 设置图例
        ax2.legend(loc='upper left', fontsize=10, ncol=1)

        plt.savefig(os.path.join(file_output_path, pic_name), bbox_inches='tight')
        plt.close()

    def pic_draw_3(self):

        if self.sta_obj_list_08.begin_rainy_date is not None:
            rain_begin = self.sta_obj_list_08.begin_rainy_date
        else:
            rain_begin = None
        rain_end = self.date_time
        total_rain_value = np.zeros(373)
        temp_lon = None
        temp_lat = None
        if rain_begin and rain_end is not None:
            while rain_begin <= rain_end:
                begin_time = rain_begin.strftime('%y%m%d')
                temp_all_list = self.sta_obj_list_08.sta_obj_dict.get(begin_time)
                temp_lon = [i[0] for i in temp_all_list]
                temp_lat = [i[1] for i in temp_all_list]
                total_rain_value += np.array([i[2] for i in temp_all_list])
                rain_begin += timedelta(days=1)
        else:
            return

        pic_name = "{}_华西秋雨自开始日期至当前的降水累计分布的监测.png".format(
            (self.date_time - timedelta(days=1)).strftime("%y%m%d") + self.start_h)
        file_output_path = self.pic_output_path.format((self.date_time - timedelta(days=1)).strftime("%Y%m%d"))
        if not os.path.exists(file_output_path):
            os.makedirs(file_output_path)
        draw = figure_pic.DrawImages(extent=[101, 113, 25, 37], x_scale=3, y_scale=3)
        draw.set_title("华西秋雨{}-{}累计降水量分布监测".format(self.sta_obj_list_08.begin_rainy_date.strftime("%d%b"),(self.date_time - timedelta(days=1)).strftime("%d%b")))
        draw.add_one_or_multi_province(add_china_shp=True, add_world_shp=False, add_sub_nine_dashed=False)
        v_min, v_max = 0, 1000
        scatter_style_1 = [temp_lon, temp_lat, total_rain_value, v_min, v_max]
        scatter = [scatter_style_1]
        draw.add_scatter(scatter)
        draw.add_color_bar(v_min, v_max, 18,'')
        draw.save_fig(os.path.join(file_output_path, pic_name))
        plt.close()

    def pic_draw_4(self):

        labels = []
        start_date, end_date = [], []
        file_path = os.path.join(os.path.dirname(os.path.split(os.path.abspath(__file__))[0]), 'file', 'huaxi_his_date.txt')
        f_start = open(file_path, "r")
        datas_start = f_start.readlines()

        for i in datas_start:
            Year, beginT, endT = i.strip().split('\t')
            labels.append(Year)
            beginT_num = (datetime.strptime(Year + beginT, '%Y%m%d') - datetime.strptime(Year + '0101', '%Y%m%d')).days - 3
            endT_num = (datetime.strptime(Year + endT, '%Y%m%d') - datetime.strptime(Year + '0101', '%Y%m%d')).days - 3
            start_date.append(beginT_num)
            end_date.append(endT_num)

        labels.insert(0, '1960')
        start_date.insert(0, 0)
        end_date.insert(0, 0)

        pic_name = "{}_华西秋雨开始日期变化.png".format(
            (self.date_time - timedelta(days=1)).strftime("%y%m%d") + self.start_h)
        file_output_path = self.pic_output_path.format((self.date_time - timedelta(days=1)).strftime("%Y%m%d"))
        if not os.path.exists(file_output_path):
            os.makedirs(file_output_path)
        plt.figure(figsize=(16, 10))

        ax1 = plt.subplot(211)
        ax1.plot([0, 61], [np.mean(start_date), np.mean(start_date)], linewidth=2, color='r', linestyle='--')
        ax1.bar(labels, start_date, 0.6, color="b")
        ax1.set_ylabel('华西秋雨开始日期')
        a, b = 212, 263
        List_start_tmp = list(pd.date_range(datetime(1961, 1, 1) + timedelta(days=a), datetime(1961, 1, 1) + timedelta(days=b), freq='10D'))
        List_start = [i.strftime('%m-%d') for i in List_start_tmp]
        # 设置坐标
        ax1.set_xticks(labels)
        ax1.set_yticklabels(List_start)
        # 设置x轴主刻度间隔为5，设置x轴副刻度间隔为1
        ax1.xaxis.set_major_locator(MultipleLocator(10))
        ax1.xaxis.set_minor_locator(MultipleLocator(5))
        # 设置y轴数值范围
        plt.ylim(a, b)


        ax2 = plt.subplot(212)
        ax2.plot([0, 61], [np.mean(end_date), np.mean(end_date)], linewidth=2, color='r', linestyle='--')
        ax2.bar(labels, end_date, 0.6, color="b")
        ax2.set_ylabel('华西秋雨结束日期')
        a, b = 243, 344
        List_end_tmp = list(
            pd.date_range(datetime(2022, 1, 1) + timedelta(days=a), datetime(2022, 1, 1) + timedelta(days=b), freq='20D'))
        List_end = [i.strftime('%m-%d') for i in List_end_tmp]
        # 设置坐标
        ax2.set_xticks(labels)
        ax2.set_yticklabels(List_end)
        # 设置x轴主刻度间隔为5，设置x轴副刻度间隔为1
        ax2.xaxis.set_major_locator(MultipleLocator(10))
        ax2.xaxis.set_minor_locator(MultipleLocator(5))
        # 设置y轴数值范围
        plt.ylim(a, b)

        plt.savefig(os.path.join(file_output_path, pic_name), bbox_inches='tight')
        plt.close()

    def pic_draw_5(self):

        rain_value = np.zeros(373)
        temp_lon, temp_lat = None, None
        temp_time = self.date_time - timedelta(days=1)
        temp_all_list = self.sta_obj_list_08.sta_obj_dict.get(temp_time.strftime('%y%m%d'))
        temp_lon = [i[0] for i in temp_all_list]
        temp_lat = [i[1] for i in temp_all_list]
        rain_value = [i[2] for i in temp_all_list]

        pic_name = "{}_过去24小时集合平均预报降水与实况观测.png".format(
            (self.date_time - timedelta(days=1)).strftime("%y%m%d") + self.start_h)
        file_output_path = self.pic_output_path.format((self.date_time - timedelta(days=1)).strftime("%Y%m%d"))
        if not os.path.exists(file_output_path):
            os.makedirs(file_output_path)
        draw = figure_pic.DrawImages(extent=[101, 113, 25, 37], x_scale=3, y_scale=3)
        draw.set_title("{}起报24时效 {}时降水观测与集合平均预报".format(temp_time.strftime('%Y%m%d')+self.start_h, self.date_time.strftime('%y%m%d')+self.start_h))
        draw.add_one_or_multi_province(add_china_shp=True, add_world_shp=False, add_sub_nine_dashed=False)

        file_name = "grid24_" + (self.date_time-timedelta(days=1)).strftime('%Y%m%d') + self.start_h + ".024"
        cfg_dict = cfg.Config("./config/basic_cfg_local.ini").cfg_dict
        fst_data_path = cfg_dict["INPUT_PATH"]["fst_data_path"]
        file_path = os.path.join(fst_data_path, file_name)
        if os.path.exists(file_path):
            data_file, longs, lats = read_m4_file(file_path)
            grid_lons, grid_lats = np.meshgrid(longs, lats)
            levels = [0.1, 5, 10, 15, 20, 25, 30, 35, 40, 50, 60]
            draw.add_contourf(grid_lons, grid_lats, data_file, levels = levels, label='EC_e')

            v_min, v_max = 0, 60
            scatter_style_1 = [temp_lon, temp_lat, rain_value, v_min, v_max]
            scatter = [scatter_style_1]
            draw.add_scatter(scatter)
            draw.add_color_bar(v_min, v_max, 18, label='Obs')

            draw.save_fig(os.path.join(file_output_path, pic_name))
            plt.close()
        else:
            print(file_path + '  文件缺失')

    def pic_draw_6(self):
        """

        Returns:

        """
        date_value = self.sta_obj_list_08.begin_rainy_date
        if date_value is not None:
            if date_value + timedelta(days=4) < self.date_time:
                rain_begin = date_value.strftime('%Y%m%d')
            else:
                rain_begin = date_value.strftime('%Y%m%d') + ' (预报)'
        else:
            rain_begin = '未检测出'

        date_value_e = self.sta_obj_list_08.end_rain_date
        if self.date_time + timedelta(days=10) >= self.date_time.replace(month=11, day=30):
            if date_value_e is not None:
                if date_value_e < self.date_time:
                    rain_end = date_value_e.strftime('%Y%m%d')
                else:
                    rain_end = date_value_e.strftime('%Y%m%d') + ' (预报)'
            else:
                rain_end = '未检测出'
        else:
            rain_end = date_value_e.strftime('%Y%m%d') + ' (临时)'

        if self.sta_obj_list_08.rainy_day_len is not None:
            rain_len = self.sta_obj_list_08.rainy_day_len
        else:
            rain_len = '未检测出'

        if self.sta_obj_list_08.total_rain is not None:
            total_rain = self.sta_obj_list_08.total_rain
        else:
            total_rain = 0

        if self.sta_obj_list_08.III and self.sta_obj_list_08.IIII is not None:
            rain_strength, rain_strength_Lev = self.sta_obj_list_08.III, self.sta_obj_list_08.IIII
        else:
            rain_strength, rain_strength_Lev = 0, None

        if self.start_h == '08':
            rain_mean = Climatic_Mean_AutumnRain_value_08
            rain_std = Climatic_Std_AutumnRain_value_08
        else:
            rain_mean = Climatic_Mean_AutumnRain_value_20
            rain_std = Climatic_Std_AutumnRain_value_20

        pic_name = "{}_华西地区监测图.png".format((self.date_time - timedelta(days=1)).strftime("%y%m%d") + self.start_h)
        file_output_path = self.pic_output_path.format((self.date_time - timedelta(days=1)).strftime("%Y%m%d"))
        fig = plt.figure(figsize=(8, 5))
        plt.text(0.01, 0.95, "监测指标：", size=30, rotation=0, ha="left", va="top")
        plt.text(0.01, 0.80, "华西秋雨开始日期为： {}".format(rain_begin), size=15, rotation=0, ha="left", va="top")
        plt.text(0.01, 0.70, "华西秋雨结束日期为： {}".format(rain_end), size=15, rotation=0, ha="left", va="top")
        plt.text(0.01, 0.60, "华西秋雨期长度为： {} 天".format(rain_len), size=15, rotation=0, ha="left", va="top")
        plt.text(0.01, 0.50, "华西秋雨量为： {} mm".format('%.1f' % total_rain), size=15, rotation=0, ha="left", va="top")
        plt.text(0.01, 0.40, "华西秋雨综合强度指数为： {}  强度等级： {}".format('%.1f' % rain_strength, rain_strength_Lev), size=15,
                 rotation=0, ha="left", va="top")
        plt.text(0.01, 0.30, "===================================", size=15, rotation=0, ha="left", va="top")
        plt.text(0.01, 0.20, "华西秋雨量的气候均方差为： {} mm".format('%.1f' % rain_std), size=15, rotation=0, ha="left",
                 va="top")
        plt.text(0.01, 0.10, "华西秋雨量的气候平均值为： {} mm".format('%.1f' % rain_mean),
                 size=15, rotation=0, ha="left", va="top")
        plt.xticks([])
        plt.yticks([])
        plt.gca().spines['bottom'].set_linewidth(2)
        plt.gca().spines['left'].set_linewidth(2)
        plt.gca().spines['top'].set_linewidth(2)
        plt.gca().spines['right'].set_linewidth(2)
        plt.savefig(os.path.join(file_output_path, pic_name), bbox_inches='tight')
        plt.close(fig)

    def _save_rainy_days_begin_to_file(self):
        results = []
        date_value = self.sta_obj_list_08.begin_rainy_date
        if date_value is not None:
            if date_value + timedelta(days=4) < self.date_time:
                results.append(date_value.strftime('%Y%m%d'))
            else:
                results.append(date_value.strftime('%Y%m%d') + ' (预报)')
        else:
            pass

        if "08" == self.start_h:
            with open("./file/statistics/obs_statistics_begin_08.txt", "w") as f:
                f.writelines(results)
        if "20" == self.start_h:
            with open("./file/statistics/obs_statistics_begin_20.txt", "w") as f:
                f.writelines(results)

    def _save_rainy_days_end_to_file(self):
        results = []
        date_value = self.sta_obj_list_08.end_rain_date
        if date_value is not None:
            if date_value < self.date_time:
                rain_end = date_value.strftime('%Y%m%d')
                results.append(rain_end)
            else:
                rain_end = date_value.strftime('%Y%m%d') + ' (预报)'
                results.append(rain_end)

        if "08" == self.start_h:
            with open("./file/statistics/obs_statistics_end_08.txt", "w") as f:
                f.writelines(results)
        if "20" == self.start_h:
            with open("./file/statistics/obs_statistics_end_20.txt", "w") as f:
                f.writelines(results)
