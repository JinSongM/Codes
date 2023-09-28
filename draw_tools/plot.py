# -*- coding: UTF-8 -*-
"""
@Name:plot_high.py
@Auth:yujw
@Date:2023/2/14-12:50
"""
import numpy as np
import pandas as pd
import meteva.base as meb
from Utils.micaps import open_diamond5_file
import matplotlib.pyplot as plt
import matplotlib as mpl
from metpy.plots import Hodograph, SkewT
from datetime import datetime, timedelta
from Utils.file import File
import xarray as xr

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def plot_high_sta(sta_path, d_time):
    sta_data = open_diamond5_file(sta_path, encoding="gbk")
    xr_data = xr.open_dataset("./data/FY4B-_GIIRS-_N_REGC_1330E_L2-_AVP-_MULT_GLL_20230212130328_20230212140836_012KM_V0001.NC")
    #levels = xr_data["pre"].values
    levels = [500, 700, 850, 1000]
    dic = {
        # "59948": "三亚",
        "51463": "乌鲁木齐站",
        "58238": "南京站",
        "54511": "北京站",
    }
    for sta in list(dic.keys()):
        one_data = sta_data[sta_data["stationId"] == sta]
        one_data = one_data.sort_values(by="气压")
        # plot = PlotXy()
        p = one_data["气压"].values.astype("int")
        T = one_data["温度"].values
        d = one_data["露点"].values
        sta_xr_data_T, sta_xr_data_DPT = [], []
        for level in levels:
            T_array_name, Dpt_array_name = 'AT_Prof_' + str(level), 'AQ_Prof_' + str(level)
            FY4B_LAT = sorted(xr_data['Latitude'].data[:, 0])
            FY4B_LON = sorted(xr_data['Longitude'].data[0,:], reverse=True)
            # df_array_lat, df_array_lon= np.absolute(np.array(FY4B_LAT) - one_data["lat"].values[0]), \
            #                              np.absolute(np.array(FY4B_LON) - one_data["lon"].values[0])
            # df_array_lat, df_array_lon= np.absolute(np.array(FY4B_LAT) - one_data["lat"].values[0]), \
            #                              np.absolute(np.array(FY4B_LON) - one_data["lon"].values[0])
            # index_y, index_x = df_array_lat.argmin(), df_array_lon.argmin()
            # data_T = xr_data[T_array_name].interp(y=index_y, x=index_x).values.reshape(-1, )[0] - 273.15
            # data_DPT = xr_data[Dpt_array_name].interp(y=index_y, x=index_x).values.reshape(-1, )[0]

            data_sta = {
                '站号': [sta],
                "经度": [one_data["lon"].values[0]],
                "纬度": [one_data["lat"].values[0]],

            }
            M3_grd = pd.DataFrame(data_sta)
            sta_sta = meb.sta_data(M3_grd, columns=["id", "lon", "lat"])

            grid0 = meb.grid([min(FY4B_LON), max(FY4B_LON), 0.04], [min(FY4B_LAT), max(FY4B_LAT), 0.04])
            data_array_T = xr_data[T_array_name].data
            data_array_T[data_array_T <= -9999] = np.nan
            grd_T = meb.grid_data(grid0, data=data_array_T[::-1])
            data_T = meb.interp_gs_linear(grd_T, sta_sta).data0[0] - 273.15

            data_array_Dpt = xr_data[Dpt_array_name].data
            data_array_Dpt[data_array_Dpt <= -9999] = np.nan
            grd_Dpt = meb.grid_data(grid0, data=data_array_Dpt[::-1])
            data_Dpt = meb.interp_gs_linear(grd_Dpt, sta_sta).data0[0]

            sta_xr_data_T.append(data_T)
            sta_xr_data_DPT.append(data_Dpt)


        fig = plt.figure(figsize=(12, 12), dpi=120)

        # Grid for plots
        skew = SkewT(fig, rotation=0)

        # Plot the data using normal plotting functions, in this case using
        # log scaling in Y, as dictated by the typical meteorological plot
        skew.plot(p, T, 'r', label="温度")
        skew.plot(p, d, 'green', label="露点")
        skew.plot(levels, sta_xr_data_T, 'purple', label="FY4B-温度")
        skew.plot(levels, sta_xr_data_DPT, 'blue', label="FY4B-湿度")
        skew.ax.set_ylim(1000, 100)

        # Add the relevant special lines
        skew.plot_dry_adiabats()
        skew.plot_moist_adiabats()
        skew.plot_mixing_lines()

        # Good bounds for aspect ratio
        skew.ax.set_xlim(-100, 60)
        skew.ax.text(0, 1.02, "{}[{:.2f},{:.2f}] 时间：{:%Y-%m-%d %H}:00 FY(UTC):{}点 ".format(dic[sta], one_data["lon"].values[0], one_data["lat"].values[0], d_time, 14), transform=skew.ax.transAxes, fontdict=dict(fontsize=14))
        plt.legend()
        file_path = "./pic/{:%Y%m%d%H}/{}_14.png".format(d_time, sta)
        File(file_path).mkdirs()
        fig.savefig(file_path, bbox_inches="tight", pad_inches=0.15)
        plt.close(fig)


def process():
    #plot_high_sta("./data/23021220.000", datetime.strptime("23021220", "%y%m%d%H"))
    plot_high_sta("./data/23021208.000", datetime.strptime("23021208", "%y%m%d%H"))


if __name__ == '__main__':
    process()
