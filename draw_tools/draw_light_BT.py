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
    # threshold, heatmap_Bin = cv2.threshold(heatmap_array.astype(np.uint8), 0, np.max(heatmap_array), cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    fig = plt.figure(figsize=(12, 12), dpi=120)
    ax = plt.axes()
    # 设置标题
    ax.set_title(pic_name, fontsize=24, fontdict={'family': 'simhei'})
    # 设置X轴标签
    plt.xlabel('{}'.format(x_name))
    # 设置Y轴标签
    plt.ylabel('{}'.format(y_name))

    plt.xlim(xmax=260, xmin=180)
    plt.ylim(ymax=10, ymin=-60)
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    levels = [0, 20, 40, 60, 80, 100, 150, 200, 250, 300, 500, 1000]
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
    yedges = yedges * 5
    fig = plt.figure(figsize=(12, 12), dpi=120)
    ax = plt.axes()
    # 设置标题
    ax.set_title(pic_name, fontsize=24, fontdict={'family': 'simhei'})
    # 设置X轴标签
    plt.xlabel('{}'.format(x_name))
    # 设置Y轴标签
    plt.ylabel('{}'.format(y_name))

    plt.xlim(xmax=260, xmin=180)
    plt.ylim(ymax=15, ymin=-60)
    plt.yticks([-60, -45, -30, -15, 0, 15], [-12, -9, -6, -3, 0, 3])
    # # 设置坐标轴刻度

    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    levels = [0, 20, 40, 60, 80, 100, 150, 200, 250, 300, 500, 1000]
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
    yedges = yedges * 5
    fig = plt.figure(figsize=(12, 12), dpi=120)
    ax = plt.axes()
    # 设置标题
    ax.set_title(pic_name, fontsize=24, fontdict={'family': 'simhei'})
    # 设置X轴标签
    plt.xlabel('{}'.format(x_name))
    # 设置Y轴标签
    plt.ylabel('{}'.format(y_name))

    plt.xlim(xmax=260, xmin=180)
    plt.ylim(ymax=15, ymin=-60)
    plt.yticks([-60, -45, -30, -15, 0, 15], [-12, -9, -6, -3, 0, 3])
    # # 设置坐标轴刻度

    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    levels = [0, 20, 40, 60, 80, 100, 150, 200, 250, 300, 500, 1000]
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

    plt.xlim(xmax=10, xmin=-60)
    plt.ylim(ymax=0, ymin=-45)
    plt.yticks([-45, -30, -15, 0], [-9, -6, -3, 0])
    # # 设置坐标轴刻度

    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    levels = [0, 20, 40, 60, 80, 100, 150, 200, 250, 300, 500, 1000]
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

    plt.xlim(xmax=10, xmin=-60)
    plt.ylim(ymax=15, ymin=-60)
    plt.yticks([-60, -45, -30, -15, 0, 15], [-12, -9, -6, -3, 0, 3])
    # # 设置坐标轴刻度

    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    # levels = [0,20,40,60,80,100,140,180,220,260,300]
    levels = [0, 20, 40, 60, 80, 100, 150, 200, 250, 300, 500, 1000]
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

    plt.xlim(xmax=2, xmin=-12)
    plt.ylim(ymax=0, ymin=-10)
    # 设置坐标轴刻度

    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    levels = [0, 20, 40, 60, 80, 100, 150, 200, 250, 300, 500, 1000]
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
    filepath = r'/data/BTD1.xlsx'
    data_df = pd.read_excel(filepath, sheet_name='Sheet2', usecols=['BT13', 'BTD09_13', 'BTD09_10', 'BTD14_13'])
    histogram2d_1(data_df.BT13, data_df.BTD09_13, 'BT13(K)', 'BTD09_13(℃)', '6月份闪电_风云4B卫星通道值分布')
    histogram2d_2(data_df.BT13, data_df.BTD09_10, 'BT13(K)', 'BTD09_10(℃)', '6月份闪电_风云4B卫星通道值分布')
    histogram2d_3(data_df.BT13, data_df.BTD14_13, 'BT13(K)', 'BTD14_13(℃)', '6月份闪电_风云4B卫星通道值分布')
    histogram2d_4(data_df.BTD09_13, data_df.BTD14_13, 'BTD09_13(℃)', 'BTD14_13(℃)', '6月份闪电_风云4B卫星通道值分布')
    histogram2d_5(data_df.BTD09_13, data_df.BTD09_10, 'BTD09_13(℃)', 'BTD09_10(℃)', '6月份闪电_风云4B卫星通道值分布')
    histogram2d_6(data_df.BTD09_10, data_df.BTD14_13, 'BTD09_10(℃)', 'BTD14_13(℃)', '6月份闪电_风云4B卫星通道值分布')