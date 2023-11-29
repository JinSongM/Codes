# -- coding: utf-8 --
# @Time : 2023/11/1 13:56
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : stats_norm_hail.py
# @Software: PyCharm
import math
import os, glob
import sys, cv2

import sklearn.neural_network
import xgboost as xgb
import meteva.base as meb
import netCDF4 as nc
from sklearn.linear_model import SGDClassifier
from scipy.stats import norm
import numpy as np
import pandas as pd
import _pickle as cPickle
from matplotlib import colors
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from cartopy.io.shapereader import Reader
import cartopy.crs as ccrs
from sklearn.model_selection import GridSearchCV
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter


plt.rcParams.update({
    'font.sans-serif': 'Times New Roman',
    'font.size': 22
    })
plt.rcParams['axes.unicode_minus']=False


south_lat, north_lat, east_lon, west_lon, res = 10, 60, 140, 70, 0.04
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
        # 冰雹数据
        self.rain0_file = r'/data/PRODUCT/rain_channel_sta/0/merge3/merge_rain0.csv'
        self.rain1_file = r'/data/PRODUCT/rain_channel_sta/20/merge3/merge_rain20.csv'
        self.rain2_file = r'/data/PRODUCT/rain_channel_sta/50/merge3/merge_rain50.csv'
        self.rain3_file = r'/data/PRODUCT/rain_channel_sta/80/merge3/merge_rain80.csv'
        try:
            self.hail_df0 = pd.read_csv(self.rain0_file)
            self.hail_df1 = pd.read_csv(self.rain1_file)
            self.hail_df2 = pd.read_csv(self.rain2_file)
            self.hail_df3 = pd.read_csv(self.rain3_file)
            self.hail0_df = self.hail_df0.dropna(axis=0, how='any')
            self.hail1_df = pd.concat([self.hail_df1, self.hail_df2, self.hail_df3], axis=0)
            self.hail1_df = self.hail1_df.dropna(axis=0, how='any')

            # # 标签检验
            # labelDf0 = self.hail0_df[channel_list].copy().sample(10000)
            # labelDf0['label'] = 0
            # labelDf1 = self.hail1_df[channel_list].copy().sample(10000)
            # labelDf1['label'] = 1
            # merge_df = pd.concat([labelDf0, labelDf1], axis=0)
            # filepath = os.path.join(outpathdir, 'label.csv')
            # merge_df.to_csv(filepath)

        except Exception as e:
            print(e)

class save_use_model:

    def save_model_to_file(self, model, file_path):
        with open(file_path, 'wb') as f:
            cPickle.dump(model, f)

    def use_model(self, file_path):
        with open(file_path, 'rb') as f:
            rf = cPickle.load(f)
        return rf

class xgmodel(loadData):
    """
    构建机器学习模型
    params:
        channel:
        pic_name:
        ytitle:
    return:
        概率密度图
    """

    def __init__(self, channel_list):
        super().__init__()
        self.channel_list = channel_list

    def create_xgboost(self):
        xgboost_obj = save_use_model()
        filepath = os.path.join(outpathdir, 'xgboost.pkl')

        if not os.path.exists(filepath):
            xgboost_model = xgboost_obj.use_model(filepath)
        else:
            df0, df1 = self.hail0_df.copy(), self.hail1_df.copy()
            df0['label'], df1['label'] = 0, 1
            locname = channel_list + ['label']
            train_df0, train_df1 = df0[locname], df1[locname]
            test_df0, test_df1 = train_df0.sample(frac=0.3), train_df1.sample(frac=0.3)

            train_data0 = (train_df0.append(test_df0)).drop_duplicates(keep=False)
            train_data1 = (train_df1.append(test_df1)).drop_duplicates(keep=False)
            xtrain = pd.concat([train_data0[locname[:-1]], train_data1[locname[:-1]]], axis=0)
            ytrain = pd.concat([train_data0[locname[-1:]], train_data1[locname[-1:]]], axis=0)
            normlize_xtrain = xtrain.copy()
            for i in channel_list:
                normlize_xtrain[i] = (normlize_xtrain[i]-np.min(xtrain[i])) / (np.max(xtrain[i])-np.min(xtrain[i]))
            param_grid = {
                'learning_rate': [0.05],
                'max_depth': [4,6,8],
                'min_child_weight': [3,5,7],
                'subsample': [0.6, 0.7, 0.8],
                'colsample_bytree': [0.8]
            }
            from sklearn.ensemble import RandomForestClassifier
            other_params = {'bootstrap': True, 'max_features': 'sqrt', 'max_depth': 14,
                            'min_samples_split': 2, 'n_estimators': 100, 'min_samples_leaf': 1}
            model = RandomForestClassifier(**other_params)
            # model = xgb.XGBClassifier()
            # grid_search = GridSearchCV(model, param_grid, cv=2, scoring='neg_mean_squared_error')
            model.fit(normlize_xtrain, ytrain)
            print(model)

            # xtest = pd.concat([test_df0, test_df1], axis=0)
            # xpredict = xtest.copy()
            # for i in locname[:-1]:
            #     xpredict[i] = (xpredict[i]-np.mean(xpredict[i])) / np.std(xpredict[i])
            # testlabel = grid_search.predict(xpredict[locname[:-1]])
            # xpredict['predict'] = testlabel
            # xpredict.to_csv('./plot/xgboost/test.csv')

            xgboost_obj.save_model_to_file(model, filepath)
            xgboost_model = model

        return xgboost_model

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
            lon, lat = np.arange(west_lon, east_lon + res, res), np.arange(south_lat, north_lat + res, res)
            lon_grd, lat_grd = np.meshgrid(lon, lat[::-1])
            fy4b_channel_dict = {
                'BT13': fy4b_obj.tb_13,
                'BTD14_13': fy4b_obj.tb_14 - fy4b_obj.tb_13,
                'BTD09_13': fy4b_obj.tb_09 - fy4b_obj.tb_13,
                'BTD09_10': fy4b_obj.tb_09 - fy4b_obj.tb_10,
            }
            fy4b_channel_dict_info = {
                'BT13': fy4b_obj.tb_13.flatten(),
                'BTD09_10': fy4b_obj.tb_09.flatten() - fy4b_obj.tb_10.flatten(),
                'BTD09_13': fy4b_obj.tb_09.flatten() - fy4b_obj.tb_13.flatten(),
                'BTD14_13': fy4b_obj.tb_14.flatten() - fy4b_obj.tb_13.flatten(),
            }
            normlize_info = fy4b_channel_dict_info.copy()
            for i in channel_list:
                normlize_info[i] = (normlize_info[i] - np.mean(normlize_info[i])) / np.std(normlize_info[i])

            fy4b_channel_df = pd.DataFrame(normlize_info)
            print('完成通道数据字典准备')
            return fy4b_channel_dict, fy4b_channel_df
        except Exception as e:
            print(e)
            return None

    def draw_haillabel(self, LabelGrd, background):
        try:
            plt.figure(figsize=(16, 12), dpi=400)
            shp = Reader(shp_path)
            map = plt.axes(projection=ccrs.PlateCarree())
            plt.title(self.date_time.strftime("%Y%m%d%H%M"), loc='right', fontsize=20)
            plt.title('冰雹', loc='left', fontsize=20, fontdict={'family': 'simhei'})
            map.set_xticks(np.arange(west_lon, east_lon + res, 10), crs=ccrs.PlateCarree())
            map.set_yticks(np.arange(south_lat, north_lat + res, 10), crs=ccrs.PlateCarree())
            map.set_extent([west_lon, east_lon, south_lat, north_lat], crs=ccrs.PlateCarree())
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

            kernel = np.ones((7, 7), np.uint8)
            # xr_data_array = cv2.erode(xr_data_array.astype(np.uint8), kernel, iterations=1)
            # xr_data_array = cv2.dilate(xr_data_array, kernel, iterations=1)
            xr_data_array = cv2.GaussianBlur(xr_data_array.astype(np.uint8), (5, 5), 0, 0)
            xr_data_array = np.ma.masked_where(xr_data_array != 1, xr_data_array)
            plt.pcolormesh(LON, LAT, xr_data_array, cmap=colors.ListedColormap(['#64B8FD']))

            map.add_geometries(shp.geometries(), crs=ccrs.PlateCarree(), edgecolor='red', linewidths=0.6,
                               facecolor='none', alpha=0.6)
            filepath = os.path.join(outpathdir, 'TP_' + self.date_time.strftime('%Y%m%d%H%M') + '.png')
            plt.savefig(fname=filepath, bbox_inches='tight')
            print('绘图成功：{}'.format(os.path.basename(filepath)))
        except Exception as e:
            print(e)

    def mainProcess(self):
        gtime = self.date_time.strftime('%Y-%m-%d-%H:%M')
        fy4b_channel_dict, fy4b_channel_df = self.MonitorConvection()
        drawNormClass = xgmodel(channel_list)
        model = drawNormClass.create_xgboost()
        label_df = model.predict(fy4b_channel_df)
        label = label_df.reshape(1251, 1751)
        lon_grd, lat_grd = [west_lon, east_lon, res], [south_lat, north_lat, res]
        hailLabelGrd = self.creat_M4_grd(lon_grd, lat_grd, label, 'haillabel', gtime)
        self.draw_haillabel(hailLabelGrd, fy4b_channel_dict.get('BT13'))

if __name__ == '__main__':
    outpathdir = './plot/xgboost'
    shp_path = r"/data/datasource/Geoserver/Geoserver/全国边界线/chinaGJSJ/china_20220325.shp"
    channel_list = ['BT13', 'BTD09_10', 'BTD09_13', 'BTD14_13']
    # drawNormClass = xgmodel(channel_list)
    # drawNormClass.create_xgboost()

    if len(sys.argv) > 1:
        start_time = datetime.strptime(sys.argv[1], '%Y%m%d%H%M')
        end_time = datetime.strptime(sys.argv[2], '%Y%m%d%H%M')
    else:
        date_time = datetime.now() - timedelta(hours=12)
        end_time = date_time - timedelta(minutes=date_time.minute % 15)
        start_time = end_time - timedelta(minutes=30)

    while start_time <= end_time:
        MonitorConvectionObj = MonitorConvection(start_time, channel_list)
        MonitorConvectionObj.mainProcess()
        start_time += timedelta(minutes=15)