# -- coding: utf-8 --
# @Time : 2023/7/12 10:58
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : plot_his.py
# @Software: PyCharm
import os, sys
import logging
import numpy as np
import pandas as pd
from config_ptype import *
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
plt.rcParams.update({
    'font.family': 'simsun',
    'font.sans-serif': 'Times New Roman',
    'font.size': 18
    })
plt.rcParams['axes.unicode_minus']=False
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

his_path = r'/share/DATASOURCE/PTYPE/STATIS_HIS/{rpt:%Y%m}/{rpt:%Y%m_%H}_{cst:03d}_{label}.csv'
png_path_ptype = r'/share/DATASOURCE/PTYPE/IMAGES/{rpt:%Y%m%d}/{rpt:%Y%m%d%H}.{cst:03d}.ptype.png'
png_path_ptype_prob = r'/share/DATASOURCE/PTYPE/IMAGES/{rpt:%Y%m%d}/{rpt:%Y%m%d%H}.{cst:03d}.{label}.prob.png'

def draw_ptype_Ppt(report_time, cst, outpath, var):
    if report_time.day < 16:
        label = 'low'
    else:
        label = 'up'
    his_file = his_path.format(rpt=report_time, cst=int(cst), label=label)
    out_file = outpath.format(rpt=report_time, cst=int(cst), label=var)
    try:
        csv_df = pd.read_csv(his_file)
        obs_time_str = (report_time + timedelta(hours=int(cst))).strftime('%Y-%m-%d %H:00:00')
        df1 = csv_df[csv_df['obs_time'] == obs_time_str][var + '-0']
        df2 = csv_df[csv_df['obs_time'] == obs_time_str][var + '-1']
        df3 = csv_df[csv_df['obs_time'] == obs_time_str][var + '-2']
        df4 = csv_df[csv_df['obs_time'] == obs_time_str][var + '-3']
        df5 = csv_df[csv_df['obs_time'] == obs_time_str][var + '-4']
        dict1 = {
            '无降水1': len(df1[(df1>=0) & (df1<0.2)]),'无降水2': len(df1[(df1>=0.2) & (df1<0.4)]),
            '无降水3': len(df1[(df1>=0.4) & (df1<0.6)]),'无降水4': len(df1[(df1>=0.6) & (df1<0.8)]),
            '无降水5': len(df1[(df1>=0.8) & (df1<=1)])
        }
        dict2 = {
            '雨1': len(df2[(df2 >= 0) & (df2 < 0.2)]),'雨2': len(df2[(df2>=0.2) & (df2<0.4)]),
            '雨3': len(df2[(df2 >= 0.4) & (df2 < 0.6)]),'雨4': len(df2[(df2>=0.6) & (df2<0.8)]),
            '雨5': len(df2[(df2 >= 0.8) & (df2 <= 1)])
        }
        dict3 = {
            '雨夹雪1': len(df3[(df3 >= 0) & (df3 < 0.2)]),'雨夹雪2': len(df3[(df3>=0.2) & (df3<0.4)]),
            '雨夹雪3': len(df3[(df3 >= 0.4) & (df3 < 0.6)]),'雨夹雪4': len(df3[(df3>=0.6) & (df3<0.8)]),
            '雨夹雪5': len(df3[(df3 >= 0.8) & (df3 <= 1)])
        }
        dict4 = {
            '雪1': len(df4[(df4 >= 0) & (df4 < 0.2)]),'雪2': len(df4[(df4>=0.2) & (df4<0.4)]),
            '雪3': len(df4[(df4 >= 0.4) & (df4 < 0.6)]),'雪4': len(df4[(df4>=0.6) & (df4<0.8)]),
            '雪5': len(df4[(df4 >= 0.8) & (df4 <= 1)])
        }
        dict5 = {
            '冻雨1': len(df5[(df5 >= 0) & (df5 < 0.2)]),'冻雨2': len(df5[(df5>=0.2) & (df5<0.4)]),
            '冻雨3': len(df5[(df5 >= 0.4) & (df5 < 0.6)]),'冻雨4': len(df5[(df5>=0.6) & (df5<0.8)]),
            '冻雨5': len(df5[(df5 >= 0.8) & (df5 <= 1)])
        }
        type_list = [dict1, dict2, dict3, dict4, dict5]
        x_tick, width = [i for i in range(1, 6)], 0.3
        x_tick_label = ['无降水', '雨', '雨夹雪', '雪', '冻雨']
        # y_tick_obs = list(map(lambda x: x + 50, loi_obs_dict.values()))

        plt.figure(figsize=(16, 9), dpi=300)
        color_list = ['royalblue','skyblue','lavender','sandybrown','tomato']
        subjects = ['0.0-0.2','0.2-0.4','0.4-0.6','0.6-0.8','0.8-1.0']
        for i, j in enumerate(subjects):
            x_tick_obs = list(map(lambda x: x + (i - 2) * width / 2, x_tick))
            y_tick_obs = list(map(lambda x: list(x.values())[i], type_list))
            y_tick_obs_label = list(map(lambda x: x + 50, y_tick_obs))
            plt.bar(x_tick_obs, y_tick_obs, width=width/2, edgecolor = 'k', linewidth=0.5,
                    color=color_list[i], label = subjects[i])
            for i, j in enumerate(x_tick_obs):
                plt.text(j, y_tick_obs_label[i], y_tick_obs[i], size=14, ha='center')

        plt.xticks(x_tick, x_tick_label)
        plt.ylabel("站点数")
        plt.title(var + "-预报降水相态概率分布")
        plt.legend(loc=0, frameon=False)
        if not os.path.exists(os.path.dirname(out_file)):
            os.makedirs(os.path.dirname(out_file))
        plt.savefig(out_file, bbox_inches='tight')
        logging.info(var + '-预报降水相态概率分布图绘制完成')
    except Exception as e:
        logging.error(e)

def draw_ptype_obs(report_time, cst, outpath):
    if report_time.day < 16:
        label = 'low'
    else:
        label = 'up'
    his_file = his_path.format(rpt=report_time, cst=int(cst), label=label)
    out_file = outpath.format(rpt=report_time, cst=int(cst))
    try:
        csv_df = pd.read_csv(his_file)
        obs_time_str = (report_time + timedelta(hours=int(cst))).strftime('%Y-%m-%d %H:00:00')
        loi_obs_df = csv_df[csv_df['obs_time'] == obs_time_str]['Obs6']
        loi_nafp_df = csv_df[csv_df['obs_time'] == obs_time_str]['Ppt2-sta']

        loi_obs_dict = {
            '无降水' : len(loi_obs_df[loi_obs_df == 0.0]),
            '雨' : len(loi_obs_df[loi_obs_df == 1.0]),
            '冻雨': len(loi_obs_df[loi_obs_df == 4.0]),
            '雨夹雪' : len(loi_obs_df[loi_obs_df == 2.0]),
            '雪' : len(loi_obs_df[loi_obs_df == 3.0]),
            '缺测' : len(loi_obs_df[loi_obs_df == 9.0])
        }
        loi_nafp_dict = {
            '无降水' : len(loi_nafp_df[loi_nafp_df == 0.0]),
            '雨' : len(loi_nafp_df[loi_nafp_df == 1.0]),
            '冻雨': len(loi_nafp_df[loi_nafp_df == 3.0]),
            '雨夹雪': len(loi_nafp_df[loi_nafp_df == 7.0]),
            '雪': len(loi_nafp_df[loi_nafp_df == 5.0])+len(loi_nafp_df[loi_nafp_df == 6.0])+len(loi_nafp_df[loi_nafp_df == 8.0]),
            # '干雪': len(loi_df[loi_df == 5.0]),
            # '湿雪': len(loi_df[loi_df == 6.0]),
            # '冰粒' : len(loi_df[loi_df == 8.0]),
            '缺测': 0
        }
        x_tick, width = [i for i in range(1, len(loi_obs_dict.keys())+1)], 0.3
        x_tick_obs = list(map(lambda x: x - width / 2, x_tick))
        x_tick_nafp = list(map(lambda x: x + width / 2, x_tick))
        y_tick_obs = list(map(lambda x: x + 50, loi_obs_dict.values()))
        y_tick_nafp = list(map(lambda x: x + 50, loi_nafp_dict.values()))

        plt.figure(figsize=(16, 9), dpi=300)
        plt.bar(x_tick_obs, loi_obs_dict.values(), width=width,
                label='Obs6', edgecolor = 'k', linewidth=0.5, color = 'skyblue')
        plt.bar(x_tick_nafp, loi_nafp_dict.values(), width=width,
                label='Ppt2-sta', edgecolor = 'k', linewidth=0.5, color = 'sandybrown')
        for i, j in enumerate(x_tick_obs):
            plt.text(j, y_tick_obs[i], list(loi_obs_dict.values())[i], ha='center')
        for i, j in enumerate(x_tick_nafp):
            plt.text(j, y_tick_nafp[i], list(loi_nafp_dict.values())[i], ha='center')

        plt.xticks(x_tick, loi_obs_dict.keys())
        plt.ylabel("站点数")
        plt.title("实况与预报降水相态对比")
        plt.legend(loc=9, frameon=False)
        if not os.path.exists(os.path.dirname(out_file)):
            os.makedirs(os.path.dirname(out_file))
        plt.savefig(out_file, bbox_inches='tight')
        logging.info('实况与预报降水相态对比图绘制完成')
    except Exception as e:
        logging.error(e)

def draw():
    csv_df = pd.read_csv(r'D:\share\DATASOURCE\PTYPE\STATIS_HIS\202304\202304_08_003_low.csv')
    plt.figure(figsize=(16, 9), dpi=300)
    obs_time_str = datetime(year=2023,month=4,day=10,hour=11).strftime('%Y-%m-%d %H:00:00')
    loi_obs_df = csv_df[csv_df['obs_time'] == obs_time_str][['ID', 'Obs']]
    nation_df = loi_obs_df[loi_obs_df['ID'] < 100000]
    local_df = loi_obs_df[loi_obs_df['ID'] > 100000]

    nation_df_Y = np.sum(nation_df.Obs < 999)
    nation_df_N = np.sum(nation_df.Obs > 999)
    local_df_Y = np.sum(local_df.Obs < 999)
    local_df_N = np.sum(local_df.Obs > 999)
    x_tick, width = [i for i in range(1, 3)], 0.3
    x_tick_Y = list(map(lambda x: x - width / 2, x_tick))
    x_tick_N = list(map(lambda x: x + width / 2, x_tick))
    y_tick_Y = [nation_df_Y, local_df_Y]
    y_tick_N = [nation_df_N, local_df_N]

    plt.bar(x_tick_Y, y_tick_Y, width=width,
            label='正常值', edgecolor='k', linewidth=0.5, color='skyblue')
    plt.bar(x_tick_N, y_tick_N, width=width,
            label='异常值', edgecolor='k', linewidth=0.5, color='sandybrown')
    for i, j in enumerate(x_tick_Y):
        plt.text(j, y_tick_Y[i]+20, y_tick_Y[i], ha='center')
    for i, j in enumerate(x_tick_N):
        plt.text(j, y_tick_N[i]+20, y_tick_N[i], ha='center')
    plt.xticks(x_tick, ['五位数站点', '高位数站点'])
    plt.ylabel("站点数")
    plt.title(obs_time_str)
    plt.legend(loc=9, frameon=False)
    plt.savefig('2.png', bbox_inches='tight')


if __name__ == '__main__':
    draw()
    # 参数：2023040208 3 Ppt1
    # argv = sys.argv
    # rp_H = [8, 20]
    # if len(argv) == 1:
    #     report_time_tmp = datetime.now() - timedelta(days=1)
    #     cst_list = fst_h
    #     for report_hour in rp_H:
    #         for cst in cst_list:
    #             report_time = report_time_tmp.replace(hour=report_hour)
    #             draw_ptype_obs(report_time, cst, png_path_ptype)
    #             draw_ptype_Ppt(report_time, cst, png_path_ptype_prob, 'Ppt1')
    #             draw_ptype_Ppt(report_time, cst, png_path_ptype_prob, 'Ppt2')
    # elif len(argv) == 4:
    #     report_time = datetime.strptime(argv[1], '%Y%m%d%H')
    #     cst = argv[2]
    #     if argv[-1] == 'ptype':
    #         draw_ptype_obs(report_time, cst, png_path_ptype)
    #     elif argv[-1] == 'Ppt1' or argv[-1] == 'Ppt2':
    #         draw_ptype_Ppt(report_time, cst, png_path_ptype_prob, argv[-1])
    #     else:
    #         logging.error('参数有误')
    # else:
    #     logging.error('参数有误')
