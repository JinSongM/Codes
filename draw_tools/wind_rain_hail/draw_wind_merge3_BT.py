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

def histogram2d_1(x_data, y_data, x_name, y_name, pic_name):
    """
    BTD13
    BTD09_13
    """
    heatmap_array, xedges, yedges = np.histogram2d(x_data, y_data, bins=200)
    yedges = yedges * 2

    fig = plt.figure(figsize=(12, 12), dpi=120)
    ax = plt.axes()
    # 设置标题
    ax.set_title(pic_name, fontsize=24, fontdict={'family': 'simhei'})
    # 设置X轴标签
    plt.xlabel('{}'.format(x_name))
    # 设置Y轴标签
    plt.ylabel('{}'.format(y_name))

    plt.xlim(xmax=300, xmin=180)
    plt.ylim(ymax=0, ymin=-120)
    plt.yticks([-120, -100, -80, -60, -40, -20, 0], [-60, -50, -40, -30, -20, -10, 0])
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    levels = np.arange(0, np.max(heatmap_array) - 5, 1)
    cmap, norm = cm_collected.get_cmap('ncl/CBR_wet', extend='max', levels=levels)
    heatmap_array = cv2.blur(heatmap_array.T, (3, 3))
    heatmap = plt.imshow(heatmap_array, extent=extent, origin='lower', cmap=cmap, norm=norm)
    l, b, w, h = ax.get_position().bounds
    # cax = fig.add_axes([l, b - h * 0.06 - 0.05, w, h * 0.02])
    cax = fig.add_axes([l + 1.02 * w, b, w * 0.02, h])
    cbar = plt.colorbar(heatmap, cax=cax, ticks=levels, label=levels, orientation='vertical', extend='max')
    cbar.set_label('点数', fontdict={'family': 'simsun'})
    cbar.ax.tick_params(labelsize=16)
    plt.savefig(fname='BTD09_13.png', bbox_inches='tight')
    print('绘图成功：BTD09_13.png')

def histogram2d_2(x_data, y_data, x_name, y_name, pic_name):
    """
    BTD13
    BTD09_10
    """
    heatmap_array, xedges, yedges = np.histogram2d(x_data, y_data, bins=200)
    yedges = yedges * 10
    fig = plt.figure(figsize=(12, 12), dpi=120)
    ax = plt.axes()
    # 设置标题
    ax.set_title(pic_name, fontsize=24, fontdict={'family': 'simhei'})
    # 设置X轴标签
    plt.xlabel('{}'.format(x_name))
    # 设置Y轴标签
    plt.ylabel('{}'.format(y_name))

    plt.xlim(xmax=300, xmin=180)
    plt.ylim(ymax=0, ymin=-120)
    plt.yticks([-120, -100, -80, -60, -40, -20, 0], [-12, -10, -8, -6, -4, -2, 0])
    # # 设置坐标轴刻度

    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    levels = np.arange(0, np.max(heatmap_array) - 5, 1)
    cmap, norm = cm_collected.get_cmap('ncl/CBR_wet', extend='max', levels=levels)
    heatmap_array = cv2.blur(heatmap_array.T, (3, 3))
    heatmap = plt.imshow(heatmap_array, extent=extent, origin='lower', cmap=cmap, norm=norm)
    l, b, w, h = ax.get_position().bounds
    # cax = fig.add_axes([l, b - h * 0.06 - 0.05, w, h * 0.02])
    cax = fig.add_axes([l + 1.02 * w, b, w * 0.02, h])
    cbar = plt.colorbar(heatmap, cax=cax, ticks=levels, label=levels, orientation='vertical', extend='max')
    cbar.set_label('点数', fontdict={'family': 'simsun'})
    cbar.ax.tick_params(labelsize=16)
    plt.savefig(fname='BTD09_10.png', bbox_inches='tight')
    print('绘图成功：BTD09_10.png')


def histogram2d_3(x_data, y_data, x_name, y_name, pic_name):
    """
    BTD13
    BTD09_10
    """
    heatmap_array, xedges, yedges = np.histogram2d(x_data, y_data, bins=200)
    yedges = yedges * 10
    fig = plt.figure(figsize=(12, 12), dpi=120)
    ax = plt.axes()
    # 设置标题
    ax.set_title(pic_name, fontsize=24, fontdict={'family': 'simhei'})
    # 设置X轴标签
    plt.xlabel('{}'.format(x_name))
    # 设置Y轴标签
    plt.ylabel('{}'.format(y_name))

    plt.xlim(xmax=300, xmin=180)
    plt.ylim(ymax=0, ymin=-120)
    plt.yticks([-120, -100, -80, -60, -40, -20, 0], [-12, -10, -8, -6, -4, -2, 0])
    # # 设置坐标轴刻度

    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    levels = np.arange(0, np.max(heatmap_array) - 7, 1)
    cmap, norm = cm_collected.get_cmap('ncl/CBR_wet', extend='max', levels=levels)
    heatmap_array = cv2.blur(heatmap_array.T, (3, 3))
    heatmap = plt.imshow(heatmap_array, extent=extent, origin='lower', cmap=cmap, norm=norm)
    l, b, w, h = ax.get_position().bounds
    # cax = fig.add_axes([l, b - h * 0.06 - 0.05, w, h * 0.02])
    cax = fig.add_axes([l + 1.02 * w, b, w * 0.02, h])
    cbar = plt.colorbar(heatmap, cax=cax, ticks=levels, label=levels, orientation='vertical', extend='max')
    cbar.set_label('点数', fontdict={'family': 'simsun'})
    cbar.ax.tick_params(labelsize=16)
    plt.savefig(fname='BTD14_13.png', bbox_inches='tight')
    print('绘图成功：BTD14_13.png')

def histogram2d_4(x_data, y_data, x_name, y_name, pic_name):
    """
    BTD09_13
    BTD14_13
    """
    heatmap_array, xedges, yedges = np.histogram2d(x_data, y_data, bins=200)
    yedges = yedges * 5
    fig = plt.figure(figsize=(12, 12), dpi=120)
    ax = plt.axes()
    # 设置标题
    ax.set_title(pic_name, fontsize=24, fontdict={'family': 'simhei'})
    # 设置X轴标签
    plt.xlabel('{}'.format(x_name))
    # 设置Y轴标签
    plt.ylabel('{}'.format(y_name))

    plt.xlim(xmax=0, xmin=-60)
    plt.ylim(ymax=0, ymin=-60)
    plt.yticks([-60, -50, -40, -30, -20, -10, 0], [-12, -10, -8, -6, -4, -2, 0])
    # # 设置坐标轴刻度

    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    levels = np.arange(0, np.max(heatmap_array) - 11, 1)
    cmap, norm = cm_collected.get_cmap('ncl/CBR_wet', extend='max', levels=levels)
    heatmap_array = cv2.blur(heatmap_array.T, (3, 3))
    heatmap = plt.imshow(heatmap_array, extent=extent, origin='lower', cmap=cmap, norm=norm)
    l, b, w, h = ax.get_position().bounds
    # cax = fig.add_axes([l, b - h * 0.06 - 0.05, w, h * 0.02])
    cax = fig.add_axes([l + 1.02 * w, b, w * 0.02, h])
    cbar = plt.colorbar(heatmap, cax=cax, ticks=levels, label=levels, orientation='vertical', extend='max')
    cbar.set_label('点数', fontdict={'family': 'simsun'})
    cbar.ax.tick_params(labelsize=16)
    plt.savefig(fname='BTD09_13_14_13.png', bbox_inches='tight')
    print('绘图成功：BTD09_13_14_13.png')

def histogram2d_5(x_data, y_data, x_name, y_name, pic_name):
    """
    BTD09_13
    BTD09_10
    """
    heatmap_array, xedges, yedges = np.histogram2d(x_data, y_data, bins=200)
    yedges = yedges * 5
    fig = plt.figure(figsize=(12, 12), dpi=120)
    ax = plt.axes()
    # 设置标题
    ax.set_title(pic_name, fontsize=24, fontdict={'family': 'simhei'})
    # 设置X轴标签
    plt.xlabel('{}'.format(x_name))
    # 设置Y轴标签
    plt.ylabel('{}'.format(y_name))

    plt.xlim(xmax=0, xmin=-60)
    plt.ylim(ymax=0, ymin=-60)
    plt.yticks([-60, -50, -40, -30, -20, -10, 0], [-12, -10, -8, -6, -4, -2, 0])
    # # 设置坐标轴刻度


    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    levels = np.arange(0, np.max(heatmap_array) - 11, 1)
    cmap, norm = cm_collected.get_cmap('ncl/CBR_wet', extend='max', levels=levels)
    heatmap_array = cv2.blur(heatmap_array.T, (3, 3))
    heatmap = plt.imshow(heatmap_array, extent=extent, origin='lower', cmap=cmap, norm=norm)
    l, b, w, h = ax.get_position().bounds
    # cax = fig.add_axes([l, b - h * 0.06 - 0.05, w, h * 0.02])
    cax = fig.add_axes([l + 1.02 * w, b, w * 0.02, h])
    cbar = plt.colorbar(heatmap, cax=cax, ticks=levels, label=levels, orientation='vertical', extend='max')
    cbar.set_label('点数', fontdict={'family': 'simsun'})
    cbar.ax.tick_params(labelsize=16)
    plt.savefig(fname='BTD09_13_09_10.png', bbox_inches='tight')
    print('绘图成功：BTD09_13_09_10.png')

def histogram2d_6(x_data, y_data, x_name, y_name, pic_name):
    """
    BTD9_10
    BTD14_13
    """
    heatmap_array, xedges, yedges = np.histogram2d(x_data, y_data, bins=200)
    fig = plt.figure(figsize=(12, 12), dpi=120)
    ax = plt.axes()
    # 设置标题
    ax.set_title(pic_name, fontsize=24, fontdict={'family': 'simhei'})
    # 设置X轴标签
    plt.xlabel('{}'.format(x_name))
    # 设置Y轴标签
    plt.ylabel('{}'.format(y_name))

    plt.xlim(xmax=0, xmin=-12)
    plt.ylim(ymax=0, ymin=-12)
    # 设置坐标轴刻度

    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    levels = np.arange(0, np.max(heatmap_array) - 8, 1)
    cmap, norm = cm_collected.get_cmap('ncl/CBR_wet', extend='max', levels=levels)
    heatmap_array = cv2.blur(heatmap_array.T, (3, 3))
    heatmap = plt.imshow(heatmap_array, extent=extent, origin='lower', cmap=cmap, norm=norm)
    l, b, w, h = ax.get_position().bounds
    # cax = fig.add_axes([l, b - h * 0.06 - 0.05, w, h * 0.02])
    cax = fig.add_axes([l + 1.02 * w, b, w * 0.02, h])
    cbar = plt.colorbar(heatmap, cax=cax, ticks=levels, label=levels, orientation='vertical', extend='max')
    cbar.set_label('点数', fontdict={'family': 'simsun'})
    cbar.ax.tick_params(labelsize=16)
    plt.savefig(fname='BTD09_10_14_13.png', bbox_inches='tight')
    print('绘图成功：BTD09_10_14_13.png')

if __name__=='__main__':
    filepath_wind = r'/data/PRODUCT/wind_channel_sta/merge_wind6-8.csv'
    wind_df = pd.read_csv(filepath_wind)
    wind_df = wind_df.dropna(axis=0, how='any')
    title = '6-8月份大风_风云4B卫星通道值分布'
    histogram2d_1(wind_df.BT13, wind_df.BTD09_13, 'BT13(K)', 'BTD09_13(℃)', title)
    histogram2d_2(wind_df.BT13, wind_df.BTD09_10, 'BT13(K)', 'BTD09_10(℃)', title)
    histogram2d_3(wind_df.BT13, wind_df.BTD14_13, 'BT13(K)', 'BTD14_13(℃)', title)
    histogram2d_4(wind_df.BTD09_13, wind_df.BTD14_13, 'BTD09_13(℃)', 'BTD14_13(℃)', title)
    histogram2d_5(wind_df.BTD09_13, wind_df.BTD09_10, 'BTD09_13(℃)', 'BTD09_10(℃)', title)
    histogram2d_6(wind_df.BTD09_10, wind_df.BTD14_13, 'BTD09_10(℃)', 'BTD14_13(℃)', title)