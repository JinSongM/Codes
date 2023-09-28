import glob
import random
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from datetime import datetime, timedelta
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import numpy as np
from cartopy.io.shapereader import Reader
import matplotlib.colors as colors

plt.rcParams.update({
    'font.serif': 'Times New Roman',
    'font.size': 18
    })
plt.rcParams['axes.unicode_minus']=False

'''
1 plt.rcParams[’axes.unicode_minus’] = False 字符显示
2 plt.rcParams[’font.sans-serif’] = ‘SimHei’ 设置字体
线条样式：lines
3 plt.rcParams[’lines.linestyle’] = ‘-.’ 线条样式
4 plt.rcParams[’lines.linewidth’] = 3 线条宽度
5 plt.rcParams[’lines.color’] = ‘blue’ 线条颜色
6 plt.rcParams[’lines.marker’] = None 默认标记
7 plt.rcParams[’lines.markersize’] = 6 标记大小
8 plt.rcParams[’lines.markeredgewidth’] = 0.5 标记附近的线宽
横、纵轴：xtick、ytick
9 plt.rcParams[’xtick.labelsize’] 横轴字体大小
10 plt.rcParams[’ytick.labelsize’] 纵轴字体大小
11 plt.rcParams[’xtick.major.size’] x轴最大刻度
12 plt.rcParams[’ytick.major.size’] y轴最大刻度
figure中的子图：axes
13 plt.rcParams[’axes.titlesize’] 子图的标题大小
14 plt.rcParams[’axes.labelsize’] 子图的标签大小
图像、图片：figure、savefig
15 plt.rcParams[’figure.dpi’] 图像分辨率
16 plt.rcParams[’figure.figsize’] 图像显示大小
17 plt.rcParams[’savefig.dpi’] 图片像素
'''

china_shp = r'D:\data\datasource\Geoserver\Geoserver\全国边界线\chinaGJSJ\china_20220325.shp'
worldmap_shp = r'D:\data\datasource\Geoserver\Geoserver\全国边界线\coastLine\worldmap.shp'
coastline_shp = r'D:\data\datasource\Geoserver\Geoserver\全国边界线\coastLine\ne_10m_coastline.shp'
southsea_png = r'D:\data\datasource\Geoserver\Geoserver\全国边界线\coastLine\white.png'

def SW_vortex(Dict):

    plt.figure(figsize=(16, 9), dpi=120)
    ax = plt.axes(projection=ccrs.PlateCarree())

    box, xstep, ystep = [100, 125, 20, 36], 5, 4
    ax.set_xticks(np.arange(int(box[0]), box[1] + xstep, xstep)) #xstep * 100
    ax.set_yticks(np.arange(int(box[2]), box[3] + ystep, ystep))
    ax.set_extent(box, crs=ccrs.PlateCarree())
    plt.tick_params(axis="both", which="major", width=1, length=10, pad=10)

    # 标注坐标轴
    china_reader, worldmap_reader, coastline_reader = Reader(china_shp), Reader(worldmap_shp), Reader(coastline_shp)
    enshicity = cfeature.ShapelyFeature(china_reader.geometries(), ccrs.PlateCarree(), edgecolor='grey', facecolor='none')
    ax.add_feature(enshicity, linewidth=0.6)  # 添加市界细节
    enshicity = cfeature.ShapelyFeature(worldmap_reader.geometries(), ccrs.PlateCarree(), edgecolor='grey', facecolor='none')
    ax.add_feature(enshicity, linewidth=0.6)  # 添加市界细节
    enshicity = cfeature.ShapelyFeature(coastline_reader.geometries(), ccrs.PlateCarree(), edgecolor='grey', facecolor='none')
    ax.add_feature(enshicity, linewidth=0.6)  # 添加市界细节
    # ax.add_feature(cfeature.STATES.with_scale('50m'), edgecolor='grey', alpha=0.8)
    # ax.add_feature(cfeature.COASTLINE.with_scale('50m'), edgecolor='grey', alpha=0.8)

    # zero_direction_label用来设置经度的0度加不加E和W
    lon_formatter = LongitudeFormatter(zero_direction_label=False)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    for key, value in Dict.items():
        ax.plot(value[0], value[1], color='m', linewidth=2, transform = ccrs.PlateCarree(), marker='o', markersize='10', markerfacecolor='none', label=key)
        for j in range(len(value[2])):
            plot_text = (value[3] + timedelta(hours=int(value[2][j]))).strftime('%d.%H')
            print(value[3], int(value[2][j]), plot_text)
            plt.text(value[0][j]-0.5, value[1][j]-0.5, plot_text, transform = ccrs.PlateCarree(), fontsize=14)
    plt.legend()
    plt.savefig('SW_vortex.png', bbox_inches='tight')

def read_csv(csv_file):
    report_time, cst, id, lon, lat = [], [], [], [], []
    with open(csv_file) as file:
        for values in file:
            value_sp = values.split(',')
            report_time.append(value_sp[2])
            cst.append(value_sp[3])
            id.append(value_sp[4])
            lon.append(value_sp[5])
            lat.append(value_sp[6])
    report_time_hour = datetime.strptime(report_time[1], '%Y-%m-%d %H:%M:%S')
    dict = {
        'cst': cst[1:],
        'id': id[1:],
        'lon': lon[1:],
        'lat': lat[1:]
    }
    df = pd.DataFrame(dict)
    return report_time_hour, cst[1:], id[1:], lon[1:], lat[1:], df

def gain_vortex_road(cst, df):
    plot_cst, plot_lon, plot_lat = [], [], []
    cst_list = sorted(list(set(cst)))
    df0 = df[df['cst'] == cst_list[0]]
    plot_cst.append(df0.cst.values[0])
    plot_lon.append(float(df0.lon.values[0]))
    plot_lat.append(float(df0.lat.values[0]))
    for i in cst_list[1:]:
        df_temp = df[df['cst'] == i].sort_values(by=['lon'])
        lon_temp, lat_temp = list(df_temp.lon.values), list(df_temp.lat.values)
        for j in range(len(lon_temp)):
            if float(lon_temp[j]) > float(plot_lon[-1]):
                plot_cst.append(i)
                plot_lon.append(float(lon_temp[j]))
                plot_lat.append(float(lat_temp[j]))
                break
    return plot_cst, plot_lon, plot_lat


if __name__ == '__main__':
    Dict = dict()
    # csv_file = r'/data2/cpvs/vortexSW/data/JavaData/{model_name}/wind/{report_time:%Y}/{report_time:%Y%m%d%H}/veri_png/vortex/cl_df.txt'
    csv_file = r'D:\data\datasource/cl_df.txt'
    report_time_hour, cst, id, lon, lat, df  = read_csv(csv_file)
    plot_cst, plot_lon, plot_lat = gain_vortex_road(cst, df)
    Dict['CMA_GFS ' + report_time_hour.strftime('%m%d')] = [plot_lon, plot_lat, plot_cst, report_time_hour]

    SW_vortex(Dict)