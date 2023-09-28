# -- coding: utf-8 --
# @Time : 2023/3/17 16:24
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : cartopy_subplot.py
# @Software: PyCharm
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# plot dbz-panel by WRF model data using cartopy

import numpy as np
from matplotlib import cm, colors
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import netCDF4 as nc

fip = "/home/storm/python/sample_file/"
fin1 = "wrfout_v2_Lambert.nc"

ti = [6, 7, 8, 9]
xs = 0
xe = -1
ys = 0
ye = -1
zs = 0
ze = -1

data = nc.Dataset(fip + fin1, "r")
truelat1 = data.TRUELAT1
truelat2 = data.TRUELAT2
stalon = data.CEN_LON
stalat = data.CEN_LAT

fn = "Arial"
fs = 10
ld = 0.
nrows = 2
ncols = 2

fig, axes = plt.subplots(nrows=nrows, ncols=ncols, subplot_kw=dict(projection=ccrs.PlateCarree(), aspect='auto'))

for i, ax in zip(np.arange(0, nrows * ncols), axes.flat):
    rain = data.variables["RAINC"][ti[i], xs:xe, ys:ye]
    lat = data.variables["XLAT"][ti[i], xs:xe, ys:ye]
    lon = data.variables["XLONG"][ti[i], xs:xe, ys:ye]

    ax.set_xticks(range(int(lon[-1, 0]), int(lon[0, -1]) + 1, 2))
    ax.set_yticks(range(int(lat[0, 0]), int(lat[-1, -1]) + 1, 1))
    lon_formatter = LongitudeFormatter(number_format='.0f',
                                       degree_symbol='',
                                       dateline_direction_label=True)
    lat_formatter = LatitudeFormatter(number_format='.0f',
                                      degree_symbol='')
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    con = ax.contourf(lon, lat, rain)
    ax.hold(True)
    ax.coastlines(resolution='10m')

    # 设置坐标轴范围
    ax.set_xlim([lon[-1, 0], lon[0, -1]])
    ax.set_ylim([lat[0, 0], lat[-1, -1]])
    ax.set_adjustable('box-forced')

fig.subplots_adjust(hspace=0.05, wspace=0.05)
leg = fig.colorbar(con, ax=axes.ravel().tolist(), pad=0.01)
# plt.savefig("panel.eps")
plt.show()