# -- coding: utf-8 --
# @Time : 2023/5/17 17:22
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : parser_ptype_NAFP.py
# @Software: PyCharm
import os, re
import sys
import meteva
import pygrib
import numpy as np
import xarray as xr
from meteva.base.io import CMADaasAccess
from datetime import datetime, timedelta
import meteva.base as meb
import traceback

def meteva_grid(grb, latorder):
    dataTimeStr = '0000' if grb.dataTime == 0 else str(grb.dataTime)
    dt = datetime.strptime(str(grb.dataDate) + dataTimeStr, '%Y%m%d%H%M')
    dtime = grb.dataTime
    dname = grb.shortName
    level = grb.level
    lon = np.arange(grb.Ni) * grb.iDirectionIncrementInDegrees + grb.longitudeOfFirstGridPointInDegrees

    if latorder is None:
        if grb.latitudeOfFirstGridPointInDegrees > grb.latitudeOfLastGridPointInDegrees:
            lat = grb.latitudeOfFirstGridPointInDegrees - np.arange(grb.Nj) * grb.jDirectionIncrementInDegrees
            ds = np.array(grb.values) if type(grb.values) == np.ma.core.MaskedArray else grb.values
        else:
            lat = grb.latitudeOfFirstGridPointInDegrees + np.arange(grb.Nj) * grb.jDirectionIncrementInDegrees
            ds = np.array(grb.values) if type(grb.values) == np.ma.core.MaskedArray else grb.values
    elif latorder:  # s to n
        if grb.latitudeOfFirstGridPointInDegrees > grb.latitudeOfLastGridPointInDegrees:
            lat = grb.latitudeOfLastGridPointInDegrees + np.arange(grb.Nj) * grb.jDirectionIncrementInDegrees
            ds = np.array(grb.values) if type(grb.values) == np.ma.core.MaskedArray else grb.values
            ds = ds[::-1]
        else:
            lat = grb.latitudeOfFirstGridPointInDegrees + np.arange(grb.Nj) * grb.jDirectionIncrementInDegrees
            ds = np.array(grb.values) if type(grb.values) == np.ma.core.MaskedArray else grb.values
    else:  # n to s
        if grb.latitudeOfFirstGridPointInDegrees > grb.latitudeOfLastGridPointInDegrees:
            lat = grb.latitudeOfFirstGridPointInDegrees - np.arange(grb.Nj) * grb.jDirectionIncrementInDegrees
            ds = np.array(grb.values) if type(grb.values) == np.ma.core.MaskedArray else grb.values
        else:
            lat = grb.latitudeOfLastGridPointInDegrees - np.arange(grb.Nj) * grb.jDirectionIncrementInDegrees
            ds = np.array(grb.values) if type(grb.values) == np.ma.core.MaskedArray else grb.values
            ds = ds[::-1]

    da = xr.DataArray(ds.reshape((1, 1, 1, 1, grb.Nj, grb.Ni)),
                      coords={'member': [dname], 'level': [level], 'time': [dt], 'dtime': [dtime], 'lat': lat,
                              'lon': lon},
                      dims=['member', 'level', 'time', 'dtime', 'lat', 'lon'])
    da.attrs["dtime_type"] = "hour"
    da.name = dname
    return da


def parser_grib(begin_time, fmt_PRTY, outpath):
    file_path = datetime.strftime(begin_time, fmt_PRTY)
    with pygrib.open(file_path) as grbs:
        for grb in grbs:
            try:
                cst = int(grb.endStep)
                griddata = meteva_grid(grb, True)
                save_PRTY = datetime.strftime(begin_time, outpath).format(cst=cst)
                interp_griddata = meb.interp_gg_linear(griddata, grid_w, outer_value=-9999)
                meb.write_griddata_to_micaps4(interp_griddata, save_PRTY, creat_dir=True, effectiveNum=2, show=True)
            except Exception as e:
                print(e)
                continue

def readW_stadata_from_cmadaas(dataCode,element,time,station,outfile,level=0,dtime=0,data_name=None,show=True):
    ## stations
    qparams = {'interfaceId': 'getSurfEleByTime',
               'dataCode': dataCode,
               'elements': 'Datetime,Station_Id_D,Lat,Lon,'+element,
               }  ##字典规定接口名称，数据代码，下载要素代码。
    # 数据部分： SURF_CHN_MUL_HOR_N 数据为全国基准站(2400多站点)逐小时地面要素
    # 接口部分： getSurfEleByTime 接口为按时间提取地面要素
    # 要素部分： PRE_24h 为地面降水，其他包括TEM、TEM_Max、RHU、WIN_D_Avg_10mi、WIN_S_Avg_10mi等，可自己选择
    time_str = time.strftime("%Y%m%d%H%M")
    try:
        sta = CMADaasAccess.get_obs_micaps3_from_cmadaas(qparams, userId=userID, pwd=pwd, time=time_str, show=show, url=cmadaas_url)
    except:
        if show:
            exstr = traceback.format_exc()
            #print(exstr)
        return None
    if sta is not None:
        if data_name is None:
            data_name = dataCode
        meteva.base.set_stadata_names(sta,data_name_list=[data_name])
        sta['level'] = level
        sta['dtime'] = dtime
        # if (station is not None):
        #     sta = meteva.base.put_stadata_on_station(sta, station)
        meb.write_stadata_to_micaps3(sta, outfile, creat_dir=True)
        print('成功输出至' + outfile)
    else:
        print("数据读取失败")

def save_ens_nc(shortname, fst_h, value, ens, lons, lats, d_time: datetime):
    """
    集合预报
    """
    fst_time = d_time
    filepath = outpath.format(d_time=fst_time, fst_h=fst_h)
    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))
    grid0 = meb.grid([lons[0], lons[-1], lons[1] - lons[0]], [lats[0], lats[-1], lats[1] - lats[0]],
                     gtime=[fst_time.strftime("%Y%m%d%H")], dtime_list=[fst_h], level_list=[0], member_list=ens)
    grb = meb.grid_data(grid0, value)
    inter_grb = meb.interp_gg_linear(grb, grid_w, outer_value=None)
    inter_grb.name = shortname
    meb.write_griddata_to_nc(inter_grb, filepath)
    print('成功输出至' + filepath)


if __name__ == '__main__':
    begin_time = datetime.now().replace(hour=8)
    grid_w = meb.grid([70., 140., 0.05], [10., 60., 0.05])
    parser_grib(begin_time, fmt_PRTY, outpath)


    _arr = np.ndarray((51, 1, 1, 1, len(lats), len(lons)), dtype=int)
    for i in range(0, 51, 1):
        _arr[i, 0, 0, 0, :, :] = _value[i]
    save_ens_nc(shortname, fst_h_k, _arr, ens, lons, lats, d_time)