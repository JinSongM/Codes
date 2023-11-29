# -- coding: utf-8 --
# @Time : 2023/11/28 10:59
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : convert.py
# @Software: PyCharm
import meteva.base as meb
import pandas as pd
from datetime import datetime


def creat_M3_grd(data):
    """
    构建m3标准格式
    :param ID_LIST: 站号列表
    :param Lon_list: 经度列表
    :param Lat_list: 维度列表
    :param Data_list: 数据列表
    :return:
    """
    # 构建站点数据标准格式
    M3_grd = pd.DataFrame(data)

    sta = meb.sta_data(M3_grd, columns=["id", "lon", "lat", 'data0'])
    meb.set_stadata_coords(sta, level=0, time=datetime(2023, 1, 1, 8, 0), dtime=0)
    return sta

def read_csv():
    dataframe = pd.read_csv(r'D:\Wiztek_Python\cartopy_draw\plot\202309191200.csv')
    dataframe = dataframe[(dataframe['WIN_S_Inst_Max'] < 9999) & (dataframe['WIN_S_Inst_Max'] >= 17.2)]
    dataframe = dataframe[['Station_Id_d', 'Lon', 'Lat', 'WIN_S_Inst_Max']]
    sta = creat_M3_grd(dataframe)
    meb.write_stadata_to_micaps3(sta, r'D:\Wiztek_Python\cartopy_draw\plot\ws_23091912.000')
    return sta


def main():
    dataframe = read_csv()
    print(dataframe)

if __name__ == '__main__':
    main()