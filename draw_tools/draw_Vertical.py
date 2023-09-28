# -- coding: utf-8 --
# @Time : 2023/7/31 17:42
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : draw_Vertical.py
# @Software: PyCharm
import os.path
import sys
import meteva
import pandas as pd
import meteva.base as meb
import matplotlib.pyplot as plt
from  matplotlib import font_manager
from datetime import datetime, timedelta
import numpy as np
import matplotlib.colors as colors
# font_manager.fontManager.addfont('/mnt/shortQPF/simhei.ttf')
plt.rcParams.update({
    'font.serif': 'Times New Roman',
    'font.size': 14
    })
plt.rcParams['axes.unicode_minus']=False


def creat_M3_grd(ID_LIST, Lon_list, Lat_list):
    data = {
        '站号': ID_LIST,
        "经度": Lon_list,
        "纬度": Lat_list,
    }
    # 构建站点数据标准格式
    M3_grd = pd.DataFrame(data)
    sta = meb.sta_data(M3_grd, columns=["id", "lon", "lat"])
    meb.set_stadata_coords(sta, level=0, dtime=0)
    return sta

def creat_M4_grd(lon, lat, data_array):
    """
    构建m4标准格式
    :param Lon_list: 经度列表[起始经度，终止经度，经向间隔]
    :param Lat_list: 维度列表
    :param Data_list: 数据列表
    :return:
    """
    grid0 = meb.grid(lon, lat)
    data = data_array
    grd = meb.grid_data(grid0, data=data)
    meb.set_griddata_coords(grd, name="data0", level_list=[0], gtime=["2023-01-01:08"],
                            dtime_list=[1], member_list=["models"])
    return grd

def statistic_Dict(argvs, infile):
    Dict, Dict_array = {}, {}
    report_time = datetime.strptime(argvs[0], '%Y%m%d%H')
    lon_roi = float(argvs[1])
    lat_roi = float(argvs[2])
    lev_list = argvs[3].split(',') #[100, 200, 300, 400, 500]
    cst_list = argvs[4].split(',') #[339, 342]
    sta_m3_roi = creat_M3_grd([0], [lon_roi], [lat_roi])

    for element in ['u', 'v', 'r', 't']:
        zeros_array = np.zeros((len(lev_list), len(cst_list)))
        for i in range(len(cst_list)):
            for j in range(len(lev_list)):
                try:
                    file_path = infile.format(element=element, lev=lev_list[j], report_time=report_time, cst=int(cst_list[i]))
                    element_value = float(meb.interp_gs_linear(meb.read_griddata_from_micaps4(file_path), sta_m3_roi).data0)
                    Dict[element +'_'+ cst_list[i] +'_'+ lev_list[j]] = element_value
                    zeros_array[j][i] = element_value
                except Exception as e:
                    print(e)
        grd_element = creat_M4_grd([1, len(cst_list), 1], [1, len(lev_list), 1], zeros_array)
        if element in ['r', 't']:
            grid_mesh = meb.grid([1, len(cst_list), 0.01], [1, len(lev_list), 0.01])
            grd_element = meb.interp_gg_linear(grd_element, grid_mesh)
            grd_element = meb.comp.smooth(grd_element, 5)
        Dict_array[element] = grd_element
    return Dict_array

def vertical_Plot(argvs, data_dict, outfile):
    report_time = datetime.strptime(argvs[0], '%Y%m%d%H')
    lon_roi, lat_roi = argvs[1], argvs[2]
    lev_list = argvs[3].split(',') #[100, 200, 300, 400, 500]
    cst_list = argvs[4].split(',')

    fig = plt.figure(figsize=(12, 10), dpi=300)
    ax = plt.axes()
    plt.title('风温湿廓线图\n', loc='center', fontsize=20, fontdict={'family': 'simhei'})

    #设置xy轴坐标
    box, xstep, ystep = [1, len(cst_list), 1, len(lev_list), 0.1], 1, 1
    xtk_labels, ytk_labels = [(report_time+timedelta(hours=int(i))).strftime('%d/%H') for i in cst_list], lev_list

    # ax.xaxis.set_minor_locator(MultipleLocator(1/3))
    # ax.yaxis.set_minor_locator(MultipleLocator(0.25))
    ax.set_yscale('log')  # 设置y轴为对数坐标
    plt.xlim(box[0] - xstep/5, box[1] + xstep/5)
    plt.ylim(box[2] - ystep, box[3] + ystep)
    plt.xticks(np.arange(box[0], box[1] + xstep, 1), xtk_labels)
    plt.yticks(np.arange(box[2], box[3] + xstep, 1), ytk_labels)
    plt.ylabel('Pressure(hpa)')
    ax.invert_yaxis()
    plt.locator_params(axis='x', nbins=6)
    plt.tick_params(axis="both", which="major", width=1, length=5)

    # 添加描述信息
    # forcast_info = '起报时间:{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(report_time)
    forcast_info1 = 'CST:{0:%Y}-{0:%m}-{0:%d} {0:%H}:00 +{1:03d}-{2:03d}H'.format(report_time, int(cst_list[0]), int(cst_list[-1]))
    forcast_info2 = '[longitude:{}°E, latitude:{}°N]'.format(lon_roi, lat_roi)
    plt.title(forcast_info1, loc='right', fontsize=14)
    plt.title(forcast_info2, loc='left', fontsize=14)

    # 绘制相对湿度
    LON, LAT = np.meshgrid(data_dict.get('r').lon.to_numpy(), data_dict.get('r').lat.to_numpy())
    colorlevel = [50, 55, 60, 65, 70, 75, 80, 85, 90, 95]
    # cmap_col = ['#FFFFFF', '#C8FFBE', '#96F58C', '#50F050', '#1FB31F', '#0DA10D', '#079407']
    # cmap = colors.ListedColormap(cmap_col)
    cmap = plt.cm.YlGn
    norm = colors.BoundaryNorm(colorlevel, cmap.N)
    r_roi = np.squeeze(data_dict.get('r').data)
    r_roi[r_roi < colorlevel[0]] = np.nan
    r_cs = plt.pcolormesh(LON, LAT, r_roi, cmap=cmap, norm=norm, alpha=0.8)
    l, b, w, h = ax.get_position().bounds
    cax0 = fig.add_axes([l+1.02*w, b, w*0.02, h])
    plt.colorbar(r_cs, cax=cax0, aspect=30, ticklocation='right', orientation='vertical', extend='max', ticks=colorlevel)
    # 绘制温度
    tem_cs = ax.contour(LON, LAT, np.squeeze(data_dict.get('t').data), levels = np.arange(-68, 42, 4),
                        colors='red', linewidths=0.75)
    ax.clabel(tem_cs, inline=1, fontsize=10, fmt='%.0f', colors='red')

    # 绘制风羽图
    LON, LAT = np.meshgrid(data_dict.get('u').lon.to_numpy(), data_dict.get('u').lat.to_numpy())
    ax.barbs(LON, LAT, np.squeeze(data_dict.get('u').data), np.squeeze(data_dict.get('v').data),
             barbcolor='b', barb_increments={'half': 2, 'full': 4, 'flag': 20}, sizes=dict(emptybarb=0), length=6)
    #保存文件
    outpath = outfile.format(report_time=report_time)
    if not os.path.exists(os.path.dirname(outpath)):
        os.makedirs(os.path.dirname(outpath))
    plt.savefig(outpath, bbox_inches='tight')
    print('成功输出至：' + outpath)
    plt.close()


if __name__ == '__main__':
    infile = r"/data/EC/{element}/{lev}/{report_time:%Y%m%d%H}/{report_time:%Y%m%d%H}.{cst:03d}"
    outfile = r"/data/PRODUCT/enviroment/Vertical/{report_time:%Y%m%d%H}.png"
    data_dict = statistic_Dict(sys.argv[1:], infile)
    print('数据准备完成')
    vertical_Plot(sys.argv[1:], data_dict, outfile)