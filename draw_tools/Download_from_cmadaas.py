# -- coding: utf-8 --
# @Time : 2023/6/1 9:33
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : Download_from_cmadaas.py
# @Software: PyCharm
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
import meteva.base as meb
import traceback

station = meb.read_stadata_from_micaps3('station_file.m3')


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
        if (station is not None):
            sta = meteva.base.put_stadata_on_station(sta, station)
            meb.write_stadata_to_micaps3(sta, outfile, creat_dir=True)
            print('成功输出至' + outfile)
    else:
        print("数据读取失败")

if __name__ == '__main__':
    #参数：OBS 2023051000-2023051100
    dataCode = 'SURF_CHN_MUL_HOR'
    element = 'WEP_Now'
    userID = 'NMC_GUOYUNQIAN'
    pwd = '19871013Guo!'
    # userID = 'NMC_XIONG1'
    # pwd = 'Xiong111111#'
    cmadaas_url = r'http://10.40.17.54/music-ws/api?'

    readW_stadata_from_cmadaas(**{})