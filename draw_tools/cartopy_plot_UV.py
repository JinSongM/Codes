# -- coding: utf-8 --
# @Time : 2023/5/22 11:45
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : cartopy_plot_UV.py
# @Software: PyCharm
import glob
import os.path
import sys
import xarray as xr
import matplotlib.pyplot as plt
import meteva.base as meb
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from datetime import datetime, timedelta
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import numpy as np
from cartopy.io.shapereader import Reader
import matplotlib.colors as colors

plt.rcParams.update({
    'font.family': 'simsun',
    'font.sans-serif': 'Times New Roman',
    'font.size': 14
    })
plt.rcParams['axes.unicode_minus']=False

china_shp = r'D:\data\datasource\Geoserver\Geoserver\全国边界线\chinaGJSJ\china_20220325.shp'
worldmap_shp = r'D:\data\datasource\Geoserver\Geoserver\全国边界线\coastLine\worldmap.shp'
coastline_shp = r'D:\data\datasource\Geoserver\Geoserver\全国边界线\coastLine\ne_10m_coastline.shp'
southsea_png = r'D:\data\datasource\Geoserver\Geoserver\全国边界线\coastLine\white.png'

def UV_BARBS(UV_dict, box, begin_time, cst, regrid_shape, out_file):
    transform = ccrs.PlateCarree()
    plt.figure(figsize=(16, 9), dpi=120)
    ax = plt.axes(projection=transform)
    plt.title('[ECMWF]10米风', loc='left', fontsize=18, fontdict={'family': 'simhei'})
    LAT = UV_dict['lat']
    LON = UV_dict['lon']
    U10 = UV_dict['u10_array']
    V10 = UV_dict['v10_array']

    box, xstep, ystep = box, 0.01, 0.01
    #[np.min(LON), np.max(LON), np.min(LAT), np.max(LAT)]
    ax.set_xticks(np.arange(int(box[0]), box[1] + xstep, 20)) #xstep * 100
    ax.set_yticks(np.arange(int(box[2]), box[3] + ystep, 10))
    ax.set_extent(box, crs=ccrs.PlateCarree())
    plt.tick_params(axis="both", which="major", width=1, length=5)

    OBS_time = begin_time
    FST_time = OBS_time + timedelta(hours=int(cst))
    # 添加描述信息
    obs_time_dc = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(OBS_time)
    fst_time_dc = '预报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(FST_time)
    forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时'.format(int(cst))
    # plt.title(forcast_info, loc='right', fontsize=18, fontdict={'family': 'simhei'})
    ax.text(0.01, 0.98, forcast_info, transform=ax.transAxes, size=12, va='top',
            ha='left', bbox=dict(facecolor='#FFFFFFCC', edgecolor='black', pad=3.0), zorder=20)
    # 标注坐标轴
    china_reader, worldmap_reader, coastline_reader = Reader(china_shp), Reader(worldmap_shp), Reader(coastline_shp)
    enshicity = cfeature.ShapelyFeature(china_reader.geometries(), transform, edgecolor='k', facecolor='none')
    ax.add_feature(enshicity, linewidth=0.7)  # 添加市界细节
    enshicity = cfeature.ShapelyFeature(worldmap_reader.geometries(), transform, edgecolor='grey', facecolor='none')
    ax.add_feature(enshicity, linewidth=0.6)  # 添加市界细节
    enshicity = cfeature.ShapelyFeature(coastline_reader.geometries(), transform, edgecolor='grey', facecolor='none')
    ax.add_feature(enshicity, linewidth=0.6)  # 添加市界细节
    # ax.add_feature(cfeature.STATES.with_scale('50m'), edgecolor='grey', alpha=0.8)
    # ax.add_feature(cfeature.COASTLINE.with_scale('50m'), edgecolor='grey', alpha=0.8)

    # zero_direction_label用来设置经度的0度加不加E和W
    lon_formatter = LongitudeFormatter(zero_direction_label=False)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    ax.barbs(LON, LAT, U10, V10, regrid_shape=regrid_shape, transform=transform, sizes=dict(emptybarb=0), length=6)
    if not os.path.exists(os.path.dirname(out_file)):
        os.makedirs(os.path.dirname(out_file))
    plt.savefig(out_file, bbox_inches='tight')
    print('文件输出至：' + out_file)

def gain_datadict(u10_NC, v10_NC, rate):
    UV_dict = {}
    if os.path.exists(u10_NC) and os.path.exists(v10_NC):
        u10 = meb.read_griddata_from_nc(u10_NC)
        v10 = meb.read_griddata_from_nc(v10_NC)
        UV_dict['lon'] = u10.lon.to_numpy()
        UV_dict['lat'] = u10.lat.to_numpy()
        UV_dict['u10_array'] = u10.data.reshape(u10.data.shape[-2], u10.data.shape[-1])
        UV_dict['v10_array'] = v10.data.reshape(u10.data.shape[-2], u10.data.shape[-1])
        return True, UV_dict
    else:
        return None, UV_dict

if __name__ == '__main__':
    u10_fmt = r"\\192.168.0.4\nbm\ECMWF\U10\{rt:%Y%m%d%H}\{rt:%Y%m%d%H}.{cst:03d}.nc"
    v10_fmt = r"\\192.168.0.4\nbm\ECMWF\V10\{rt:%Y%m%d%H}\{rt:%Y%m%d%H}.{cst:03d}.nc"
    OUT_PAT = r"\\192.168.0.4\nbm\ECMWF\Result\{rt:%Y%m%d%H}\{rt:%Y%m%d%H}.{cst:03d}.png"
    box = [70, 140, 10, 60]
    if len(sys.argv) == 4:
        stime = datetime.strptime(sys.argv[1], '%Y%m%d%H')
        etime = datetime.strptime(sys.argv[2], '%Y%m%d%H')
        regrid_shape = int(sys.argv[3])
    else:
        stime = datetime.now().replace(hour=0)
        etime = datetime.now().replace(hour=0)
        regrid_shape = 30

    begin_time = stime
    while begin_time <= etime:
        for cst in [i for i in range(12, 24, 12)]:
            try:
                u10_path = u10_fmt.format(rt=begin_time, cst=cst)
                v10_path = v10_fmt.format(rt=begin_time, cst=cst)
                bool, UV_dict = gain_datadict(u10_path, v10_path, regrid_shape)

                if bool:
                    out_file = OUT_PAT.format(rt=begin_time, cst=cst)
                    UV_BARBS(UV_dict, box, begin_time, cst, regrid_shape, out_file)
                begin_time += timedelta(days=1)
            except Exception as e:
                begin_time += timedelta(days=1)
                print(e)