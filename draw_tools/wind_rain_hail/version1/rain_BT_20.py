# -- coding: utf-8 --
# @Time : 2023/8/28 10:26
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : rain_BT_20.py
# @Software: PyCharm
import os, glob
import sys, cv2
import numpy as np
import netCDF4 as nc
import pandas as pd
import meteva.base as meb
from datetime import datetime, timedelta

south_lat, north_lat, east_lon, west_lon, M4000_resolution = 10, 60, 140, 70, 0.04
class fy_4b_agri_l1:
    """
    风云4B基础数据类型
    """
    def load_fy4b_data(self, path):
        s_lat, n_lat = float(south_lat), float(north_lat)
        w_lon, e_lon = float(west_lon), float(east_lon)
        self.resolution = float(M4000_resolution)
        geo_range = (s_lat, n_lat, w_lon, e_lon, self.resolution)

        np.seterr(divide='ignore', invalid='ignore')
        with nc.Dataset(path, "r") as da:
            line_begin = da.getncattr('Begin Line Number')

            lat_s, lat_n, lon_w, lon_e, step = [int(100 * x) for x in geo_range]
            lat = np.arange(lat_n, lat_s - 1, -step) / 100
            lon = np.arange(lon_w, lon_e + 1, step) / 100
            lon_mesh, lat_mesh = np.meshgrid(lon, lat)

            line, column = latlon2linecolumn(lat_mesh, lon_mesh, '4000M')
            line = np.rint(line).astype(np.uint16) - line_begin
            column = np.rint(column).astype(np.uint16)

            channel_temp_09 = da['Data']["NOMChannel09"][()][line, column]
            channel_temp_10 = da['Data']["NOMChannel10"][()][line, column]
            channel_temp_13 = da['Data']["NOMChannel13"][()][line, column]
            channel_temp_14 = da['Data']["NOMChannel14"][()][line, column]

            channel_temp_09[channel_temp_09 >= 65534] = 4096
            channel_temp_10[channel_temp_10 >= 65534] = 4096
            channel_temp_13[channel_temp_13 >= 65534] = 4096
            channel_temp_14[channel_temp_14 >= 65534] = 4096

            scalae_value_09 = da['Calibration']["CALChannel09"][()].astype(np.float32)  # 10.7um
            scalae_value_10 = da['Calibration']["CALChannel10"][()].astype(np.float32)  # 12.5um
            scalae_value_13 = da['Calibration']["CALChannel13"][()].astype(np.float32)  # 13.3um
            scalae_value_14 = da['Calibration']["CALChannel14"][()].astype(np.float32)  # 10.7um

            scalae_value_09 = np.append(scalae_value_09, np.nan)
            scalae_value_10 = np.append(scalae_value_10, np.nan)
            scalae_value_13 = np.append(scalae_value_13, np.nan)
            scalae_value_14 = np.append(scalae_value_14, np.nan)

            self.tb_09 = scalae_value_09[channel_temp_09]
            self.tb_10 = scalae_value_10[channel_temp_10]
            self.tb_13 = scalae_value_13[channel_temp_13]
            self.tb_14 = scalae_value_14[channel_temp_14]

def latlon2linecolumn(lat, lon, resolution_str):
    """
    经纬度转换为行列式
    Args:
        lat:
        lon:
        cfg_dict:

    Returns:

    """
    # 地球的半长轴[km]
    ea = 6378.137
    # 地球的短半轴[km]
    eb = 6356.7523
    # 地心到卫星质心的距离[km]
    h = 42164
    # 卫星星下点所在经度
    λD = np.deg2rad(133.0)
    # 列偏移
    coff = {"0500M": 10991.5, "1000M": 5495.5, "2000M": 2747.5, "4000M": 1373.5}
    # 列比例因子
    cfac = {"0500M": 81865099, "1000M": 40932549, "2000M": 20466274, "4000M": 10233137}
    # 行偏移
    loff = coff
    # 行比例因子
    lfac = cfac
    # Step1.检查地理经纬度
    # Step2.将地理经纬度的角度表示转化为弧度表示
    lat = np.deg2rad(lat)
    lon = np.deg2rad(lon)
    # Step3.将地理经纬度转化成地心经纬度
    eb2_ea2 = eb ** 2 / ea ** 2
    λe = lon
    φe = np.arctan(eb2_ea2 * np.tan(lat))
    # Step4.求Re
    cosφe = np.cos(φe)
    re = eb / np.sqrt(1 - (1 - eb2_ea2) * cosφe ** 2)
    # Step5.求r1,r2,r3
    λe_λD = λe - λD
    r1 = h - re * cosφe * np.cos(λe_λD)
    r2 = -re * cosφe * np.sin(λe_λD)
    r3 = re * np.sin(φe)
    # Step6.求rn,x,y
    rn = np.sqrt(r1 ** 2 + r2 ** 2 + r3 ** 2)
    x = np.rad2deg(np.arctan(-r2 / r1))
    y = np.rad2deg(np.arcsin(-r3 / rn))
    # Step7.求c,l
    column = coff[resolution_str] + x * 2 ** -16 * cfac[resolution_str]
    line = loff[resolution_str] + y * 2 ** -16 * lfac[resolution_str]
    return line, column

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

def get_fy4_file_path(d_date: datetime):
    """
    通过时间，获取FY4B的文件
    Args:
        d_date:
        cfg_dict:

    Returns:

    """
    filename = '{d_time:%Y}/{d_time:%Y%m%d}/FY4B-_AGRI--_N_*_1330E_L1-_FDI-_MULT_NOM_{d_time:%Y%m%d%H%M}00*_4000M_V0001.HDF'
    path = r"/mnt/satlake/FY4/FY4B/AGRI/L1/FDI/DISK/4000M"
    filepath = os.path.join(path, filename.format(d_time=d_date))
    files = glob.glob(filepath)
    if len(files) > 0:
        return files[0]
    else:
        return None

def get_fy4_file_channel(d_date: datetime):
    # FY4B卫星数据加载
    fy4b_obj_dict= {}
    time_temp = d_date
    fy4b_obj = fy_4b_agri_l1()
    try:
        fy4_file = get_fy4_file_path(time_temp)
        if fy4_file is None:
            return None
        print('读取FY4B通道数据: ' + d_date.strftime('%Y%m%d%H%M'))
        fy4b_obj.load_fy4b_data(fy4_file)
        lon, lat = [west_lon, east_lon, M4000_resolution], [south_lat, north_lat, M4000_resolution]
        gtime = d_date.strftime('%Y-%m-%d-%H:%M')
        fy4b_channel = {
            # 'BT09': creat_M4_grd(lon, lat, cv2.erode(fy4b_obj.tb_09[::-1], np.ones((5, 5))), 'BT09', gtime),
            # 'BT10': creat_M4_grd(lon, lat, cv2.erode(fy4b_obj.tb_10[::-1], np.ones((5, 5))), 'BT10', gtime),
            'BT13': creat_M4_grd(lon, lat, cv2.erode(fy4b_obj.tb_13[::-1], np.ones((5, 5))), 'BT13', gtime),
            # 'BT14': creat_M4_grd(lon, lat, cv2.erode(fy4b_obj.tb_14[::-1], np.ones((5, 5))), 'BT14', gtime),
            'BTD14_13': creat_M4_grd(lon, lat, cv2.erode((fy4b_obj.tb_14-fy4b_obj.tb_13)[::-1], np.ones((5, 5))), 'BTD14_13', gtime),
            'BTD09_13': creat_M4_grd(lon, lat, cv2.erode((fy4b_obj.tb_09-fy4b_obj.tb_13)[::-1], np.ones((5, 5))), 'BTD09_13', gtime),
            'BTD09_10': creat_M4_grd(lon, lat, cv2.erode((fy4b_obj.tb_09-fy4b_obj.tb_10)[::-1], np.ones((5, 5))), 'BTD09_10', gtime),
        }
        fy4b_obj_dict[time_temp.strftime('%Y%m%d%H%M')] = fy4b_channel
        return fy4b_obj_dict
    except Exception as e:
        print(e)
        return None

def get_TQ_DATA_file(d_date: datetime):
    # 读取闪电数据
    TQ_DATA_dict = {}
    time_temp = d_date
    try:
        filename = '{d_time:%Y}/{d_time:%Y%m%d}/{d_time:%Y_%m_%d_%H_%M}.csv'
        path = r"/data/DLJS/TQ_DATA/ADTD_auto"
        filepath = os.path.join(path, filename.format(d_time=d_date))
        print('读取闪电数据: ' + time_temp.strftime('%Y%m%d%H%M'))
        csv_data = pd.read_csv(filepath)
        light_local = csv_data[['Lon', 'Lat']]
        light_sta = creat_M3_grd(light_local)
        TQ_DATA_dict[time_temp.strftime('%Y%m%d%H%M')] = light_sta
        return TQ_DATA_dict
    except:
        return None

def get_rain_file(d_date: datetime):
    # 读取闪电数据
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

def get_channel_sta(time_list, outfile):
    BT09_list, BT10_list, BT13_list, BT14_list, BTD14_13_list, BTD09_13_list, BTD09_10_list = [], [], [], [], [], [], []
    for time_obs in time_list:
        try:
            rain_dict = get_rain_file(time_obs)
            if rain_dict is None:
                print('--' * 40)
                continue
            time_utc = time_obs - timedelta(hours=8)
            fy4b_channels_dict = get_fy4_file_channel(time_utc)
            if fy4b_channels_dict is None:
                print('--' * 40)
                continue
            sta = rain_dict.get(time_obs.strftime('%Y%m%d%H%M'))
            grd_channels = fy4b_channels_dict.get(time_utc.strftime('%Y%m%d%H%M'))
            for key, value in grd_channels.items():
                sta_channel = meb.interp_gs_nearest(value, sta)
                # meb.write_stadata_to_micaps3(sta_channel, save_path=outfile.format(d_time=time_obs, label=key), creat_dir=True, show=True)
                if key == 'BT09':
                    BT09_list.append(sta_channel[['time', 'lon', 'lat', key]])
                elif key == 'BT10':
                    BT10_list.append(sta_channel[['time', 'lon', 'lat', key]])
                elif key == 'BT13':
                    BT13_list.append(sta_channel[['time', 'lon', 'lat', key]])
                elif key == 'BT14':
                    BT14_list.append(sta_channel[['time', 'lon', 'lat', key]])
                elif key == 'BTD14_13':
                    BTD14_13_list.append(sta_channel[['time', 'lon', 'lat', key]])
                elif key == 'BTD09_13':
                    BTD09_13_list.append(sta_channel[['time', 'lon', 'lat', key]])
                elif key == 'BTD09_10':
                    BTD09_10_list.append(sta_channel[['time', 'lon', 'lat', key]])
            print('##' * 40)
        except Exception as e:
            print(e)
    # return [BT09_list, BT10_list, BT13_list, BT14_list, BTD14_13_list, BTD09_13_list, BTD09_10_list]
    return [BT13_list, BTD14_13_list, BTD09_13_list, BTD09_10_list]

def write_channel_sta_to_csv(BT_list, outfile, label_list):
    DF_list = [pd.DataFrame() for i in range(len(BT_list))]
    for i in range(len(BT_list)):
        for j in range(len(BT_list[i])):
            DF_list[i] = pd.concat([DF_list[i], BT_list[i][j]])
    for i in range(len(DF_list)):
        outpath = outfile.format(label=label_list[i])
        DF_list[i].to_csv(outpath, index = False)
        print('成功输出至' + outpath)

if __name__ == '__main__':
    time_list = []
    start_time, end_time = datetime.strptime(sys.argv[1], '%Y%m%d%H%M'), datetime.strptime(sys.argv[2], '%Y%m%d%H%M')
    label_list = ['BT13','BTD14_13','BTD09_13','BTD09_10']
    outfile_m3 = r'/data/PRODUCT/rain_channel_sta/20/{d_time:%Y}/{d_time:%Y%m%d}/{d_time:%Y%m%d%H%M}_{label}.m3'
    outfile_csv = r'/data/PRODUCT/rain_channel_sta/20/{label}.csv'
    while start_time <= end_time:
        time_list.append(start_time)
        start_time += timedelta(minutes=10)
    BT_list = get_channel_sta(time_list, outfile_m3)
    write_channel_sta_to_csv(BT_list, outfile_csv, label_list)