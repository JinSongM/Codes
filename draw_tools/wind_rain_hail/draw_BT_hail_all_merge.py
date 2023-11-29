# -- coding: utf-8 --
# @Time : 2023/9/5 11:24
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : draw_light_BT.py
# @Software: PyCharm
import os, cv2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.stats import gaussian_kde
import metdig.graphics.cmap.cm as cm_collected

plt.rcParams.update({
    'font.sans-serif': 'Times New Roman',
    'font.size': 22
    })
plt.rcParams['axes.unicode_minus']=False

def get_scatter_beauty(x_data, y_data, x_name, y_name, pic_name):

    # 计算散点的密度
    xy = np.vstack([x_data, y_data])
    # z值密度构造
    z = gaussian_kde(xy)(xy)
    # 按密度对点进行排序，以便最后绘制最密集的点
    idx = z.argsort()
    # 排序后的x_data, y_data, 密度_data
    x, y, z = x_data[idx], y_data[idx], z[idx]

    plt.figure(figsize=(16, 9), dpi=120)
    ax = plt.axes()
    # 设置标题
    ax.set_title(pic_name, fontsize=24, fontdict={'family': 'simhei'})
    # 设置X轴标签
    plt.xlabel('{}'.format(x_name))
    # 设置Y轴标签
    plt.ylabel('{}'.format(y_name))

    # # 设置坐标轴刻度
    # x_ticks = np.arange(12,16,0.5)
    # y_ticks = np.arange(6, 14, 1)
    # plt.xticks(x_ticks)
    # plt.yticks(y_ticks)

    point_density = ax.scatter(x, y, c=z, s=15, alpha=0.8, cmap='Spectral_r', marker='o')
    # 增加颜色分级色带
    point_density_ribbon = plt.colorbar(point_density)
    # 调整色带字体大小
    # point_density_ribbon.ax.tick_params(labelsize=16)
    plt.savefig(fname='BTD09_13.png', bbox_inches='tight')

def histogram2d_1(x_data, y_data, x2_data, y2_data, x_name, y_name, pic_name):
    """
    BTD13
    BTD09_13
    """
    heatmap_array, xedges, yedges = np.histogram2d(x_data, y_data)
    heatmap_array2, xedges2, yedges2 = np.histogram2d(x2_data, y2_data)
    heatmap_array = heatmap_array[::-1]
    heatmap_array2 = heatmap_array2[::-1]
    fig = plt.figure(figsize=(12, 12), dpi=120)
    ax = plt.axes()
    # 设置标题
    ax.set_title(pic_name, fontsize=24, fontdict={'family': 'simhei'})
    # 设置X轴标签
    plt.xlabel('{}'.format(x_name))
    # 设置Y轴标签
    plt.ylabel('{}'.format(y_name))

    plt.xlim(xmax=300, xmin=180)
    plt.ylim(ymax=0, ymin=-60)

    levels = np.arange(100, np.max(heatmap_array) + 1, 50)
    x, y = np.meshgrid(xedges[:-1], yedges[:-1])
    heatmap_array = cv2.GaussianBlur(heatmap_array, (5, 5), 0, 0)
    heatmap = ax.contour(x, y, heatmap_array, levels=np.array(levels), colors='black', linewidths=2)
    if True:
        plt.clabel(heatmap, inline=1, fontsize=20, fmt='%.0f', colors='black')

    rain_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='black', facecolor='none')
    wind_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='r', facecolor='none')
    # hail_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='b', facecolor='none')
    labels = ['冰雹']
    ax.legend([rain_label], labels,
              frameon=False, prop={'family': 'simhei'})
    plt.savefig(fname='BTD09_13.png', bbox_inches='tight')
    print('绘图成功：BTD09_13.png')

def histogram2d_2(x_data, y_data, x2_data, y2_data, x_name, y_name, pic_name):
    """
    BTD13
    BTD09_10
    """
    heatmap_array, xedges, yedges = np.histogram2d(x_data, y_data)
    heatmap_array2, xedges2, yedges2 = np.histogram2d(x2_data, y2_data)
    heatmap_array = heatmap_array[::-1]
    heatmap_array2 = heatmap_array2[::-1]
    fig = plt.figure(figsize=(12, 12), dpi=120)
    ax = plt.axes()
    # 设置标题
    ax.set_title(pic_name, fontsize=24, fontdict={'family': 'simhei'})
    # 设置X轴标签
    plt.xlabel('{}'.format(x_name))
    # 设置Y轴标签
    plt.ylabel('{}'.format(y_name))

    plt.xlim(xmax=300, xmin=180)
    plt.ylim(ymax=0, ymin=-12)
    # # 设置坐标轴刻度

    levels = np.arange(100, np.max(heatmap_array) + 1, 50)
    x, y = np.meshgrid(xedges[:-1], yedges[:-1])
    heatmap_array = cv2.GaussianBlur(heatmap_array, (5, 5), 0, 0)
    heatmap = ax.contour(x, y, heatmap_array, levels=np.array(levels), colors='black', linewidths=2)
    if True:
        plt.clabel(heatmap, inline=1, fontsize=20, fmt='%.0f', colors='black')

    rain_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='black', facecolor='none')
    wind_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='r', facecolor='none')
    # hail_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='b', facecolor='none')
    labels = ['冰雹']
    ax.legend([rain_label], labels,
              frameon=False, prop={'family': 'simhei'})
    plt.savefig(fname='BTD09_10.png', bbox_inches='tight')
    print('绘图成功：BTD09_10.png')


def histogram2d_3(x_data, y_data, x2_data, y2_data, x_name, y_name, pic_name):
    """
    BTD13
    BTD09_10
    """
    heatmap_array, xedges, yedges = np.histogram2d(x_data, y_data)
    heatmap_array2, xedges2, yedges2 = np.histogram2d(x2_data, y2_data)
    heatmap_array = heatmap_array[::-1]
    heatmap_array2 = heatmap_array2[::-1]
    # yedges = yedges * 5
    fig = plt.figure(figsize=(12, 12), dpi=120)
    ax = plt.axes()
    # 设置标题
    ax.set_title(pic_name, fontsize=24, fontdict={'family': 'simhei'})
    # 设置X轴标签
    plt.xlabel('{}'.format(x_name))
    # 设置Y轴标签
    plt.ylabel('{}'.format(y_name))

    plt.xlim(xmax=300, xmin=180)
    # plt.ylim(ymax=0, ymin=-40)
    # plt.yticks([-40, -35, -30, -25, -20, -15, -10, -5, 0], [-8, -7, -6, -5, -4, -3, -2, -1, 0])
    plt.ylim(ymax=0, ymin=-12)
    # # 设置坐标轴刻度

    levels = np.arange(100, np.max(heatmap_array) + 1, 50)
    x, y = np.meshgrid(xedges[:-1], yedges[:-1])
    heatmap_array = cv2.GaussianBlur(heatmap_array, (5, 5), 0, 0)
    heatmap = ax.contour(x, y, heatmap_array, levels=np.array(levels), colors='black', linewidths=2)
    if True:
        plt.clabel(heatmap, inline=1, fontsize=20, fmt='%.0f', colors='black')

    rain_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='black', facecolor='none')
    wind_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='r', facecolor='none')
    # hail_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='b', facecolor='none')
    labels = ['冰雹']
    ax.legend([rain_label], labels,
              frameon=False, prop={'family': 'simhei'})
    plt.savefig(fname='BTD14_13.png', bbox_inches='tight')
    print('绘图成功：BTD14_13.png')

def histogram2d_4(x_data, y_data, x2_data, y2_data, x_name, y_name, pic_name):
    """
    BTD09_13
    BTD14_13
    """
    heatmap_array, xedges, yedges = np.histogram2d(x_data, y_data)
    heatmap_array2, xedges2, yedges2 = np.histogram2d(x2_data, y2_data)
    heatmap_array = heatmap_array[::-1]
    heatmap_array2 = heatmap_array2[::-1]
    # yedges = yedges * 5
    fig = plt.figure(figsize=(12, 12), dpi=120)
    ax = plt.axes()
    # 设置标题
    ax.set_title(pic_name, fontsize=24, fontdict={'family': 'simhei'})
    # 设置X轴标签
    plt.xlabel('{}'.format(x_name))
    # 设置Y轴标签
    plt.ylabel('{}'.format(y_name))

    # plt.xlim(xmax=0, xmin=-65)
    plt.ylim(ymax=0, ymin=-12)
    # plt.yticks([-45, -30, -15, 0], [-9, -6, -3, 0])
    plt.xlim(xmax=0, xmin=-60)
    # # 设置坐标轴刻度

    levels = np.arange(150, np.max(heatmap_array) + 1, 50)
    x, y = np.meshgrid(xedges[:-1], yedges[:-1])
    heatmap_array = cv2.GaussianBlur(heatmap_array, (5, 5), 0, 0)
    heatmap = ax.contour(x, y, heatmap_array, levels=np.array(levels), colors='black', linewidths=2)
    if True:
        plt.clabel(heatmap, inline=1, fontsize=20, fmt='%.0f', colors='black')

    # levels2 = np.arange(1, np.max(heatmap_array2) + 1, 1)
    # x2, y2 = np.meshgrid(xedges2[:-1], yedges2[:-1])
    # heatmap_array2 = cv2.GaussianBlur(heatmap_array2, (3, 3), 0, 0)
    # heatmap2 = ax.contour(x2, y2, heatmap_array2, levels=np.array(levels2), colors='r', linewidths=2)
    # if True:
    #     plt.clabel(heatmap2, inline=1, fontsize=20, fmt='%.0f', colors='r')

    rain_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='black', facecolor='none')
    wind_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='r', facecolor='none')
    # hail_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='b', facecolor='none')
    labels = ['冰雹']
    ax.legend([rain_label], labels,
              frameon=False, prop={'family': 'simhei'})
    plt.savefig(fname='BTD09_13_14_13.png', bbox_inches='tight')
    print('绘图成功：BTD09_13_14_13.png')

def histogram2d_5(x_data, y_data, x2_data, y2_data, x_name, y_name, pic_name):
    """
    BTD09_13
    BTD09_10
    """
    heatmap_array, xedges, yedges = np.histogram2d(x_data, y_data)
    heatmap_array2, xedges2, yedges2 = np.histogram2d(x2_data, y2_data)
    heatmap_array = heatmap_array[::-1]
    heatmap_array2 = heatmap_array2[::-1]
    # yedges = yedges * 5
    fig = plt.figure(figsize=(12, 12), dpi=120)
    ax = plt.axes()
    # 设置标题
    ax.set_title(pic_name, fontsize=24, fontdict={'family': 'simhei'})
    # 设置X轴标签
    plt.xlabel('{}'.format(x_name))
    # 设置Y轴标签
    plt.ylabel('{}'.format(y_name))

    plt.xlim(xmax=0, xmin=-60)
    plt.ylim(ymax=0, ymin=-12)
    # plt.yticks([-60, -45, -30, -15, 0], [-12, -9, -6, -3, 0])
    # # 设置坐标轴刻度

    levels = np.arange(150, np.max(heatmap_array) + 1, 50)
    x, y = np.meshgrid(xedges[:-1], yedges[:-1])
    heatmap_array = cv2.GaussianBlur(heatmap_array, (5, 5), 0, 0)
    heatmap = ax.contour(x, y, heatmap_array, levels=np.array(levels), colors='black', linewidths=2)
    if True:
        plt.clabel(heatmap, inline=1, fontsize=20, fmt='%.0f', colors='black')

    rain_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='black', facecolor='none')
    wind_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='r', facecolor='none')
    # hail_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='b', facecolor='none')
    labels = ['冰雹']
    ax.legend([rain_label], labels,
              frameon=False, prop={'family': 'simhei'})
    plt.savefig(fname='BTD09_13_09_10.png', bbox_inches='tight')
    print('绘图成功：BTD09_13_09_10.png')

def histogram2d_6(x_data, y_data, x2_data, y2_data, x_name, y_name, pic_name):
    """
    BTD9_10
    BTD14_13
    """
    heatmap_array, xedges, yedges = np.histogram2d(x_data, y_data)
    heatmap_array2, xedges2, yedges2 = np.histogram2d(x2_data, y2_data)
    heatmap_array = heatmap_array[::-1]
    heatmap_array2 = heatmap_array2[::-1]
    fig = plt.figure(figsize=(12, 12), dpi=120)
    ax = plt.axes()
    # 设置标题
    ax.set_title(pic_name, fontsize=24, fontdict={'family': 'simhei'})
    # 设置X轴标签
    plt.xlabel('{}'.format(x_name))
    # 设置Y轴标签
    plt.ylabel('{}'.format(y_name))

    # plt.xlim(xmax=0, xmin=-14)
    plt.ylim(ymax=0, ymin=-12)
    plt.xlim(xmax=0, xmin=-12)
    # 设置坐标轴刻度

    levels = np.arange(150, np.max(heatmap_array) + 1, 50)
    x, y = np.meshgrid(xedges[:-1], yedges[:-1])
    heatmap_array = cv2.GaussianBlur(heatmap_array, (5, 5), 0, 0)
    heatmap = ax.contour(x, y, heatmap_array, levels=np.array(levels), colors='black', linewidths=2)
    if True:
        plt.clabel(heatmap, inline=1, fontsize=20, fmt='%.0f', colors='black')

    rain_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='black', facecolor='none')
    wind_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='r', facecolor='none')
    # hail_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='b', facecolor='none')
    labels = ['冰雹']
    ax.legend([rain_label], labels,
              frameon=False, prop={'family': 'simhei'})
    plt.savefig(fname='BTD09_10_14_13.png', bbox_inches='tight')
    print('绘图成功：BTD09_10_14_13.png')

def mergeCSV(csvpath, outfile):
    import glob
    csvfiles = glob.glob(os.path.join(csvpath, '*.csv'))
    if len(csvfiles) > 0:
        df0 = pd.read_csv(csvfiles[0])
        for i in range(1, len(csvfiles)):
            df_tmp = pd.read_csv(csvfiles[i])
            # pd.merge(df0, df_tmp, on=['lon', 'lat'], how='outer')
            df0 = pd.merge(df0, df_tmp)
        if not os.path.exists(os.path.dirname(outfile)):
            os.makedirs(os.path.dirname(outfile))
        df0.to_csv(outfile)
        print('成功输出至：{}'.format(outfile))
    else:
        print('路径下没有CSV文件')

if __name__=='__main__':
    # mergeCSV(r'/data/PRODUCT/hail_channel_sta/1/month3', r'/data/PRODUCT/hail_channel_sta/1/merge/merge_hail1.csv')
    filepath_rain20 = r'/data/PRODUCT/hail_channel_sta/0/merge3/1.csv'
    filepath_rain50 = r'/data/PRODUCT/hail_channel_sta/1/merge3/merge_hail1.csv'
    rain_df = pd.read_csv(filepath_rain20)
    wind_df = pd.read_csv(filepath_rain50)

    rain_df = rain_df.dropna(axis=0, how='any')
    wind_df = wind_df.dropna(axis=0, how='any')
    title_name = '冰雹-FY4B卫星通道二维频次分布图'
    histogram2d_1(rain_df.BT13, rain_df.BTD09_13, wind_df.BT13, wind_df.BTD09_13, 'BT13(K)', 'BTD09_13(℃)', title_name)
    histogram2d_2(rain_df.BT13, rain_df.BTD09_10, wind_df.BT13, wind_df.BTD09_10, 'BT13(K)', 'BTD09_10(℃)', title_name)
    histogram2d_3(rain_df.BT13, rain_df.BTD14_13, wind_df.BT13, wind_df.BTD14_13, 'BT13(K)', 'BTD14_13(℃)', title_name)
    histogram2d_4(rain_df.BTD09_13, rain_df.BTD14_13, wind_df.BTD09_13, wind_df.BTD14_13, 'BTD09_13(℃)', 'BTD14_13(℃)', title_name)
    histogram2d_5(rain_df.BTD09_13, rain_df.BTD09_10, wind_df.BTD09_13, wind_df.BTD09_10, 'BTD09_13(℃)', 'BTD09_10(℃)', title_name)
    histogram2d_6(rain_df.BTD09_10, rain_df.BTD14_13, wind_df.BTD09_10, wind_df.BTD14_13, 'BTD09_10(℃)', 'BTD14_13(℃)', title_name)