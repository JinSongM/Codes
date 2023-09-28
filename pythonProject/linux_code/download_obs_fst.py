#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author    : xianyunhao
@Contact   : yhaoxian_nuist@163.com
@File      : download_obs_fst.py
@Time      : 2023/6/14 23:08
@Desc      :
"""
from datetime import datetime, timedelta
import multiprocessing
import os
import sys
import traceback

import pygrib
import numpy as np
from meteva.base.io import CMADaasAccess
import meteva.base as meb

# c3e源数据路径
src_c3e_1 = "/CMADAAS/DATA/NAFP/ECMF/C3E/{d_time:%Y}/{d_time:%Y%m%d}/ECMFENS_PRTY_1_{d_time:%Y%m%d%H}_ASI_3_4.grib2"
src_c3e_2 = "/CMADAAS/DATA/NAFP/ECMF/C3E/{d_time:%Y}/{d_time:%Y%m%d}/ECMFENS_PRTY_1_{d_time:%Y%m%d%H}_ASI_4_4.grib2"
# c3e解析后数据路径
dst_c3e = "/share/DATASOURCE/PTYPE/ORI/ECMWF/ECENS/{d_time:%Y%m%d%H}/ptype/{d_time:%Y%m%d%H}.{fst_h:03d}.nc"

# c1d源数据路径
src_c1d = "/CMADAAS/DATA/NAFP/ECMF/C1D/{d_time:%Y}/{d_time:%Y%m%d}/ECMFC1D_PRTY_1_{d_time:%Y%m%d%H}_GLB_1_2.grib2"
# c1d解析后数据路径
dst_c1d = "/share/DATASOURCE/PTYPE/ORI/ECMWF/ECMWF_C1D/{d_time:%Y%m%d%H}/ptype/{d_time:%Y%m%d%H}.{fst_h:03d}.nc"

# 天擎  SURF_CHN_MUL_HOR  WEP_Now 天气现象数据
land_obs = "/share/DATASOURCE/PTYPE/ORI/OBS/STA/{d_time:%Y%m%d}/ptype/{d_time:%Y%m%d%H}.000.m3"

land_obs6 = r'/share/DATASOURCE/PTYPE/CVT/OBS/STA/{d_time:%Y%m%d}/ptype/{d_time:%Y%m%d%H}.000.m3'

c3e_Ppt1 = r'/share/DATASOURCE/PTYPE/CVT/FST/C3E/{d_time:%Y%m%d}/ptype/{d_time:%Y%m%d%H}.{fst:03d}.csv'
c3e_pt1 = r'/share/DATASOURCE/PTYPE/CVT/FST/C3E/{d_time:%Y%m%d}/ptype/{d_time:%Y%m%d%H}.{fst:03d}.nc'

c1d_Ppt2 = r'/share/DATASOURCE/PTYPE/CVT/FST/C1D/{d_time:%Y%m%d}/ptype/{d_time:%Y%m%d%H}.{fst:03d}.csv'
c1d_pt2 = r'/share/DATASOURCE/PTYPE/CVT/FST/C1D/{d_time:%Y%m%d}/ptype/{d_time:%Y%m%d%H}.{fst:03d}.nc'
c1d_Ppt2_sta = r'/share/DATASOURCE/PTYPE/CVT/FST/C1D/{d_time:%Y%m%d}/ptype/{d_time:%Y%m%d%H}.{fst:03d}.m3'

typePP_out = r'/share/DATASOURCE/PTYPE/STATIS_HIS/{d_time:%Y%m}/{d_time:%Y%m}_{HR:02d}_{fst:03d}_{label}.csv'
NAFP_png = r'/share/DATASOURCE/PTYPE/IMAGES/{d_time:%Y%m%d}/{model}_{d_time:%Y%m%d%H}_{d_time:03d}_{model_type}.png'

station_file = './xz_all_11277.m3'

# 天擎配置
dataCode = 'SURF_CHN_MUL_HOR'
element = 'WEP_Now'
userID = 'NMC_DONGQUAN3'
pwd = 'Dongquan@401'
cmadaas_url = r'http://10.40.17.54/music-ws/api?'

station = meb.read_stadata_from_micaps3(station_file)


def c1d_convert_ptype(value, lons, lats, fst_time, fst_h):
    """

    Args:
        value:
        lons:
        lats:
        fst_time:
        fst_h:

    Returns:

    """
    sta_combine = None
    lon_lat_dict = dict()
    lon_lat_dict["lon_s"], lon_lat_dict["lon_e"], lon_lat_dict["lon_d"] = lons[0], lons[-1], lons[1] - lons[0]
    lon_lat_dict["lat_s"], lon_lat_dict["lat_e"], lon_lat_dict["lat_d"] = lats[0], lats[-1], lats[1] - lats[0]
    try:
        if len(value) == 0:
            return None, None

        tmp_value = value.reshape(value.shape[-2], value.shape[-1])

        # 2)合成五类数据 0无降水 1雨 2雨夹雪 3雪 4 冻雨
        mergedata = np.full_like(tmp_value, -9999, dtype='int16')
        #        0无降水 => 0无降水
        mergedata = np.where((mergedata == -9999) & (tmp_value > -1) & (tmp_value <= 0.5), 0, mergedata)
        #        1雨 => 1雨
        mergedata = np.where((mergedata == -9999) & (tmp_value > 0.5) & (tmp_value <= 1.5), 1, mergedata)
        #        7雨夹雪 => 2雨夹雪
        mergedata = np.where((mergedata == -9999) & (tmp_value > 6.5) & (tmp_value <= 7.5), 2, mergedata)
        #        5干雪和6湿雪8冰粒 => 3雪
        mergedata = np.where((mergedata == -9999) & (tmp_value > 4.5) & (tmp_value <= 6.5), 3, mergedata)
        mergedata = np.where((mergedata == -9999) & (tmp_value > 7.5) & (tmp_value <= 8.5), 3, mergedata)
        #        3冻雨 => 4冻雨
        mergedata = np.where((mergedata == -9999) & (tmp_value > 2.5) & (tmp_value <= 3.5), 4, mergedata)

        prob_dict = {
            'typeTP_prob0': np.full_like(tmp_value, -9999.0),
            'typeTP_prob1': np.full_like(tmp_value, -9999.0),
            'typeTP_prob2': np.full_like(tmp_value, -9999.0),
            'typeTP_prob3': np.full_like(tmp_value, -9999.0),
            'typeTP_prob4': np.full_like(tmp_value, -9999.0)
        }
        for i in range(2, tmp_value.shape[0] - 2):
            for j in range(2, tmp_value.shape[1] - 2):
                square = mergedata[i - 2:i + 3, j - 2:j + 3]
                # 3)计算五类数据的概率：计算每一个格点上51个成员0~4五类数据的概率
                # for type_num in range(5):
                for index, key in enumerate(prob_dict):
                    cell_value = np.mean(np.where((square == index), 1, 0))
                    prob_dict.get(key)[i, j] = cell_value

        lon_list = [lon_lat_dict["lon_s"], lon_lat_dict["lon_e"], lon_lat_dict["lon_d"]]
        lat_list = [lon_lat_dict["lat_s"], lon_lat_dict["lat_e"], lon_lat_dict["lat_d"]]
        pt1_list = []
        for index, key in enumerate(prob_dict):
            prob_m4 = creat_m4_grd(lon_list, lat_list, prob_dict.get(key), 'C1D', fst_time, fst_h)
            prob_m3 = meb.interp_gs_linear(prob_m4, station)
            sta_combine = meb.combine_on_all_coords(sta_combine, prob_m3)
            pt1_list.append(prob_dict.get(key))
            # prob_m3_dict[key] = prob_m3
        meb.set_stadata_names(sta_combine, ['prob0', 'prob1', 'prob2', 'prob3', 'prob4'])
        # 将多种预报合并到一个网格数据里
        pt2_grid0 = meb.grid(lon_list, lat_list, level_list=[0, 1, 2, 3, 4])
        pt2 = meb.grid_data(pt2_grid0, np.array(pt1_list))
        pt2.name = "ptype"
        return sta_combine, pt2
    except Exception as ex:
        print(ex.__str__)


def save_c1d_nc(shortname, fst_h, value, lons, lats, d_time: datetime):
    """

    Args:
        shortname:
        fst_h:
        value:
        lons:
        lats:
        d_time:

    Returns:

    """
    grid_w = meb.grid([70., 140., 0.125], [10., 60., 0.125])
    outer_value = None
    fst_time = d_time + timedelta(hours=8)
    dst_filepath = dst_c1d.format(d_time=fst_time, fst_h=fst_h)
    if not os.path.exists(os.path.dirname(dst_filepath)):
        os.makedirs(os.path.dirname(dst_filepath))
    grid0 = meb.grid([lons[0], lons[-1], lons[1] - lons[0]], [lats[0], lats[-1], lats[1] - lats[0]],
                     gtime=[fst_time.strftime("%Y%m%d%H")], dtime_list=[fst_h], level_list=[0],
                     member_list=["ECMWF_C1D"])
    grb = meb.grid_data(grid0, value)
    inter_grb = meb.interp_gg_linear(grb, grid_w, outer_value=outer_value)
    inter_grb.name = shortname
    meb.write_griddata_to_nc(inter_grb, dst_filepath)
    print("保存文件: {} 成功".format(dst_filepath))

    sta_combine, pt2 = c1d_convert_ptype(inter_grb.values, inter_grb.lon.values, inter_grb.lat.values, fst_time, fst_h)
    type_tp_m3 = meb.interp_gs_nearest(inter_grb, station)

    c1d_file_ptype_1 = c1d_Ppt2.format(d_time=fst_time, fst=fst_h)
    c1d_file_ptype_2 = c1d_pt2.format(d_time=fst_time, fst=fst_h)
    c1d_file_ptype_3 = c1d_Ppt2_sta.format(d_time=fst_time, fst=fst_h)

    if not os.path.exists(os.path.dirname(c1d_file_ptype_1)):
        os.makedirs(os.path.dirname(c1d_file_ptype_1))
    sta_combine.to_csv(c1d_file_ptype_1)
    meb.write_stadata_to_micaps3(type_tp_m3, c1d_file_ptype_3, creat_dir=True, show=True)
    meb.write_griddata_to_nc(pt2, c1d_file_ptype_2)
    print('成功输出至' + c1d_file_ptype_1 + " | " + c1d_file_ptype_2 + " | " + c1d_file_ptype_3)


def deal_c1d_data(d_time: datetime):
    """

    Args:
        d_time:

    Returns:

    """
    src_path = src_c1d.format(d_time=d_time)
    dst_filepath = dst_c1d.format(d_time=d_time + timedelta(hours=8), fst_h=240)
    if os.path.exists(dst_filepath):
        return
    # src_path = r"C:\Users\xianyunhao\Desktop\ECMFC1D_PRTY_1_2023010100_GLB_1_2.grib2"
    if os.path.exists(src_path):
        try:
            with pygrib.open(src_path) as pgs:
                for pg in pgs:
                    shortname = pg["shortName"]
                    fst_h = pg["forecastTime"]
                    value = pg["values"][::-1, :]
                    lat_s = pg["latitudeOfLastGridPointInDegrees"]
                    lat_e = pg["latitudeOfFirstGridPointInDegrees"]
                    lat_d = pg["iDirectionIncrementInDegrees"]
                    lon_s = pg["longitudeOfFirstGridPointInDegrees"]
                    lon_e = pg["longitudeOfLastGridPointInDegrees"]
                    lon_d = pg["jDirectionIncrementInDegrees"]
                    lats = np.arange(lat_s, lat_e + 0.1 * lat_d, lat_d)
                    lons = np.arange(lon_s, lon_e + 0.1 * lon_d, lon_d)
                    _arr = np.ndarray((1, 1, 1, 1, len(lats), len(lons)), dtype=int)
                    _arr[0, 0, 0, 0, :, :] = value
                    save_c1d_nc(shortname, fst_h, _arr, lons, lats, d_time)
        except Exception as ex:
            print(ex.__str__())


def creat_m4_grd(lon_list, lat_list, data_array, name, fst_time, fst_h):
    """

    Args:
        lon_list:
        lat_list:
        data_array:
        name:
        fst_time:
        fst_h:

    Returns:

    """
    grid0 = meb.grid(lon_list, lat_list)
    data = data_array
    grd = meb.grid_data(grid0, data=data)
    meb.set_griddata_coords(grd, name=name, level_list=[0], gtime=[fst_time], dtime_list=[fst_h], member_list=[0])
    return grd


def c3e_convert_ptype(value, lons, lats, fst_time: datetime, fst_h):
    """

    Args:
        value:
        lons:
        lats:
        fst_time:
        fst_h:

    Returns:

    """
    lon_lat_dict = dict()
    lon_lat_dict["lon_s"], lon_lat_dict["lon_e"], lon_lat_dict["lon_d"] = lons[0], lons[-1], lons[1] - lons[0]
    lon_lat_dict["lat_s"], lon_lat_dict["lat_e"], lon_lat_dict["lat_d"] = lats[0], lats[-1], lats[1] - lats[0]
    try:
        if len(value) == 0:
            return None, None

        tmp_value = value.reshape(value.shape[0], value.shape[-2], value.shape[-1])

        # 2)合成五类数据 0无降水 1雨 2雨夹雪 3雪 4 冻雨
        mergedata = np.full_like(tmp_value, -9999, dtype='int16')
        #        0无降水 => 0无降水
        mergedata = np.where((mergedata == -9999) & (tmp_value > -1) & (tmp_value <= 0.5), 0, mergedata)
        #        1雨 => 1雨
        mergedata = np.where((mergedata == -9999) & (tmp_value > 0.5) & (tmp_value <= 1.5), 1, mergedata)
        #        7雨夹雪 => 2雨夹雪
        mergedata = np.where((mergedata == -9999) & (tmp_value > 6.5) & (tmp_value <= 7.5), 2, mergedata)
        #        5干雪和6湿雪8冰粒 => 3雪
        mergedata = np.where((mergedata == -9999) & (tmp_value > 4.5) & (tmp_value <= 6.5), 3, mergedata)
        mergedata = np.where((mergedata == -9999) & (tmp_value > 7.5) & (tmp_value <= 8.5), 3, mergedata)
        #        3冻雨 => 4冻雨
        mergedata = np.where((mergedata == -9999) & (tmp_value > 2.5) & (tmp_value <= 3.5), 4, mergedata)

        # 3)计算五类数据的概率：计算每一个格点上51个成员0~4五类数据的概率
        prob0_array = np.mean(np.where((mergedata == 0), 1, 0), axis=0)
        prob1_array = np.mean(np.where((mergedata == 1), 1, 0), axis=0)
        prob2_array = np.mean(np.where((mergedata == 2), 1, 0), axis=0)
        prob3_array = np.mean(np.where((mergedata == 3), 1, 0), axis=0)
        prob4_array = np.mean(np.where((mergedata == 4), 1, 0), axis=0)

        lon_list = [lon_lat_dict["lon_s"], lon_lat_dict["lon_e"], lon_lat_dict["lon_d"]]
        lat_list = [lon_lat_dict["lat_s"], lon_lat_dict["lat_e"], lon_lat_dict["lat_d"]]
        prob0 = creat_m4_grd(lon_list, lat_list, prob0_array, 'C3E', fst_time, fst_h)
        prob1 = creat_m4_grd(lon_list, lat_list, prob1_array, 'C3E', fst_time, fst_h)
        prob2 = creat_m4_grd(lon_list, lat_list, prob2_array, 'C3E', fst_time, fst_h)
        prob3 = creat_m4_grd(lon_list, lat_list, prob3_array, 'C3E', fst_time, fst_h)
        prob4 = creat_m4_grd(lon_list, lat_list, prob4_array, 'C3E', fst_time, fst_h)
        # 将多种预报合并到一个网格数据里
        pt1_grid0 = meb.grid(lon_list, lat_list, level_list=[0, 1, 2, 3, 4])
        pt1 = meb.grid_data(pt1_grid0, np.array([prob0_array, prob1_array, prob2_array, prob3_array, prob4_array]))

        prob0_m3 = meb.interp_gs_linear(prob0, station)
        prob1_m3 = meb.interp_gs_linear(prob1, station)
        prob2_m3 = meb.interp_gs_linear(prob2, station)
        prob3_m3 = meb.interp_gs_linear(prob3, station)
        prob4_m3 = meb.interp_gs_linear(prob4, station)
        sta_combine = meb.combine_on_all_coords(prob0_m3, prob1_m3)
        sta_combine = meb.combine_on_all_coords(sta_combine, prob2_m3)
        sta_combine = meb.combine_on_all_coords(sta_combine, prob3_m3)
        sta_combine = meb.combine_on_all_coords(sta_combine, prob4_m3)

        meb.set_stadata_names(sta_combine, ['prob0', 'prob1', 'prob2', 'prob3', 'prob4'])

        if sta_combine is None:
            return
        c3e_file_ptype_1 = c3e_Ppt1.format(d_time=fst_time, fst=fst_h)
        c3e_file_ptype_2 = c3e_pt1.format(d_time=fst_time, fst=fst_h)
        if not os.path.exists(os.path.dirname(c3e_file_ptype_1)):
            os.makedirs(os.path.dirname(c3e_file_ptype_1))
        sta_combine.to_csv(c3e_file_ptype_1)
        meb.write_griddata_to_nc(pt1, c3e_file_ptype_2)
        print('成功输出至' + c3e_file_ptype_1)
        print('成功输出至' + c3e_file_ptype_2)
    except Exception as ex:
        print("计算C3E降水相态概率报错", ex)


def save_c3e_nc(shortname, fst_h, value, ens, lons, lats, d_time: datetime):
    """

    Args:
        shortname:
        fst_h:
        value:
        ens:
        lons:
        lats:
        d_time:

    Returns:

    """
    grid_w = meb.grid([70., 140., 0.5], [10., 60., 0.5])
    fst_time = d_time + timedelta(hours=8)
    dst_filepath = dst_c3e.format(d_time=fst_time, fst_h=fst_h)
    if not os.path.exists(os.path.dirname(dst_filepath)):
        os.makedirs(os.path.dirname(dst_filepath))
    grid0 = meb.grid([lons[0], lons[-1], lons[1] - lons[0]], [lats[0], lats[-1], lats[1] - lats[0]],
                     gtime=[fst_time.strftime("%Y%m%d%H")], dtime_list=[fst_h], level_list=[0], member_list=ens)
    grb = meb.grid_data(grid0, value)
    inter_grb = meb.interp_gg_linear(grb, grid_w, outer_value=None)
    inter_grb.name = shortname
    meb.write_griddata_to_nc(inter_grb, dst_filepath)
    print("保存文件: {} 成功".format(dst_filepath))
    c3e_convert_ptype(inter_grb.values, inter_grb.lon.values, inter_grb.lat.values, fst_time, fst_h)


def deal_c3e_data(d_time: datetime):
    """

    Args:
        d_time:

    Returns:

    """
    src_path_1 = src_c3e_1.format(d_time=d_time)
    src_path_2 = src_c3e_2.format(d_time=d_time)
    dst_filepath = dst_c3e.format(d_time=d_time + timedelta(hours=8), fst_h=240)

    if os.path.exists(dst_filepath):
        return
    # src_path_1 = r"C:\Users\xianyunhao\Desktop\ECMFENS_PRTY_1_2023010100_ASI_3_4.grib2"
    # src_path_2 = r"C:\Users\xianyunhao\Desktop\ECMFENS_PRTY_1_2023010100_ASI_4_4.grib2"
    if os.path.exists(src_path_1) and os.path.exists(src_path_2):
        try:
            _dict = dict()
            lats, lons, ens = None, None, None
            with pygrib.open(src_path_1) as pgs:
                for pg in pgs:
                    shortname = pg["shortName"]
                    fst_h = pg["forecastTime"]
                    value = pg["values"][::-1, :]
                    perturbationNumber = pg["perturbationNumber"]
                    lat_s = pg["latitudeOfLastGridPointInDegrees"]
                    lat_e = pg["latitudeOfFirstGridPointInDegrees"]
                    lat_d = pg["iDirectionIncrementInDegrees"]
                    lon_s = pg["longitudeOfFirstGridPointInDegrees"]
                    lon_e = pg["longitudeOfLastGridPointInDegrees"]
                    lon_d = pg["jDirectionIncrementInDegrees"]
                    if lats is None:
                        lats = np.arange(lat_s, lat_e + 0.1 * lat_d, lat_d)
                    if lons is None:
                        lons = np.arange(lon_s, lon_e + 0.1 * lon_d, lon_d)
                    if ens is None:
                        ens = np.arange(0, 51, 1)
                    if fst_h not in _dict.keys():
                        _dict[fst_h] = dict()
                    _dict[fst_h][perturbationNumber] = value
            with pygrib.open(src_path_2) as pgs:
                for pg in pgs:
                    shortname = pg["shortName"]
                    fst_h = pg["forecastTime"]
                    value = pg["values"][::-1, :]
                    perturbationNumber = pg["perturbationNumber"]
                    lat_s = pg["latitudeOfLastGridPointInDegrees"]
                    lat_e = pg["latitudeOfFirstGridPointInDegrees"]
                    lat_d = pg["iDirectionIncrementInDegrees"]
                    lon_s = pg["longitudeOfFirstGridPointInDegrees"]
                    lon_e = pg["longitudeOfLastGridPointInDegrees"]
                    lon_d = pg["jDirectionIncrementInDegrees"]
                    if lats is None:
                        lats = np.arange(lat_s, lat_e + 0.1 * lat_d, lat_d)
                    if lons is None:
                        lons = np.arange(lon_s, lon_e + 0.1 * lon_d, lon_d)
                    if ens is None:
                        ens = np.arange(0, 51, 1)
                    if fst_h not in _dict.keys():
                        _dict[fst_h] = dict()
                    _dict[fst_h][perturbationNumber] = value
            for fst_h_k, _value in _dict.items():
                _arr = np.ndarray((51, 1, 1, 1, len(lats), len(lons)), dtype=int)
                for i in range(0, 51, 1):
                    _arr[i, 0, 0, 0, :, :] = _value[i]
                save_c3e_nc(shortname, fst_h_k, _arr, ens, lons, lats, d_time)
        except Exception as ex:
            print(ex.__str__())


def obs_convert_ptype(sta, obs_ptype_path):
    """

    Args:
        sta:
        obs_ptype_path:

    Returns:

    """
    sta["data0"].loc[(sta["data0"] < 50)] = 0
    # 雨
    sta["data0"].loc[(sta["data0"] >= 50) & (sta["data0"] <= 55)] = 1
    sta["data0"].loc[(sta["data0"] >= 58) & (sta["data0"] <= 65)] = 1
    sta["data0"].loc[(sta["data0"] >= 80) & (sta["data0"] <= 82)] = 1

    # 雨夹雪
    sta["data0"].loc[(sta["data0"] >= 68) & (sta["data0"] <= 69)] = 2
    sta["data0"].loc[(sta["data0"] >= 83) & (sta["data0"] <= 84)] = 2

    # 降雪
    sta["data0"].loc[(sta["data0"] >= 70) & (sta["data0"] <= 76)] = 3
    sta["data0"].loc[sta["data0"] == 78] = 3
    sta["data0"].loc[(sta["data0"] >= 85) & (sta["data0"] <= 86)] = 3

    #
    sta["data0"].loc[(sta["data0"] >= 56) & (sta["data0"] <= 57)] = 4
    sta["data0"].loc[sta["data0"] == 77] = 4
    sta["data0"].loc[sta["data0"] == 79] = 4
    sta["data0"].loc[(sta["data0"] >= 66) & (sta["data0"] <= 67)] = 4
    sta = sta.drop(sta[(sta["data0"] > 4) & (sta["data0"] < 508)].index)
    sta["data0"].loc[(sta["data0"] >= 508) & (sta["data0"] <= 511)] = 9
    if not os.path.exists(os.path.dirname(obs_ptype_path)):
        os.makedirs(os.path.dirname(obs_ptype_path))
    meb.write_stadata_to_micaps3(sta, obs_ptype_path)
    print('成功输出至' + obs_ptype_path)


def process_obs(d_date: datetime, level=0, dtime=0, data_name=None, show=True):
    """

    Args:
        d_date:
        level:
        dtime:
        data_name:
        show:

    Returns:

    """
    outfile = land_obs.format(d_time=d_date)
    if not os.path.exists(outfile):
        qparams = {'interfaceId': 'getSurfEleByTime', 'dataCode': dataCode,
                   'elements': 'Datetime,Station_Id_D,Lat,Lon,' + element, }
        time_str = d_date.strftime("%Y%m%d%H%M")
        try:
            sta = CMADaasAccess.get_obs_micaps3_from_cmadaas(qparams, userId=userID, pwd=pwd, time=time_str, show=show,
                                                             url=cmadaas_url)

        except:
            exstr = traceback.format_exc()
            print(exstr)
            return None

    outfile_ptype = land_obs6.format(d_time=d_date)

    if not os.path.exists(outfile_ptype):
        if sta is not None:
            try:
                if data_name is None:
                    data_name = dataCode
                meb.set_stadata_names(sta, data_name_list=[data_name])
                sta['level'] = level
                sta['dtime'] = dtime
                if station is not None:
                    sta = meb.put_stadata_on_station(sta, station)
                    meb.write_stadata_to_micaps3(sta, outfile, creat_dir=True)
                    print('成功输出至' + outfile)
                    sta_temp = meb.read_stadata_from_micaps3(outfile)
                    obs_convert_ptype(sta_temp, outfile_ptype)
            except Exception as ex:
                print(ex.__str__())
        else:
            print("数据读取失败")


def run_obs(s_date: datetime, e_date: datetime):
    """

    Args:
        s_date:
        e_date:

    Returns:

    """
    while s_date < e_date:
        process_obs(s_date)
        s_date += timedelta(hours=1)


def run_fst_c1d(s_date: datetime, e_date: datetime):
    """

    Args:
        s_date:
        e_date:

    Returns:

    """
    ps = multiprocessing.Pool(2)
    while s_date < e_date:
        ps.apply_async(deal_c1d_data, args=(s_date,))
        s_date += timedelta(hours=12)
    ps.close()
    ps.join()


def run_fst_c3e(s_date: datetime, e_date: datetime):
    """

    Args:
        s_date:
        e_date:

    Returns:

    """
    ps = multiprocessing.Pool(2)
    while s_date < e_date:
        ps.apply_async(deal_c3e_data, args=(s_date,))
        s_date += timedelta(hours=12)
    ps.close()
    ps.join()


if __name__ == '__main__':
    if __name__ == '__main__':
        # 参数：OBS 2023050100-2023051500 2023040100-2023041500  时间为国际时间  00 12
        model = sys.argv[1]
        if len(sys.argv) == 2:
            startT, endT = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(
                days=1), datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            if "OBS" == model:
                run_obs(startT, endT)
            elif "C1D" == model:
                run_fst_c1d(startT, endT)
            elif "C3E" == model:
                run_fst_c3e(startT, endT)
            elif "ALL" == model:
                run_obs(startT, endT)
                run_fst_c1d(startT, endT)
                run_fst_c3e(startT, endT)
            else:
                print("不能识别该模式: " + model)

        elif len(sys.argv) > 2:
            if "OBS" == model:
                for date_str in sys.argv[2:]:
                    startT, endT = [datetime.strptime(i, '%Y%m%d%H') for i in date_str.split('-')]
                    run_obs(startT, endT)
            elif "C1D" == model:
                for date_str in sys.argv[2:]:
                    startT, endT = [datetime.strptime(i, '%Y%m%d%H') for i in date_str.split('-')]
                    run_fst_c1d(startT, endT)
            elif "C3E" == model:
                for date_str in sys.argv[2:]:
                    startT, endT = [datetime.strptime(i, '%Y%m%d%H') for i in date_str.split('-')]
                    run_fst_c3e(startT, endT)
            elif "ALL" == model:
                for date_str in sys.argv[2:]:
                    startT, endT = [datetime.strptime(i, '%Y%m%d%H') for i in date_str.split('-')]
                    run_obs(startT, endT)
                    run_fst_c1d(startT, endT)
                    run_fst_c3e(startT, endT)
            else:
                print("不能识别该模式: " + model)
        else:
            pass