# -- coding: utf-8 --
# @Time : 2023/5/17 17:22
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : parser_ptype_NAFP.py
# @Software: PyCharm
import os, re
import sys
import bz2
import meteva
import struct
import pygrib
import numpy as np
import xarray as xr
from meteva.base.io import CMADaasAccess
from datetime import datetime, timedelta
from config_parser import *
import meteva.base as meb
import traceback

station = meb.read_stadata_from_micaps3(station_file)

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

def pnum_grib_dict(msgdata):
    pnum_dict = {}
    pos = 0
    while (pos < len(msgdata)):
        msgver = struct.unpack('B', msgdata[pos + 7:pos + 8])[0]
        if msgver == 1:
            nextpos = pos + struct.unpack('>i', b'\0' + msgdata[pos + 4:pos + 7])[0]
        elif msgver == 2:
            nextpos = pos + struct.unpack('>q', msgdata[pos + 8:pos + 16])[0]
        else:
            raise Exception('unknown message version')
        grb = pygrib.fromstring(msgdata[pos:nextpos])
        pnum = grb.perturbationNumber
        pos = nextpos
        if not filter_msg_with_dict(grb, filters_PTYPE):
            continue
        pnum_dict[pnum] = grb
    return pnum_dict

def filter_msg_with_dict(grb, filters):
    if filters is None:
        return True
    for k, v in filters.items():
        if type(v) is list:
            if grb[k] not in v:
                return False
        else:
            shortName = grb.shortName
            if shortName != v:
                return False
    return True

def get_seq_from_dt_and_fn(dt, fname, fnfmt):
    rsts = re.findall(fnfmt, fname)
    if len(rsts) != 1:
        return None
    stime = datetime(dt.year, int(rsts[0][1][:2]), int(rsts[0][1][2:4]), int(rsts[0][1][4:6]))
    etime = datetime(dt.year, int(rsts[0][2][:2]), int(rsts[0][2][2:4]), int(rsts[0][2][4:6]))
    if stime != dt:
        return None
    if etime < stime:
        etime = datetime(dt.year + 1, int(rsts[0][2][:2]), int(rsts[0][2][2:4]))
    return int((etime - stime).total_seconds() / 3600)

def read_and_decompress(filename):
    with open(filename, 'rb') as f:
        bindata = f.read()
    return bz2.decompress(bindata)

def parser_C1D(begin_time, fmt_PRTY, outpath):
    file_path = datetime.strftime(begin_time, fmt_PRTY)
    with pygrib.open(file_path) as grbs:
        for grb in grbs:
            try:
                cst = int(grb.endStep)
                griddata = meteva_grid(grb, True)
                save_PRTY = datetime.strftime(begin_time, outpath).format(cst=cst)
                interp_griddata = meb.interp_gg_linear(griddata, grid_w, outer_value=outer_value)
                meb.write_griddata_to_micaps4(interp_griddata, save_PRTY, creat_dir=True, effectiveNum=2, show=True)
            except Exception as e:
                print(e)
                continue

def parser_C3E(begin_time, fmt_PRTY, outpath):
    file_path = datetime.strftime(begin_time, os.path.dirname(fmt_PRTY))
    file_fmt = os.path.basename(fmt_PRTY)
    fnames = os.listdir(file_path)
    for fname in fnames:
        try:
            cst = get_seq_from_dt_and_fn(begin_time, fname, file_fmt)
            if cst is None:
                continue
            msg_data = read_and_decompress(os.path.join(file_path, fname))
            pnum_dict = pnum_grib_dict(msg_data)
            for pnum, pnum_grid in pnum_dict.items():
                griddata = meteva_grid(pnum_grid, True)
                save_PRTY = datetime.strftime(begin_time, outpath).format(pnum=pnum, cst=cst)
                interp_griddata = meb.interp_gg_linear(griddata, grid_w, outer_value=outer_value)
                meb.write_griddata_to_micaps4(interp_griddata, save_PRTY, creat_dir=True, effectiveNum=2, show=True)
        except Exception as e:
            print(e)
            continue

def readW_stadata_from_cmadaas(dataCode,element,time,station, outfile, level=0,dtime=0,data_name= None, show=True):
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

def proc_nafp(fix_btime, fix_etime, model):
    while fix_btime <= fix_etime:
        try:
            print(fix_btime)
            if model == 'C3E':
                parser_C3E(fix_btime, path_C3E, save_PRTY_C3E)
            else:
                # parser_C1D(fix_btime, path_C1D, save_PRTY_C1D)
                parser_C1D(fix_btime, path_D1D, save_PRTY_D1D)
            fix_btime += timedelta(days=1)
        except Exception as e:
            fix_btime += timedelta(days=1)
            print(e)

def proc_obs(beginT, endT):
    while beginT <= endT:
        try:
            outfile = land_obs.format(rp_T=beginT)
            print(beginT)
            readW_stadata_from_cmadaas(dataCode, element, beginT, station, outfile)
            beginT += timedelta(hours=3)
        except Exception as e:
            beginT += timedelta(hours=3)
            print(e)

def parser_ptype(argv):
    if argv[1] == 'OBS':
        if len(argv) > 2:
            for time_list in argv[2:]:
                fix_stime, fix_etime = [datetime.strptime(i, '%Y%m%d%H') for i in time_list.split('-')]
                proc_obs(fix_stime, fix_etime)
        else:
            fix_etime = datetime.now().replace(minute=0)
            fix_stime = fix_etime - timedelta(days=1)
            proc_obs(fix_stime, fix_etime)
    else:
        model = argv[1]
        for hour in [0, 12]:
            if len(argv) > 2:
                for time_list in argv[2:]:
                    startT, endT = [datetime.strptime(i, '%Y%m%d%H') for i in time_list.split('-')]
                    fix_stime = startT.replace(hour=hour, minute=0)
                    fix_etime = endT.replace(hour=hour, minute=0)
                    proc_nafp(fix_stime, fix_etime, model)
            else:
                fix_etime = datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0)
                fix_stime = fix_etime - timedelta(days=10)
                proc_nafp(fix_stime, fix_etime, model)

if __name__ == '__main__':
    #参数：OBS 2023051000-2023051100
    parser_ptype(sys.argv)