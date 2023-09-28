import glob
import logging
import os.path
import sys
import meteva.base as meb
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from datetime import datetime, timedelta
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import numpy as np
import matplotlib.patches as mpatches
from cartopy.io.shapereader import Reader
from pathlib import Path
plt.rcParams.update({
    'font.sans-serif': 'Times New Roman',
    'font.size': 14
    })
plt.rcParams['axes.unicode_minus']=False

china_shp = r'D:\data\datasource\Geoserver\Geoserver\全国边界线\chinaGJSJ\china_20220325.shp'
worldmap_shp = r'D:\data\datasource\Geoserver\Geoserver\全国边界线\coastLine\worldmap.shp'
coastline_shp = r'D:\data\datasource\Geoserver\Geoserver\全国边界线\coastLine\ne_10m_coastline.shp'
southsea_png = r'D:\data\datasource\Geoserver\Geoserver\全国边界线\coastLine\white.png'
ticks = [0.1, 5, 10, 15, 20, 25, 50]
cmap_swe = ['#B6EDF0', '#8AC6EB', '#60A3E6', '#1F83E0', '#2259C7', '#1A32AB', '#0A0A91']


def contourf_SWE(infile, outfile, obs_time):
    #获取数据经纬度及二维矩阵
    if os.path.exists(infile):
        xr_data = meb.read_griddata_from_nc(infile)
    else:
        logging.error('输入文件不存在')
        return
    plt.figure(figsize=(16, 9), dpi=120)
    ax = plt.axes(projection=ccrs.PlateCarree())
    plt.title('[积雪深度]', loc='left', fontsize=20, fontdict={'family': 'simhei'})
    plt.title('CST: ' + obs_time.strftime('%Y-%m-%d'), loc='right', fontsize=20)
    LAT = xr_data.lat.to_numpy()
    LON = xr_data.lon.to_numpy()
    xr_data_array = np.squeeze(xr_data.data)
    #设置xy轴坐标
    box, xystep = [np.min(LON), np.max(LON), np.min(LAT), np.max(LAT)], 0.05
    # ax.set_xticks(np.arange(int(box[0]), box[1] + xystep, 10)) #xstep * 100
    # ax.set_yticks(np.arange(int(box[2]), box[3] + xystep, 10))
    ax.set_xticks(list(map(lambda x: int(x), np.linspace(box[0], box[1], 5)))) #xstep * 100
    ax.set_yticks(list(map(lambda x: int(x), np.linspace(box[2], box[3], 5))))
    ax.set_extent(box, crs=ccrs.PlateCarree())
    plt.tick_params(axis="both", which="major", width=1, length=5)

    #设置经纬度显示格式
    # zero_direction_label用来设置经度的0度加不加E和W
    lon_formatter = LongitudeFormatter(zero_direction_label=False)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)

    l, b, w, h = ax.get_position().bounds
    cax = plt.axes([l, b - h * 0.12, w, h * 0.03])
    # 绘制等值线填充图
    lon_mesh, lat_mesh = np.meshgrid(LON, LAT)
    cs = ax.contourf(lon_mesh, lat_mesh, xr_data_array, colors=cmap_swe, levels=ticks, extend='max', extendfrac='auto')
    #aspect：色标宽度, shrink：色标缩放
    plt.colorbar(cs, cax=cax, orientation='horizontal')

    # 标注矢量边界
    china_reader, worldmap_reader, coastline_reader = Reader(china_shp), Reader(worldmap_shp), Reader(coastline_shp)
    enshicity = cfeature.ShapelyFeature(china_reader.geometries(), ccrs.PlateCarree(), edgecolor='k', facecolor='none')
    ax.add_feature(enshicity, linewidth=0.5)  # 添加市界细节
    enshicity = cfeature.ShapelyFeature(worldmap_reader.geometries(), ccrs.PlateCarree(), edgecolor='grey', facecolor='none')
    ax.add_feature(enshicity, linewidth=0.3)  # 添加市界细节
    enshicity = cfeature.ShapelyFeature(coastline_reader.geometries(), ccrs.PlateCarree(), edgecolor='grey', facecolor='none')
    ax.add_feature(enshicity, linewidth=0.3)  # 添加市界细节
    ax.add_feature(cfeature.RIVERS, edgecolor='b', alpha=0.1)

    #保存文件
    if not os.path.exists(os.path.dirname(outfile)):
        os.makedirs(os.path.dirname(outfile))
    plt.savefig(outfile, bbox_inches='tight')
    print('成功输出至：' + outfile)
    plt.close()

def contourf_SNC(infile, outfile, obs_time):
    #获取数据经纬度及二维矩阵
    if os.path.exists(infile):
        xr_data = meb.read_griddata_from_nc(infile)
    else:
        logging.error('输入文件不存在')
        return
    plt.figure(figsize=(16, 9), dpi=120)
    ax = plt.axes(projection=ccrs.PlateCarree())
    plt.title('[雪盖]', loc='left', fontsize=20, fontdict={'family': 'simhei'})
    plt.title('CST: ' + obs_time.strftime('%Y-%m-%d'), loc='right', fontsize=20)
    LAT = xr_data.lat.to_numpy()
    LON = xr_data.lon.to_numpy()
    xr_data_array = np.squeeze(xr_data.data)
    #设置xy轴坐标
    box, xystep = [np.min(LON), np.max(LON), np.min(LAT), np.max(LAT)], 0.05
    # ax.set_xticks(np.arange(int(box[0]), box[1] + xystep, 10)) #xstep * 100
    # ax.set_yticks(np.arange(int(box[2]), box[3] + xystep, 10))
    ax.set_xticks(list(map(lambda x: int(x), np.linspace(box[0], box[1], 5)))) #xstep * 100
    ax.set_yticks(list(map(lambda x: int(x), np.linspace(box[2], box[3], 5))))
    ax.set_extent(box, crs=ccrs.PlateCarree())
    plt.tick_params(axis="both", which="major", width=1, length=5)

    #设置经纬度显示格式
    # zero_direction_label用来设置经度的0度加不加E和W
    lon_formatter = LongitudeFormatter(zero_direction_label=False)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    # 绘制等值线填充图
    lon_mesh, lat_mesh = np.meshgrid(LON, LAT)
    ax.contourf(lon_mesh, lat_mesh, xr_data_array, colors=['#FFFFFF', '#00D0C7'], levels=[0, 0.1], extend='max')

    # 标注矢量边界
    china_reader, worldmap_reader, coastline_reader = Reader(china_shp), Reader(worldmap_shp), Reader(coastline_shp)
    enshicity = cfeature.ShapelyFeature(china_reader.geometries(), ccrs.PlateCarree(), edgecolor='k', facecolor='none')
    ax.add_feature(enshicity, linewidth=0.5)  # 添加市界细节
    enshicity = cfeature.ShapelyFeature(worldmap_reader.geometries(), ccrs.PlateCarree(), edgecolor='grey', facecolor='none')
    ax.add_feature(enshicity, linewidth=0.3)  # 添加市界细节
    enshicity = cfeature.ShapelyFeature(coastline_reader.geometries(), ccrs.PlateCarree(), edgecolor='grey', facecolor='none')
    ax.add_feature(enshicity, linewidth=0.3)  # 添加市界细节
    ax.add_feature(cfeature.RIVERS, edgecolor='b', alpha=0.1)
    snow_label = mpatches.Rectangle((0, 0), 1, 1, edgecolor='#00D0C7', facecolor='#00D0C7')
    labels = ['雪盖']
    plt.legend([snow_label], labels, bbox_to_anchor=(0.99, 0.08), frameon=False, prop={'family': 'simhei'})

    #保存文件
    if not os.path.exists(os.path.dirname(outfile)):
        os.makedirs(os.path.dirname(outfile))
    plt.savefig(outfile, bbox_inches='tight')
    print('成功输出至：' + outfile)
    plt.close()

if __name__ == '__main__':
    infile_SWE = r"D:\data\PRODUCT\{var}\{date_T:%Y}\{date_T:%Y%m%d}\{date_T:%Y%m%d}_SD.nc"
    outfile_SWE = r"D:\data\PRODUCT\{var}\{date_T:%Y}\{date_T:%Y%m%d}\{date_T:%Y%m%d}_SD.png"
    infile_SNC = r"D:\data\PRODUCT\{var}\{date_T:%Y}\{date_T:%Y%m%d}\{date_T:%Y%m%d}_SNC.nc"
    outfile_SNC = r"D:\data\PRODUCT\{var}\{date_T:%Y}\{date_T:%Y%m%d}\{date_T:%Y%m%d}_SNC.png"

    stime, etime, label = None, None, None
    if len(sys.argv) == 2:
        etime = datetime.now().replace(hour=0)
        stime = etime - timedelta(days=2)
    elif len(sys.argv) == 4:
        stime = datetime.strptime(sys.argv[1].ljust(8, '0'), '%Y%m%d')
        etime = datetime.strptime(sys.argv[2].ljust(8, '0'), '%Y%m%d')
    else:
        logging.error('输入参数有误')
    label = sys.argv[-1]
    begin_t = stime
    while begin_t <= etime:
        if label == 'SWE':
            infile_path = infile_SWE.format(var=label, date_T=begin_t)
            outfile_path = outfile_SWE.format(var=label, date_T=begin_t)
            contourf_SWE(infile_path, outfile_path, begin_t)
        elif label == 'SNC':
            infile_path = infile_SNC.format(var=label, date_T=begin_t)
            outfile_path = outfile_SNC.format(var=label, date_T=begin_t)
            contourf_SNC(infile_path, outfile_path, begin_t)
        else:
            logging.error('输入参数有误')
        begin_t += timedelta(days=1)