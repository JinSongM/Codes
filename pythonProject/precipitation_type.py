# -- coding: utf-8 --
# @Time : 2023/5/12 9:48
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : precipitation_type.py
# @Software: PyCharm
import sys
import os
from config import *
import meteva.base as meb
import numpy as np
from datetime import datetime, timedelta

def creat_M4_grd(lon_list, lat_list, data_array, name):
    """
    构建m4标准格式
    :param ID_LIST: 站号列表
    :param Lon_list: 经度列表
    :param Lat_list: 维度列表
    :param Data_list: 数据列表
    :return:
    """
    grid0 = meb.grid(lon_list, lat_list)
    data = data_array
    grd = meb.grid_data(grid0, data=data)
    meb.set_griddata_coords(grd, name=name, level_list=[0], gtime=["2023-01-01:08"],
                            dtime_list=[1], member_list=["typeTP_P"])
    return grd

class precipitation_typeP_C3E:
    def __init__(self, fst_time, fst_h, infile_path, station):
        self.fst_time = fst_time
        self.fst_h = fst_h
        self.infile_path = infile_path
        self.station = station

    def _load_ptype_data_m4(self, fst_time, fst_h):
        typeP_merge_data = []
        lon_lat_dict = dict()
        try:
            for i in range(51):
                infile = self.infile_path.format(rp_T=fst_time, ens=i, cst=fst_h)
                if not os.path.exists(infile):
                    continue
                temp_m4 = meb.read_griddata_from_micaps4(infile)
                temp_m4_array = temp_m4.data.reshape(temp_m4.data.shape[-2], temp_m4.data.shape[-1])
                typeP_merge_data.append(temp_m4_array.tolist())
                # lon, lat = temp_m4.lon.data, temp_m4.lat.data
                lon_lat_dict["lon_s"] = np.min(temp_m4.lon.data)
                lon_lat_dict["lon_e"] = np.max(temp_m4.lon.data)
                lon_lat_dict["lat_s"] = np.min(temp_m4.lat.data)
                lon_lat_dict["lat_e"] = np.max(temp_m4.lat.data)
                lon_lat_dict["lon_d"] = 0.25
                lon_lat_dict["lat_d"] = 0.25
            return np.array(typeP_merge_data), lon_lat_dict
        except Exception as e:
            print('解析文件有误')

    def _cal_ptype_probability(self):
        # 加载数据:加载C3E集合预报数据
        # 加载降水相态数据:集合预报数据
        temp_data, lon_lat_dict = self._load_ptype_data_m4(self.fst_time, self.fst_h)
        sta_station = meb.read_stadata_from_micaps3(self.station)
        try:
            if len(temp_data) == 0:
                return None, None
            # 2)合成五类数据 0无降水 1雨 2雨夹雪 3雪 4 冻雨
            mergedata = np.full_like(temp_data, -9999, dtype='int16')
            #        0无降水 => 0无降水
            mergedata = np.where((mergedata == -9999) & (temp_data > -1) & (temp_data <= 0.5), 0, mergedata)
            #        1雨 => 1雨
            mergedata = np.where((mergedata == -9999) & (temp_data > 0.5) & (temp_data <= 1.5), 1, mergedata)
            #        7雨夹雪 => 2雨夹雪
            mergedata = np.where((mergedata == -9999) & (temp_data > 6.5) & (temp_data <= 7.5), 2, mergedata)
            #        5干雪和6湿雪8冰粒 => 3雪
            mergedata = np.where((mergedata == -9999) & (temp_data > 4.5) & (temp_data <= 6.5), 3, mergedata)
            mergedata = np.where((mergedata == -9999) & (temp_data > 7.5) & (temp_data <= 8.5), 3, mergedata)
            #        3冻雨 => 4冻雨
            mergedata = np.where((mergedata == -9999) & (temp_data > 2.5) & (temp_data <= 3.5), 4, mergedata)

            # 3)计算五类数据的概率：计算每一个格点上51个成员0~4五类数据的概率
            prob0_array = np.mean(np.where((mergedata == 0), 1, 0), axis=0)
            prob1_array = np.mean(np.where((mergedata == 1), 1, 0), axis=0)
            prob2_array = np.mean(np.where((mergedata == 2), 1, 0), axis=0)
            prob3_array = np.mean(np.where((mergedata == 3), 1, 0), axis=0)
            prob4_array = np.mean(np.where((mergedata == 4), 1, 0), axis=0)

            lon_list = [lon_lat_dict["lon_s"], lon_lat_dict["lon_e"], lon_lat_dict["lon_d"]]
            lat_list = [lon_lat_dict["lat_s"], lon_lat_dict["lat_e"], lon_lat_dict["lat_d"]]
            prob0 = creat_M4_grd(lon_list, lat_list, prob0_array, 'C3E')
            prob1 = creat_M4_grd(lon_list, lat_list, prob1_array, 'C3E')
            prob2 = creat_M4_grd(lon_list, lat_list, prob2_array, 'C3E')
            prob3 = creat_M4_grd(lon_list, lat_list, prob3_array, 'C3E')
            prob4 = creat_M4_grd(lon_list, lat_list, prob4_array, 'C3E')
            # 将多种预报合并到一个网格数据里
            pt1_grid0 = meb.grid(lon_list, lat_list, level_list=[0,1,2,3,4])
            pt1 = meb.grid_data(pt1_grid0, np.array([prob0_array,prob1_array,prob2_array,prob3_array,prob4_array]))

            prob0_m3 = meb.interp_gs_linear(prob0, sta_station)
            prob1_m3 = meb.interp_gs_linear(prob1, sta_station)
            prob2_m3 = meb.interp_gs_linear(prob2, sta_station)
            prob3_m3 = meb.interp_gs_linear(prob3, sta_station)
            prob4_m3 = meb.interp_gs_linear(prob4, sta_station)
            sta_combine = meb.combine_on_all_coords(prob0_m3, prob1_m3)
            sta_combine = meb.combine_on_all_coords(sta_combine, prob2_m3)
            sta_combine = meb.combine_on_all_coords(sta_combine, prob3_m3)
            sta_combine = meb.combine_on_all_coords(sta_combine, prob4_m3)

            meb.set_stadata_names(sta_combine, ['prob0', 'prob1', 'prob2', 'prob3', 'prob4'])
            return sta_combine, pt1
        except Exception as ex:
            print("计算C3E降水相态概率报错", ex)

class precipitation_typeP_C1D:
    def __init__(self, fst_time, fst_h, infile_path, station):
        self.fst_time = fst_time
        self.fst_h = fst_h
        self.infile_path = infile_path
        self.station = station

    def _load_ptype_data_m4(self, fst_time, fst_h):
        lon_lat_dict = dict()
        infile = self.infile_path.format(rp_T=fst_time, cst=fst_h)
        try:
            if not os.path.exists(infile):
                print('解析文件不存在')
                return
            temp_m4 = meb.read_griddata_from_micaps4(infile)
            sta_station = meb.read_stadata_from_micaps3(self.station)
            temp_m4_array = temp_m4.data.reshape(temp_m4.data.shape[-2], temp_m4.data.shape[-1])
            typeTP_m3 = meb.interp_gs_nearest(temp_m4, sta_station)
            # lon, lat = temp_m4.lon.data, temp_m4.lat.data
            lon_lat_dict["lon_s"] = np.min(temp_m4.lon.data)
            lon_lat_dict["lon_e"] = np.max(temp_m4.lon.data)
            lon_lat_dict["lat_s"] = np.min(temp_m4.lat.data)
            lon_lat_dict["lat_e"] = np.max(temp_m4.lat.data)
            lon_lat_dict["lon_d"] = 0.25
            lon_lat_dict["lat_d"] = 0.25
            return temp_m4_array, lon_lat_dict, typeTP_m3, sta_station
        except Exception as e:
            print(e)

    def _cal_ptype_probability(self):
        # 加载数据:加载C1D集合预报数据
        # 加载降水相态数据:集合预报数据
        sta_combine = None
        temp_data, lon_lat_dict, typeTP_m3, sta_station = self._load_ptype_data_m4(self.fst_time, self.fst_h)
        try:
            if temp_data is None:
                return None, None, None
            # 2)合成五类数据 0无降水 1雨 2雨夹雪 3雪 4 冻雨
            mergedata = np.full_like(temp_data, -9999, dtype='int16')
            #        0无降水 => 0无降水
            mergedata = np.where((mergedata == -9999) & (temp_data > -1) & (temp_data <= 0.5), 0, mergedata)
            #        1雨 => 1雨
            mergedata = np.where((mergedata == -9999) & (temp_data > 0.5) & (temp_data <= 1.5), 1, mergedata)
            #        7雨夹雪 => 2雨夹雪
            mergedata = np.where((mergedata == -9999) & (temp_data > 6.5) & (temp_data <= 7.5), 2, mergedata)
            #        5干雪和6湿雪8冰粒 => 3雪
            mergedata = np.where((mergedata == -9999) & (temp_data > 4.5) & (temp_data <= 6.5), 3, mergedata)
            mergedata = np.where((mergedata == -9999) & (temp_data > 7.5) & (temp_data <= 8.5), 3, mergedata)
            #        3冻雨 => 4冻雨
            mergedata = np.where((mergedata == -9999) & (temp_data > 2.5) & (temp_data <= 3.5), 4, mergedata)

            prob_dict = {
                'typeTP_prob0' : np.full_like(temp_data, -9999.0),
                'typeTP_prob1' : np.full_like(temp_data, -9999.0),
                'typeTP_prob2' : np.full_like(temp_data, -9999.0),
                'typeTP_prob3' : np.full_like(temp_data, -9999.0),
                'typeTP_prob4' : np.full_like(temp_data, -9999.0)
            }
            for i in range(2, temp_data.shape[0]-2):
                for j in range(2, temp_data.shape[1] - 2):
                    square = mergedata[i-2:i+3, j-2:j+3]
                    # 3)计算五类数据的概率：计算每一个格点上51个成员0~4五类数据的概率
                    # for type_num in range(5):
                    for index, key in enumerate(prob_dict):
                        cell_value = np.mean(np.where((square == index), 1, 0))
                        prob_dict.get(key)[i, j] = cell_value

            lon_list = [lon_lat_dict["lon_s"], lon_lat_dict["lon_e"], lon_lat_dict["lon_d"]]
            lat_list = [lon_lat_dict["lat_s"], lon_lat_dict["lat_e"], lon_lat_dict["lat_d"]]
            pt1_list = []
            for index, key in enumerate(prob_dict):
                prob_m4 = creat_M4_grd(lon_list, lat_list, prob_dict.get(key), 'C1D')
                prob_m3 = meb.interp_gs_linear(prob_m4, sta_station)
                sta_combine = meb.combine_on_all_coords(sta_combine, prob_m3)
                pt1_list.append(prob_dict.get(key))
                # prob_m3_dict[key] = prob_m3
            meb.set_stadata_names(sta_combine, ['prob0', 'prob1', 'prob2', 'prob3', 'prob4'])
            # 将多种预报合并到一个网格数据里
            pt2_grid0 = meb.grid(lon_list, lat_list, level_list=[0,1,2,3,4])
            pt2 = meb.grid_data(pt2_grid0, np.array(pt1_list))
            return sta_combine, typeTP_m3, pt2
        except Exception as ex:
            print("计算C1D降水相态概率报错", ex)

def save_Ppt(model, fst_time, fst_h,  input_c3e, input_c1d, output_c3e, output_c1d, c3e_pt1, c1d_pt2, station_path):
    if model == 'C3E':
        Ppt_c3e = precipitation_typeP_C3E(fst_time, fst_h, input_c3e, station_path)
        prob_m3_c3e, pt1_c3e = Ppt_c3e._cal_ptype_probability()
        if prob_m3_c3e is None:
            return
        c3e_file_Ppt1 = output_c3e.format(rp_T=fst_time, cst=fst_h)
        c3e_file_pt1 = c3e_pt1.format(rp_T=fst_time, cst=fst_h)
        if not os.path.exists(os.path.dirname(c3e_file_Ppt1)):
            os.makedirs(os.path.dirname(c3e_file_Ppt1))
        prob_m3_c3e.to_csv(c3e_file_Ppt1)
        meb.write_griddata_to_nc(pt1_c3e, c3e_file_pt1)
        print('成功输出至' + c3e_file_Ppt1)
        print('成功输出至' + c3e_file_pt1)
    elif model == 'C1D':
        c1d_file_Ppt2 = output_c1d.format(rp_T=fst_time, cst=fst_h)
        c1d_file_pt2 = c1d_pt2.format(rp_T=fst_time, cst=fst_h)
        c1d_file_Ppt2_sta = c1d_file_Ppt2.replace('PRTY', 'Ppt2_sta')
        c1d_file_Ppt2_sta = c1d_file_Ppt2_sta.replace('csv', 'm3')
        Ppt_c1d = precipitation_typeP_C1D(fst_time, fst_h, input_c1d, station_path)
        prob_m3_c1d, typeTP_m3, pt2_C1D = Ppt_c1d._cal_ptype_probability()
        if not os.path.exists(os.path.dirname(c1d_file_Ppt2)):
            os.makedirs(os.path.dirname(c1d_file_Ppt2))
        prob_m3_c1d.to_csv(c1d_file_Ppt2)
        meb.write_stadata_to_micaps3(typeTP_m3, c1d_file_Ppt2_sta, creat_dir = True, show = True)
        meb.write_griddata_to_nc(pt2_C1D, c1d_file_pt2)
        print('成功输出至' + c1d_file_Ppt2)
        print('成功输出至' + c1d_file_pt2)
    else:
        print('error')

def precipitation_typeP_OBS(infile, outfile):
    if os.path.exists(infile):
        sta = meb.read_stadata_from_micaps3(infile)
        sta["data0"].loc[(sta["data0"] < 50)] = 0
        sta["data0"].loc[(sta["data0"] >= 50) & (sta["data0"] <= 55)] = 1
        sta["data0"].loc[(sta["data0"] >= 58) & (sta["data0"] <= 65)] = 1
        sta["data0"].loc[(sta["data0"] >= 80) & (sta["data0"] <= 82)] = 1

        sta["data0"].loc[(sta["data0"] >= 68) & (sta["data0"] <= 69)] = 2
        sta["data0"].loc[(sta["data0"] >= 83) & (sta["data0"] <= 84)] = 2

        sta["data0"].loc[(sta["data0"] >= 70) & (sta["data0"] <= 76)] = 3
        sta["data0"].loc[sta["data0"] == 78] = 3
        sta["data0"].loc[(sta["data0"] >= 85) & (sta["data0"] <= 86)] = 3

        sta["data0"].loc[(sta["data0"] >= 56) & (sta["data0"] <= 57)] = 4
        sta["data0"].loc[sta["data0"] == 77] = 4
        sta["data0"].loc[sta["data0"] == 79] = 4
        sta["data0"].loc[(sta["data0"] >= 66) & (sta["data0"] <= 67)] = 4
        sta = sta.drop(sta[(sta["data0"] > 4) & (sta["data0"] < 508)].index)
        sta["data0"].loc[(sta["data0"] >= 508)] = 9
        # print(sta)
        if not os.path.exists(os.path.dirname(outfile)):
            os.makedirs(os.path.dirname(outfile))
        meb.write_stadata_to_micaps3(sta, outfile)
        print('成功输出至' + outfile)
    else:
        print('文件不存在')

def ptype(startT, endT, fst_h, model):
    begin_fst_T = startT
    while begin_fst_T <= endT:
        if model == 'OBS':
            infile = land_obs.format(rp_T=begin_fst_T)
            outfile = land_obs6.format(rp_T=begin_fst_T)
            try:
                precipitation_typeP_OBS(infile, outfile)
                begin_fst_T += timedelta(hours=3)
            except Exception as e:
                begin_fst_T += timedelta(hours=3)
                print(e)
                continue
        else:
            for cst in fst_h:
                try:
                    save_Ppt(model, begin_fst_T, cst,  infile_path_c3e, infile_path_c1d, c3e_Ppt1, c1d_Ppt2, c3e_pt1, c1d_pt2, station_path)
                except Exception as e:
                    print(e)
                    continue
            begin_fst_T += timedelta(hours=12)

if __name__ == '__main__':
    #参数：OBS 2023051000-2023051100
    if len(sys.argv) > 2:
        for time_list in sys.argv[2:]:
            startT, endT = [datetime.strptime(i, '%Y%m%d%H') for i in time_list.split('-')]
            print(startT, endT)
            ptype(startT, endT, fst_h, sys.argv[1])
    else:
        startT, endT = datetime.now().replace(hour=0, minute=0) - timedelta(days=1), datetime.now().replace(hour=12, minute=0)
        print(startT, endT)
        ptype(startT, endT, fst_h, sys.argv[1])
