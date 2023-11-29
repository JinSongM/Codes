# -- coding: utf-8 --
# @Time : 2023/8/28 10:26
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : rain_radar.py
# @Software: PyCharm
import bz2
import os, glob
import sys, cv2
import numpy as np
import netCDF4 as nc
import pandas as pd
import meteva.base as meb
from datetime import datetime, timedelta

south_lat, north_lat, east_lon, west_lon, M4000_resolution = 10, 60, 140, 70, 0.04

def creat_M3_grd(M3_grd):
    """
    构建m3标准格式
    :param M3_grd: Dataframe
    :return:
    """
    # 构建站点数据标准格式
    M3_grd = M3_grd
    sta = meb.sta_data(M3_grd, columns=["lon", "lat"])
    meb.set_stadata_coords(sta, level=0, time=datetime(2023, 1, 1, 8, 0), dtime=0)
    return sta

def creat_M4_grd(lon, lat, data_array, name, gtime):
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
    meb.set_griddata_coords(grd, name="FY4B", level_list=[0], gtime=[gtime], dtime_list=[1], member_list=[name])
    return grd

def get_rain_file(d_date: datetime):
    # 读取强降水数据
    rain_dict = {}
    time_temp = d_date
    try:
        filename = '{d_time:%Y%m%d}/{d_time:%Y%m%d%H%M}.000'
        path = r"/data/2023sk/rain"
        filepath = os.path.join(path, filename.format(d_time=d_date))
        rain_sta = meb.read_stadata_from_micaps3(filepath)
        print('读取强降水数据: ' + time_temp.strftime('%Y%m%d%H%M'))
        rain_sta_filter = rain_sta[(rain_sta.data0 >= 20) & (rain_sta.data0 < 50)]
        # rain_sta_filter = rain_sta[(rain_sta.data0 >= 50) & (rain_sta.data0 < 80)]
        # rain_sta_filter = rain_sta[rain_sta.data0 >= 80]
        if rain_sta_filter.empty:
            return None
        rain_dict[time_temp.strftime('%Y%m%d%H%M')] = rain_sta_filter
        return rain_dict
    except:
        return None

def get_radar(d_date: datetime):
    # 读取雷达数据
    radar_dict = {}
    time_obs = d_date
    try:
        radar_format = r'/mnt/radar_data/SWAN/MCR/%Y/%Y%m%d/Z_OTHE_RADAMCR_%Y%m%d%H%M00.bin.bz2'
        radar_files = datetime.strftime(time_obs, radar_format)
        f = bz2.open(radar_files, 'rb')
        radar_grd = meb.decode_griddata_from_swan_d131_byteArray(f.read())
        print('读取雷达数据: ' + time_obs.strftime('%Y%m%d%H%M'))
        radar_grd.name = 'radar'
        radar_dict[time_obs.strftime('%Y%m%d%H%M')] = radar_grd
    except:
        return None
    return radar_dict

def get_radar_sta(time_list, outfile):
    radar_list = []
    for time_obs in time_list:
        try:
            rain_dict = get_rain_file(time_obs)
            if rain_dict is None:
                print('--' * 40)
                continue
            time_utc = time_obs - timedelta(hours=8)
            radar_dict = get_radar(time_utc)
            if radar_dict is None:
                print('--' * 40)
                continue
            sta = rain_dict.get(time_obs.strftime('%Y%m%d%H%M'))
            grd_channels = radar_dict.get(time_utc.strftime('%Y%m%d%H%M'))
            sta_channel = meb.interp_gs_nearest(grd_channels, sta)
            eigenvalue = sta_channel[['time', 'lon', 'lat', 'data0']]
            eigenvalue = eigenvalue[eigenvalue['data0'] > 0]
            radar_list.append(eigenvalue)
            print('##' * 40)
        except Exception as e:
            print(e)
    return [radar_list]

def write_channel_sta_to_csv(BT_list, outfile):
    DF_list = [pd.DataFrame() for i in range(len(BT_list))]
    for i in range(len(BT_list)):
        for j in range(len(BT_list[i])):
            DF_list[i] = pd.concat([DF_list[i], BT_list[i][j]])
    for i in range(len(DF_list)):
        outpath = outfile.format(label='radar')
        if not os.path.exists(os.path.dirname(outpath)):
            os.makedirs(os.path.dirname(outpath))
        DF_list[i].to_csv(outpath, index = False)
        print('成功输出至' + outpath)

if __name__ == '__main__':
    time_list = []
    start_time, end_time = datetime.strptime(sys.argv[1], '%Y%m%d%H%M'), datetime.strptime(sys.argv[2], '%Y%m%d%H%M')
    outfile_m3 = r'/data/PRODUCT/rain_radar_sta/20/{d_time:%Y}/{d_time:%Y%m%d}/{d_time:%Y%m%d%H%M}_{label}.m3'
    outfile_csv = r'/data/PRODUCT/rain_radar_sta/20/{label}.csv'
    while start_time <= end_time:
        time_list.append(start_time)
        start_time += timedelta(minutes=10)
    radar_list = get_radar_sta(time_list, outfile_m3)
    write_channel_sta_to_csv(radar_list, outfile_csv)