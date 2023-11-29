# -- coding: utf-8 --
# @Time : 2023/11/20 13:58
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : stats_norm_rain_kde.py
# @Software: PyCharm

import math, bz2
import os, glob
import sys, cv2
import meteva.base as meb
import netCDF4 as nc
from scipy.stats import norm
import numpy as np
import pandas as pd
from matplotlib import colors
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from datetime import datetime, timedelta
from cartopy.io.shapereader import Reader
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter


plt.rcParams.update({
    'font.sans-serif': 'Times New Roman',
    'font.size': 22
    })
plt.rcParams['axes.unicode_minus']=False


south_lat, north_lat, east_lon, west_lon, res = 10, 60, 140, 70, 0.04
lon_grd, lat_grd = [west_lon, east_lon, res], [south_lat, north_lat, res]
class fy_4b_agri_l1:
    """
    读取风云4B通道数据
    Args:
        path: FY4文件
    Returns:

    """
    def load_fy4b_data(self, path):
        s_lat, n_lat = float(south_lat), float(north_lat)
        w_lon, e_lon = float(west_lon), float(east_lon)
        geo_range = (s_lat, n_lat, w_lon, e_lon, res)

        np.seterr(divide='ignore', invalid='ignore')
        with nc.Dataset(path, "r") as da:
            line_begin = da.getncattr('Begin Line Number')

            lat_s, lat_n, lon_w, lon_e, step = [int(100 * x) for x in geo_range]
            lat = np.arange(lat_s, lat_n + 1, step) / 100
            lon = np.arange(lon_w, lon_e + 1, step) / 100
            lon_mesh, lat_mesh = np.meshgrid(lon, lat)

            line, column = self.latlon2linecolumn(lat_mesh, lon_mesh, '4000M')
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

    def latlon2linecolumn(self, lat, lon, resolution_str):
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

class loadData:
    """
    加载统计数据
    params:
    return:
        dataframe
    """
    def __init__(self):
        # 强降水数据
        self.rain0_file = r'/data/PRODUCT/rain_channel_sta/0/merge3/merge_rain0.csv'
        self.rain1_file = r'/data/PRODUCT/rain_channel_sta/20/merge3/merge_rain20.csv'
        self.rain2_file = r'/data/PRODUCT/rain_channel_sta/50/merge3/merge_rain50.csv'
        self.rain3_file = r'/data/PRODUCT/rain_channel_sta/80/merge3/merge_rain80.csv'
        try:
            self.rain_df0 = pd.read_csv(self.rain0_file)
            self.rain_df1 = pd.read_csv(self.rain1_file)
            self.rain_df2 = pd.read_csv(self.rain2_file)
            self.rain_df3 = pd.read_csv(self.rain3_file)

            self.rain0_df = self.rain_df0.dropna(axis=0, how='any')
            self.rain1_df = pd.concat([self.rain_df1, self.rain_df2, self.rain_df3], axis=0)
            self.rain1_df = self.rain1_df.dropna(axis=0, how='any')

            # 标签检验
            labelDf0 = self.rain0_df[channel_list].copy().sample(10000)
            labelDf0['label'] = 0
            labelDf1 = self.rain1_df[channel_list].copy().sample(10000)
            labelDf1['label'] = 1
            merge_df = pd.concat([labelDf0, labelDf1], axis=0)
            filepath = os.path.join(outpathdir, 'label.csv')
            merge_df.to_csv(filepath)

        except Exception as e:
            print(e)


class drawMembership(loadData):
    """
    绘制概率密度-隶属度函数图
    params:
        channel:
        pic_name:
        ytitle:
    return:
        概率密度图
    """

    def __init__(self, channels):
        super().__init__()
        self.eigenvalue_dict = self.eigenvalue(channels)
        self.area_dict, self.weight_list = self.weightvalue()

    def eigenvalue(self, channels):
        dict = {}
        for channel in channels:
            try:
                xdata_0 = np.sort(self.rain0_df.get(channel).to_list())
                kde0 = gaussian_kde(xdata_0)
                xdata_1 = np.sort(self.rain1_df.get(channel).to_list())
                kde1 = gaussian_kde(xdata_1)
                dict[channel] = [kde0, kde1]
            except:
                return None
        return dict

    def weightvalue(self):
        filepath = os.path.join(outpathdir, 'weight.csv')
        if os.path.exists(filepath):
            area_dict = pd.read_csv(filepath)[channel_list]
            area_list = area_dict.values.tolist()
            weight_list = [1 / i[0] for i in area_list]
        else:
            area_dict, weight_list = {}, []
            try:
                channel_dict = {
                    'BT13' : np.arange(160, 341, 0.1),
                    'BTD09_10': np.arange(-16, 5, 0.1),
                    'BTD09_13': np.arange(-80, 5, 0.1),
                    'BTD14_13': np.arange(-16, 5, 0.1),
                }
                for CN, VA in self.eigenvalue_dict.items():
                    xdata = channel_dict.get(CN)
                    area = np.trapz(np.min([VA[1](xdata), VA[0](xdata)], axis=0), xdata)
                    area_dict[CN] = [area]
                    weight_list.append(1 / area)
                pd.DataFrame(area_dict).to_csv(filepath)
            except:
                return None, None
        return area_dict, weight_list

    def membership_weight(self, channel, x):
        try:
            value = self.eigenvalue_dict.get(channel)
            membership = value[1](x) / (value[0](x) + value[1](x))
            weight = float(1 / self.area_dict.get(channel)[0]) * np.sum(self.weight_list)

            return membership, float(weight)
        except Exception as e:
            print(e)
            return None, None

    def draw_norm(self, pic_name, ytitle, ytitle2):
        if self.eigenvalue_dict is None:
            return
        for channel, value in self.eigenvalue_dict.items():
            try:
                fig, ax = plt.subplots(1, 1, figsize=(12, 9))
                # 设置标题
                ax.set_title(pic_name, fontsize=24, fontdict={'family': 'simhei'})
                # 设置X轴标签
                plt.xlabel('{}'.format(channel))
                # 设置Y轴标签
                plt.ylabel('{}'.format(ytitle), fontdict={'family': 'simsun'})
                if channel == 'BT13':
                    x = np.arange(180, 321, 0.1)
                    plt.xlim(xmax=320, xmin=180)
                    plt.ylim(ymax=0.03, ymin=0)
                elif channel == 'BTD09_10':
                    x = np.arange(-16, 1, 0.1)
                    plt.xlim(xmax=0, xmin=-16)
                    plt.ylim(ymax=0.3, ymin=0)
                elif channel == 'BTD09_13':
                    x = np.arange(-80, 1, 0.1)
                    plt.xlim(xmax=0, xmin=-80)
                    plt.ylim(ymax=0.05, ymin=0)
                elif channel == 'BTD14_13':
                    x = np.arange(-10, 3, 0.1)
                    plt.xlim(xmax=2, xmin=-10)
                    plt.ylim(ymax=0.4, ymin=0)
                else:
                    return

                weight = float(self.area_dict.get(channel)[0])
                y1, y2 = value[0](x), value[1](x)
                y = [min(x, y) for x, y in zip(y1, y2)]
                ax.fill_between(x, y, color='blue', alpha=0.2)

                ax.plot(x, y1, 'g--', lw=2, alpha=0.6, label='0~20mm')
                ax.plot(x, y2, 'y-', lw=2, alpha=0.6, label='20~mm')
                plt.legend(frameon=False, loc=1)

                ax2 = ax.twinx()
                plt.ylim(ymax=1, ymin=0)
                membership = y2 / (y1 + y2)
                ax2.plot(x, membership, 'r-', lw=2, alpha=0.6, label='隶属度')
                # 设置Y2轴标签
                plt.ylabel('{}'.format(ytitle2), fontdict={'family': 'simsun'})
                plt.legend(frameon=False, loc=(0.04, 0.92), prop={'family': 'simsun'})
                plt.text(0.05, 0.88, 'Area='+str('%.2f'%weight), transform=plt.gca().transAxes)

                filepath = os.path.join(outpathdir, channel + '_norm.png')
                plt.savefig(fname=filepath, bbox_inches='tight')
                print('绘图成功：{}'.format(os.path.basename(filepath)))
            except Exception as e:
                print(e)

    def cal_Q_scatter(self, dict:dict, cal):
        """
        估算站点分类强对流概率
        params:
            dict：各特征量字典
        return:
            probability：概率
            probability：强对流
        """
        numerator = []
        denominator = []
        for key, value in dict.items():
            membership, weight = self.membership_weight(key, value)
            print('{}:{:.2f}\t隶属度:{:.2f}\t权重:{:.2f}'.format(key, value, membership, weight))
            if membership is None or weight is None:
                return None
            numerator.append(membership * weight)
            denominator.append(weight)
        probability = np.sum(numerator) / np.sum(denominator)
        print('##' * 20)
        if probability > cal:
            label = '1'
        else:
            label = '0'
        return probability, label

    def cal_Q_grd(self, dict:dict, cal):
        """
        估算格点分类强对流概率
        params:
            dict：各特征量字典
        return:
            probability：概率
            probability：强对流
        """
        numerator = []
        denominator = []
        for key, value in dict.items():
            if key in channel_list:
                membership, weight = self.membership_weight(key, value)
                if membership is None or weight is None:
                    return None
                numerator.append(membership * weight)
                denominator.append(weight)
        probability = np.sum(numerator, axis=0) / np.sum(denominator)
        print('概率系数计算完成，阈值：{}'.format(cal))
        label = np.where(probability > cal, 1, 0)
        return label

    def checkAccuracy(self):
        checkfile = os.path.join(outpathdir, 'label.csv')
        if not os.path.exists(checkfile):
            return
        checkdf = pd.read_csv(checkfile, index_col=0)
        for j in range(5, 105, 5):
            dict = checkdf[channel_list].to_dict('list')
            label_list = self.cal_Q_grd(dict, j / 100.0)
            checkdf['label'+str(j)] = label_list
        checkdf.to_csv(checkfile)

class MonitorConvection:
    """
    分类强对流监测
    Args:
        date_time: datetime格式时间
        channel_list: 通道名
    Returns:

    """
    def __init__(self, date_time, channel_list):

        self.date_time = date_time
        self.channel_list = channel_list

    def creat_M4_grd(self, lon, lat, data_array, name, gtime):
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
        meb.set_griddata_coords(grd, name="LABEL", level_list=[0], gtime=[gtime], dtime_list=[1], member_list=[name])
        return grd

    def get_fy4_file_path(self):
        """
        通过时间，获取FY4B的文件
        Args:
            d_date:
            cfg_dict:

        Returns:
        """
        filename = '{d_time:%Y}/{d_time:%Y%m%d}/FY4B-_AGRI--_N_*_1330E_L1-_FDI-_MULT_NOM_{d_time:%Y%m%d%H%M}00*_4000M_V0001.HDF'
        path = r"/mnt/satlake/FY4/FY4B/AGRI/L1/FDI/DISK/4000M"
        filepath = os.path.join(path, filename.format(d_time=self.date_time))
        files = glob.glob(filepath)
        try:
            return files[0]
        except:
            print('FY4B文件不存在')
            return None

    def MonitorConvection(self):

        try:
            fy4_file = self.get_fy4_file_path()
            print('读取FY4B通道数据: ' + self.date_time.strftime('%Y%m%d%H%M'))
            fy4b_obj = fy_4b_agri_l1()
            fy4b_obj.load_fy4b_data(fy4_file)
            lat, lon = np.arange(south_lat, north_lat + res, res), np.arange(west_lon, east_lon + res, res)
            fy4b_channel_dict = {
                'BT13': fy4b_obj.tb_13,
                'BTD14_13': fy4b_obj.tb_14 - fy4b_obj.tb_13,
                'BTD09_13': fy4b_obj.tb_09 - fy4b_obj.tb_13,
                'BTD09_10': fy4b_obj.tb_09 - fy4b_obj.tb_10,
                # 'lat': np.meshgrid(lon, lat)[1],
                # 'lon': np.meshgrid(lon, lat)[0],
            }
            print('完成通道数据字典准备')
            return fy4b_channel_dict
        except Exception as e:
            print(e)
            return None

    def MonitorRadar(self):

        try:
            radar_format = r'/mnt/radar_data/SWAN/MCR/%Y/%Y%m%d/Z_OTHE_RADAMCR_%Y%m%d%H%M00.bin.bz2'
            radar_files = datetime.strftime(self.date_time, radar_format)
            f = bz2.open(radar_files, 'rb')
            radar_grd = meb.decode_griddata_from_swan_d131_byteArray(f.read())
            grd_w = meb.grid(lon_grd, lat_grd)
            radar_grd_inter = meb.interp_gg_linear(radar_grd, grd_w, outer_value=-32)
            print('读取雷达数据: ' + self.date_time.strftime('%Y%m%d%H%M'))
            radar_grd_inter.name = 'radar'
            print('完成雷达数据准备')
            radar_array = radar_grd_inter.data
            radar_array[radar_array < 0] = -1
            return np.squeeze(radar_array)
        except Exception as e:
            print(e)
            return None

    def draw_rainlabel(self, LabelGrd, background):
        try:
            plt.figure(figsize=(16, 12), dpi=400)
            shp = Reader(shp_path)
            map = plt.axes(projection=ccrs.PlateCarree())
            plt.title(self.date_time.strftime("%Y%m%d%H%M"), loc='right', fontsize=20)
            plt.title('强降水', loc='left', fontsize=20, fontdict={'family': 'simhei'})
            map.set_xticks(np.arange(west_lon, east_lon + res, 10), crs=ccrs.PlateCarree())
            map.set_yticks(np.arange(south_lat, north_lat + res, 10), crs=ccrs.PlateCarree())
            map.set_extent([west_lon, east_lon, south_lat, north_lat], crs=ccrs.PlateCarree())
            # map.set_extent([112, 124, 28, 36], crs=ccrs.PlateCarree())
            lon_formatter = LongitudeFormatter(zero_direction_label='FALSE')
            lat_formatter = LatitudeFormatter()
            map.xaxis.set_major_formatter(lon_formatter)
            map.yaxis.set_major_formatter(lat_formatter)
            plt.tick_params(labelsize=18, axis="both", which="major", width=1, length=5, pad=5)
            vmin, vmax, cmap, extent = 200, 300, 'gist_yarg', (west_lon, east_lon, north_lat, south_lat)
            BackGroundShow = plt.imshow(background, cmap=cmap, extent=extent, vmin=vmin, vmax=vmax)
            plt.colorbar(BackGroundShow, aspect=45, pad=0.05, shrink=0.83, orientation='horizontal')
            lon = LabelGrd.lon.to_numpy()
            lat = LabelGrd.lat.to_numpy()
            LON, LAT = np.meshgrid(lon, lat)
            xr_data_array = np.squeeze(LabelGrd.data)

            kernel = np.ones((5, 5), np.uint8)
            xr_data_array = cv2.dilate(xr_data_array.astype(np.uint8), kernel, iterations=1)
            xr_data_array = cv2.erode(xr_data_array.astype(np.uint8), kernel, iterations=1)
            xr_data_array = cv2.GaussianBlur(xr_data_array, (3, 3), 0, 0)
            xr_data_array[xr_data_array < 1] = -1
            plt.contourf(LON, LAT, xr_data_array, colors=['#64B8FD'], levels=[1, 2])

            # 绘制散点图
            sta = meb.read_stadata_from_micaps3(r'D:\Wiztek_Python\cartopy_draw\plot\23091920.000')
            colors_list, levels = ['#64FDB6', '#9600B4'], [20, 100]
            cmap = colors.ListedColormap(colors_list)
            norm = colors.BoundaryNorm(levels, cmap.N - 1)
            plt.scatter(sta.lon.to_list(), sta.lat.to_list(), marker='.', s=5, c=sta.data0.to_list(), cmap=cmap,
                        norm=norm)

            map.add_geometries(shp.geometries(), crs=ccrs.PlateCarree(), edgecolor='red', linewidths=0.6,
                               facecolor='none', alpha=0.6)
            filepath = os.path.join(outpathdir, 'TP_' + self.date_time.strftime('%Y%m%d%H%M') + '.png')
            plt.savefig(fname=filepath, bbox_inches='tight')
            print('绘图成功：{}'.format(os.path.basename(filepath)))
        except Exception as e:
            print(e)

    def mainProcess(self, threshold):
        gtime = self.date_time.strftime('%Y-%m-%d-%H:%M')
        fy4b_channel_dict = self.MonitorConvection()
        drawNormClass = drawMembership(channel_list)
        # fy4b_channel_dict['radar'] = self.MonitorRadar()
        # fy4b_channel_dict_filter = {key: value for key, value in fy4b_channel_dict.items() if key in channel_list[:-1]}

        label = drawNormClass.cal_Q_grd(fy4b_channel_dict, threshold)
        RainLabelGrd = self.creat_M4_grd(lon_grd, lat_grd, label, 'rainlabel', gtime)
        self.draw_rainlabel(RainLabelGrd, fy4b_channel_dict.get('BT13'))

if __name__=='__main__':
    threshold = 0.9
    outpathdir = r'D:\Wiztek_Python\cartopy_draw\plot\test'
    shp_path = r"/data/datasource/Geoserver/Geoserver/全国边界线/chinaGJSJ/china_20220325.shp"
    channel_list = ['BT13', 'BTD09_10', 'BTD09_13', 'BTD14_13']
    drawNormClass = drawMembership(channel_list)
    # drawNormClass.draw_norm('强降水-FY4B卫星通道概率密度-隶属度分布', '概率密度', '隶属度')
    # TB_dict = {
    #     'BT13': 251.5700073,
    #     'BTD09_10':-5.970001221,
    #     'BTD09_13':-2.15000916,
    #     'BTD14_13':-2.850006104,
    # }
    # print('##' * 20)
    # probability, label = drawNormClass.cal_Q_scatter(TB_dict, 0.45)
    # print('概率系数Q:{:.2f}\t标签:{}'.format(probability, label))
    drawNormClass.checkAccuracy()

    # if len(sys.argv) > 1:
    #     start_time = datetime.strptime(sys.argv[1], '%Y%m%d%H%M')
    #     end_time = datetime.strptime(sys.argv[2], '%Y%m%d%H%M')
    # else:
    #     date_time = datetime.now() - timedelta(hours=12)
    #     end_time = date_time - timedelta(minutes=date_time.minute % 15)
    #     start_time = end_time - timedelta(minutes=30)
    #
    # while start_time <= end_time:
    #     MonitorConvectionObj = MonitorConvection(start_time, channel_list)
    #     MonitorConvectionObj.mainProcess(threshold)
    #     start_time += timedelta(minutes=15)