# -- coding: utf-8 --
# @Time : 2023/9/5 11:24
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : rain_wind_hail_contour.py
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

def histogram2d_1(x_data, y_data, x2_data, y2_data, x3_data, y3_data, x_name, y_name, pic_name):
    """
    BTD13
    BTD09_13
    """
    heatmap_array, xedges, yedges = np.histogram2d(x_data, y_data)
    heatmap_array2, xedges2, yedges2 = np.histogram2d(x2_data, y2_data)
    heatmap_array3, xedges3, yedges3 = np.histogram2d(x3_data, y3_data)
    heatmap_array = heatmap_array[::-1]
    heatmap_array2 = heatmap_array2[::-1]
    heatmap_array3 = heatmap_array3[::-1]
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


    levels = np.arange(11000, np.max(heatmap_array) + 1, 2000)
    x, y = np.meshgrid(xedges[:-1], yedges[:-1])
    heatmap_array = cv2.GaussianBlur(heatmap_array, (5, 5), 0, 0)
    heatmap = ax.contourf(x, y, heatmap_array, levels=np.array(levels), extend='max', cmap='Reds', alpha=0.8)
    # cb1 = plt.colorbar(heatmap, ticks=levels, orientation='vertical', pad=-0.02, aspect=45)
    # cb1.set_label('强降水', fontdict={'family': 'simsun'})

    levels3 = np.arange(110, np.max(heatmap_array3) + 1, 80)
    x3, y3 = np.meshgrid(xedges3[:-1], yedges3[:-1])
    heatmap_array3 = cv2.GaussianBlur(heatmap_array3, (3, 3), 0, 0)
    heatmap3 = ax.contourf(x3, y3, heatmap_array3, levels=np.array(levels3), extend='max', cmap='Greens', alpha=0.8)
    # cb3 = plt.colorbar(heatmap3, ticks=levels3, orientation='vertical', pad=0.02, aspect=45)
    # cb3.set_label('冰雹', fontdict={'family': 'simsun'})

    levels2 = np.arange(750, np.max(heatmap_array2) + 1, 50)
    x2, y2 = np.meshgrid(xedges2[:-1], yedges2[:-1])
    heatmap_array2 = cv2.GaussianBlur(heatmap_array2, (3, 3), 0, 0)
    heatmap2 = ax.contourf(x2, y2, heatmap_array2, levels=np.array(levels2), extend='max', cmap='PuRd', alpha=0.8)
    # cb2 = plt.colorbar(heatmap2, ticks=levels2, orientation='vertical', pad=0.01, aspect=45)
    # cb2.set_label('雷暴大风', fontdict={'family': 'simsun'})

    rain_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='red', facecolor='red', alpha=0.3)
    wind_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='b', facecolor='b', alpha=0.3)
    hail_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='g', facecolor='g', alpha=0.3)
    labels = ['强降水', '雷暴大风', '冰雹']
    ax.legend([rain_label, wind_label, hail_label], labels,
              frameon=False, prop={'family': 'simhei'})
    plt.savefig(fname='BTD09_13.png', bbox_inches='tight')
    print('绘图成功：BTD09_13.png')

def histogram2d_2(x_data, y_data, x2_data, y2_data, x3_data, y3_data, x_name, y_name, pic_name):
    """
    BTD13
    BTD09_10
    """
    heatmap_array, xedges, yedges = np.histogram2d(x_data, y_data)
    heatmap_array2, xedges2, yedges2 = np.histogram2d(x2_data, y2_data)
    heatmap_array3, xedges3, yedges3 = np.histogram2d(x3_data, y3_data)
    heatmap_array = heatmap_array[::-1]
    heatmap_array2 = heatmap_array2[::-1]
    heatmap_array3 = heatmap_array3[::-1]
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
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    levels = np.arange(10000, np.max(heatmap_array) + 1, 3000)
    x, y = np.meshgrid(xedges[:-1], yedges[:-1])
    heatmap_array = cv2.GaussianBlur(heatmap_array, (5, 5), 0, 0)
    heatmap = ax.contourf(x, y, heatmap_array, levels=np.array(levels), extend='max', cmap='Reds', alpha=0.8)
    # cb1 = plt.colorbar(heatmap, orientation='horizontal', aspect=45)
    # cb1.ax.set_position([0.22, 0.46, 0.68, 0.1])
    # cb1.set_label('强降水', fontdict={'family': 'simsun'}, labelpad=-45, x=-0.1)

    levels2 = np.arange(700, np.max(heatmap_array2) + 1, 100)
    x2, y2 = np.meshgrid(xedges2[:-1], yedges2[:-1])
    heatmap_array2 = cv2.GaussianBlur(heatmap_array2, (3, 3), 0, 0)
    heatmap2 = ax.contourf(x2, y2, heatmap_array2, levels=np.array(levels2), extend='max', cmap='PuRd', alpha=0.8)
    # cb2 = plt.colorbar(heatmap2, ticks=levels2, orientation='horizontal', aspect=45)
    # cb2.ax.set_position([0.22, 0.42, 0.68, 0.1])
    # cb2.set_label('雷暴大风', fontdict={'family': 'simsun'}, labelpad=-45, x=-0.1)

    levels3 = np.arange(150, np.max(heatmap_array3) + 1, 50)
    x3, y3 = np.meshgrid(xedges3[:-1], yedges3[:-1])
    heatmap_array3 = cv2.GaussianBlur(heatmap_array3, (3, 3), 0, 0)
    heatmap3 = ax.contourf(x3, y3, heatmap_array3, levels=np.array(levels3), extend='max', cmap='Greens', alpha=0.8)
    # cb3 = plt.colorbar(heatmap3, ticks=levels3, orientation='horizontal', aspect=45)
    # cb3.ax.set_position([0.22, 0.38, 0.68, 0.1])
    # cb3.set_label('冰雹', fontdict={'family': 'simsun'}, labelpad=-45, x=-0.1)

    rain_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='red', facecolor='red', alpha=0.3)
    wind_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='b', facecolor='b', alpha=0.3)
    hail_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='g', facecolor='g', alpha=0.3)
    labels = ['强降水', '雷暴大风', '冰雹']
    ax.legend([rain_label, wind_label, hail_label], labels,
              frameon=False, prop={'family': 'simhei'})
    plt.savefig(fname='BTD09_10.png', bbox_inches='tight')
    print('绘图成功：BTD09_10.png')


def histogram2d_3(x_data, y_data, x2_data, y2_data, x3_data, y3_data, x_name, y_name, pic_name):
    """
    BTD13
    BTD09_10
    """
    heatmap_array, xedges, yedges = np.histogram2d(x_data, y_data)
    heatmap_array2, xedges2, yedges2 = np.histogram2d(x2_data, y2_data)
    heatmap_array3, xedges3, yedges3 = np.histogram2d(x3_data, y3_data)
    heatmap_array = heatmap_array[::-1]
    heatmap_array2 = heatmap_array2[::-1]
    heatmap_array3 = heatmap_array3[::-1]
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
    plt.ylim(ymax=0, ymin=-12)
    # # 设置坐标轴刻度

    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    levels = np.arange(12000, np.max(heatmap_array) + 1, 2000)
    x, y = np.meshgrid(xedges[:-1], yedges[:-1])
    heatmap_array = cv2.GaussianBlur(heatmap_array, (5, 5), 0, 0)
    heatmap = ax.contourf(x, y, heatmap_array, levels=np.array(levels), extend='max', cmap='Reds', alpha=0.8)
    # cb1 = plt.colorbar(heatmap, ticks=levels, orientation='vertical', pad=-0.02, aspect=45)
    # cb1.set_label('强降水', fontdict={'family': 'simsun'})

    levels2 = np.arange(800, np.max(heatmap_array2) + 1, 50)
    x2, y2 = np.meshgrid(xedges2[:-1], yedges2[:-1])
    heatmap_array2 = cv2.GaussianBlur(heatmap_array2, (3, 3), 0, 0)
    heatmap2 = ax.contourf(x2, y2, heatmap_array2, levels=np.array(levels2), extend='max', cmap='PuRd', alpha=0.8)
    # cb2 = plt.colorbar(heatmap2, ticks=levels2, orientation='vertical', pad=0.01, aspect=45)
    # cb2.set_label('雷暴大风', fontdict={'family': 'simsun'})

    levels3 = np.arange(150, np.max(heatmap_array3) + 1, 60)
    x3, y3 = np.meshgrid(xedges3[:-1], yedges3[:-1])
    heatmap_array3 = cv2.GaussianBlur(heatmap_array3, (3, 3), 0, 0)
    heatmap3 = ax.contourf(x3, y3, heatmap_array3, levels=np.array(levels3), extend='max', cmap='Greens', alpha=0.8)
    # cb3 = plt.colorbar(heatmap3, ticks=levels3, orientation='vertical', pad=0.02, aspect=45)
    # cb3.set_label('冰雹', fontdict={'family': 'simsun'})


    rain_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='red', facecolor='red', alpha=0.3)
    wind_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='b', facecolor='b', alpha=0.3)
    hail_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='g', facecolor='g', alpha=0.3)
    labels = ['强降水', '雷暴大风', '冰雹']
    ax.legend([rain_label, wind_label, hail_label], labels,
              frameon=False, prop={'family': 'simhei'})
    plt.savefig(fname='BTD14_13.png', bbox_inches='tight')
    print('绘图成功：BTD14_13.png')

def histogram2d_4(x_data, y_data, x2_data, y2_data, x3_data, y3_data, x_name, y_name, pic_name):
    """
    BTD09_13
    BTD14_13
    """
    heatmap_array, xedges, yedges = np.histogram2d(x_data, y_data)
    heatmap_array2, xedges2, yedges2 = np.histogram2d(x2_data, y2_data)
    heatmap_array3, xedges3, yedges3 = np.histogram2d(x3_data, y3_data)
    heatmap_array = heatmap_array[::-1]
    heatmap_array2 = heatmap_array2[::-1]
    heatmap_array3 = heatmap_array3[::-1]
    # yedges = yedges * 5
    fig = plt.figure(figsize=(12, 12), dpi=120)
    ax = plt.axes()
    # 设置标题
    ax.set_title(pic_name, fontsize=24, fontdict={'family': 'simhei'})
    # 设置X轴标签
    plt.xlabel('{}'.format(x_name))
    # 设置Y轴标签
    plt.ylabel('{}'.format(y_name))

    plt.ylim(ymax=0, ymin=-12)
    plt.xlim(xmax=0, xmin=-60)
    # # 设置坐标轴刻度

    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    levels = np.arange(15000, np.max(heatmap_array) + 1, 1000)
    x, y = np.meshgrid(xedges[:-1], yedges[:-1])
    heatmap_array = cv2.GaussianBlur(heatmap_array, (5, 5), 0, 0)
    heatmap = ax.contourf(x, y, heatmap_array, levels=np.array(levels), extend='max', cmap='Reds', alpha=0.8)
    # cb1 = plt.colorbar(heatmap, ticks=levels, orientation='vertical', pad=-0.02, aspect=45)
    # cb1.set_label('强降水', fontdict={'family': 'simsun'})

    levels2 = np.arange(700, np.max(heatmap_array2) + 1, 100)
    x2, y2 = np.meshgrid(xedges2[:-1], yedges2[:-1])
    heatmap_array2 = cv2.GaussianBlur(heatmap_array2, (3, 3), 0, 0)
    heatmap2 = ax.contourf(x2, y2, heatmap_array2, levels=np.array(levels2), extend='max', cmap='PuRd', alpha=0.8)
    # cb2 = plt.colorbar(heatmap2, ticks=levels2, orientation='vertical', pad=0.01, aspect=45)
    # cb2.set_label('雷暴大风', fontdict={'family': 'simsun'})

    levels3 = np.arange(130, np.max(heatmap_array3) + 1, 60)
    x3, y3 = np.meshgrid(xedges3[:-1], yedges3[:-1])
    heatmap_array3 = cv2.GaussianBlur(heatmap_array3, (3, 3), 0, 0)
    heatmap3 = ax.contourf(x3, y3, heatmap_array3, levels=np.array(levels3), extend='max', cmap='Greens', alpha=0.8)
    # cb3 = plt.colorbar(heatmap3, ticks=levels3, orientation='vertical', pad=0.02, aspect=45)
    # cb3.set_label('冰雹', fontdict={'family': 'simsun'})

    rain_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='red', facecolor='red', alpha=0.3)
    wind_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='b', facecolor='b', alpha=0.3)
    hail_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='g', facecolor='g', alpha=0.3)
    labels = ['强降水', '雷暴大风', '冰雹']
    ax.legend([rain_label, wind_label, hail_label], labels,
              frameon=False, prop={'family': 'simhei'})
    plt.savefig(fname='BTD09_13_14_13.png', bbox_inches='tight')
    print('绘图成功：BTD09_13_14_13.png')

def histogram2d_5(x_data, y_data, x2_data, y2_data, x3_data, y3_data, x_name, y_name, pic_name):
    """
    BTD09_13
    BTD09_10
    """
    heatmap_array, xedges, yedges = np.histogram2d(x_data, y_data)
    heatmap_array2, xedges2, yedges2 = np.histogram2d(x2_data, y2_data)
    heatmap_array3, xedges3, yedges3 = np.histogram2d(x3_data, y3_data)
    heatmap_array = heatmap_array[::-1]
    heatmap_array2 = heatmap_array2[::-1]
    heatmap_array3 = heatmap_array3[::-1]
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
    # # 设置坐标轴刻度

    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    levels = np.arange(13000, np.max(heatmap_array) + 1, 2000)
    x, y = np.meshgrid(xedges[:-1], yedges[:-1])
    heatmap_array = cv2.GaussianBlur(heatmap_array, (5, 5), 0, 0)
    heatmap = ax.contourf(x, y, heatmap_array, levels=np.array(levels), extend='max', cmap='Reds', alpha=0.8)
    # cb1 = plt.colorbar(heatmap, ticks=levels, orientation='vertical', pad=-0.02, aspect=45)
    # cb1.set_label('强降水', fontdict={'family': 'simsun'})

    levels2 = np.arange(700, np.max(heatmap_array2) + 1, 100)
    x2, y2 = np.meshgrid(xedges2[:-1], yedges2[:-1])
    heatmap_array2 = cv2.GaussianBlur(heatmap_array2, (3, 3), 0, 0)
    heatmap2 = ax.contourf(x2, y2, heatmap_array2, levels=np.array(levels2), extend='max', cmap='PuRd', alpha=0.8)
    # cb2 = plt.colorbar(heatmap2, ticks=levels2, orientation='vertical', pad=0.01, aspect=45)
    # cb2.set_label('雷暴大风', fontdict={'family': 'simsun'})

    levels3 = np.arange(110, np.max(heatmap_array3) + 1, 80)
    x3, y3 = np.meshgrid(xedges3[:-1], yedges3[:-1])
    heatmap_array3 = cv2.GaussianBlur(heatmap_array3, (3, 3), 0, 0)
    heatmap3 = ax.contourf(x3, y3, heatmap_array3, levels=np.array(levels3), extend='max', cmap='Greens', alpha=0.8)
    # cb3 = plt.colorbar(heatmap3, ticks=levels3, orientation='vertical', pad=0.02, aspect=45)
    # cb3.set_label('冰雹', fontdict={'family': 'simsun'})

    rain_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='red', facecolor='red', alpha=0.3)
    wind_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='b', facecolor='b', alpha=0.3)
    hail_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='g', facecolor='g', alpha=0.3)
    labels = ['强降水', '雷暴大风', '冰雹']
    ax.legend([rain_label, wind_label, hail_label], labels,
              frameon=False, prop={'family': 'simhei'})
    plt.savefig(fname='BTD09_13_09_10.png', bbox_inches='tight')
    print('绘图成功：BTD09_13_09_10.png')

def histogram2d_6(x_data, y_data, x2_data, y2_data, x3_data, y3_data, x_name, y_name, pic_name):
    """
    BTD9_10
    BTD14_13
    """
    heatmap_array, xedges, yedges = np.histogram2d(x_data, y_data)
    heatmap_array2, xedges2, yedges2 = np.histogram2d(x2_data, y2_data)
    heatmap_array3, xedges3, yedges3 = np.histogram2d(x3_data, y3_data)
    heatmap_array = heatmap_array[::-1]
    heatmap_array2 = heatmap_array2[::-1]
    heatmap_array3 = heatmap_array3[::-1]
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
    levels = np.arange(14000, np.max(heatmap_array) + 1, 3000)
    x, y = np.meshgrid(xedges[:-1], yedges[:-1])
    heatmap_array = cv2.GaussianBlur(heatmap_array, (5, 5), 0, 0)
    heatmap = ax.contourf(x, y, heatmap_array, levels=np.array(levels), extend='max', cmap='Reds', alpha=0.8)
    # cb1 = plt.colorbar(heatmap, ticks=levels, orientation='vertical', pad=-0.02, aspect=45)
    # cb1.set_label('强降水', fontdict={'family': 'simsun'})


    levels2 = np.arange(600, np.max(heatmap_array2) + 1, 200)
    x2, y2 = np.meshgrid(xedges2[:-1], yedges2[:-1])
    heatmap_array2 = cv2.GaussianBlur(heatmap_array2, (3, 3), 0, 0)
    heatmap2 = ax.contourf(x2, y2, heatmap_array2, levels=np.array(levels2), extend='max', cmap='PuRd', alpha=0.8)
    # cb2 = plt.colorbar(heatmap2, ticks=levels2, orientation='vertical', pad=0.01, aspect=45)
    # cb2.set_label('雷暴大风', fontdict={'family': 'simsun'})

    levels3 = np.arange(150, np.max(heatmap_array3) + 1, 80)
    x3, y3 = np.meshgrid(xedges3[:-1], yedges3[:-1])
    heatmap_array3 = cv2.GaussianBlur(heatmap_array3, (3, 3), 0, 0)
    heatmap3 = ax.contourf(x3, y3, heatmap_array3, levels=np.array(levels3), extend='max', cmap='Greens', alpha=0.8)
    # cb3 = plt.colorbar(heatmap3, ticks=levels3, orientation='vertical', pad=0.02, aspect=45)
    # cb3.set_label('冰雹', fontdict={'family': 'simsun'})

    rain_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='red', facecolor='red', alpha=0.3)
    wind_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='b', facecolor='b', alpha=0.3)
    hail_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='g', facecolor='g', alpha=0.3)
    labels = ['强降水', '雷暴大风', '冰雹']
    ax.legend([rain_label, wind_label, hail_label], labels,
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
    filepath_rain = r'/data/PRODUCT/rain_channel_sta/merge_rain6-8.csv'
    filepath_wind = r'/data/PRODUCT/wind_channel_sta/merge_wind6-8.csv'
    filepath_hail = r'/data/PRODUCT/hail_channel_sta/merge_hail6-8.csv'
    rain_df = pd.read_csv(filepath_rain)
    wind_df = pd.read_csv(filepath_wind)
    hail_df = pd.read_csv(filepath_hail)

    rain_df = rain_df.dropna(axis=0, how='any')
    wind_df = wind_df.dropna(axis=0, how='any')
    hail_df = hail_df.dropna(axis=0, how='any')
    title = '强降水-雷暴大风-冰雹-FY4B卫星通道二维频次分布图'
    histogram2d_1(rain_df.BT13, rain_df.BTD09_13, wind_df.BT13, wind_df.BTD09_13, hail_df.BT13, hail_df.BTD09_13, 'BT13(K)', 'BTD09_13(℃)', title)
    histogram2d_2(rain_df.BT13, rain_df.BTD09_10, wind_df.BT13, wind_df.BTD09_10, hail_df.BT13, hail_df.BTD09_10, 'BT13(K)', 'BTD09_10(℃)', title)
    # histogram2d_3(rain_df.BT13, rain_df.BTD14_13, wind_df.BT13, wind_df.BTD14_13, hail_df.BT13, hail_df.BTD14_13, 'BT13(K)', 'BTD14_13(℃)', title)
    # histogram2d_4(rain_df.BTD09_13, rain_df.BTD14_13, wind_df.BTD09_13, wind_df.BTD14_13, hail_df.BTD09_13, hail_df.BTD14_13, 'BTD09_13(℃)', 'BTD14_13(℃)', title)
    # histogram2d_5(rain_df.BTD09_13, rain_df.BTD09_10, wind_df.BTD09_13, wind_df.BTD09_10, hail_df.BTD09_13, hail_df.BTD09_10, 'BTD09_13(℃)', 'BTD09_10(℃)', title)
    # histogram2d_6(rain_df.BTD09_10, rain_df.BTD14_13, wind_df.BTD09_10, wind_df.BTD14_13, hail_df.BTD09_10, hail_df.BTD14_13, 'BTD09_10(℃)', 'BTD14_13(℃)', title)