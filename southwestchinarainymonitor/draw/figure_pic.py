#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
   @Project   ：Wiztek.DataService.MountainTorrent.Py 
   
   @File      ：figure_pic.py
   
   @Author    ：yhaoxian
   
   @Date      ：2022/2/18 11:00 
   
   @Describe  : 
   
"""

import matplotlib as mpl
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import cartopy.feature as c_feature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import cartopy.crs as c_crs
import numpy as np
from utils import config
from utils.logging import logger
import geopandas
import matplotlib.pyplot as plt

mpl.use('AGG')

plt.rcParams['font.sans-serif'] = ['SIMHEI']  # 显示中文标签
plt.rcParams['axes.unicode_minus'] = False


class DrawImages(object):
    """

    """

    def __init__(self, fig=None, ax=None, shp_idx=None, axes=None, extent=None, sub_nine_dashed_extent=None, x_scale=10,
                 y_scale=10, central_longitude=0):
        self.shp_idx = shp_idx
        if extent is None:
            extent = [60, 140, 10, 60]
        if axes is None:
            axes = [0.06, 0.08, 0.85, 0.85]

        if sub_nine_dashed_extent is None:
            sub_nine_dashed_extent = [0.0305, 0.096, 0.2, 0.25]
        self.sub_nine_dashed_extent = sub_nine_dashed_extent
        if ax is None:
            self.fig = plt.figure(figsize=[16, 9], dpi=200)
            self.ax = self.fig.add_axes(axes, projection=c_crs.PlateCarree(central_longitude=central_longitude))
        else:
            self.fig = fig
            self.ax = ax
        self.ax.set_extent(extent, crs=c_crs.PlateCarree())
        self.x_ticks = np.arange(extent[0], extent[1] + 1, x_scale)
        self.y_ticks = np.arange(extent[2], extent[3] + 1, y_scale)
        self.shp_folder = "./draw/shp"
        self.china_bool = False
        self.color_bar_extent = [self.ax.get_position().x1 + 0.01, self.ax.get_position().y0, 0.02, self.ax.get_position().height]

    def set_title(self, title=None, font_size=18):
        """

        :param title:
        :param font_size:
        :return:
        """
        if title is not None:
            self.ax.set_title(title, zorder=1, pad=15, fontdict=dict(fontsize=font_size))

    def add_one_or_multi_province(self, add_china_shp=True, add_world_shp=False, add_sub_nine_dashed=True,
                                  land_color="#ffffff", ocean_color="#ffffff"):
        """

        :param add_china_shp:
        :param add_world_shp:
        :param add_sub_nine_dashed:
        :param land_color:
        :param ocean_color:
        :return:
        """
        self._set_x_y_axis()

        self.__set_grid()

        if add_china_shp:
            self._add_china_shp(self.ax)

        if add_world_shp:
            self._draw_world_map(land_color=land_color, ocean_color=ocean_color)

        if add_sub_nine_dashed:
            self._add_sub_nine_dashed_line(land_color=land_color, ocean_color=ocean_color)

        if self.shp_idx is not None:
            china2 = geopandas.GeoDataFrame.from_file("{}/all_full/all.shp".format(self.shp_folder))

            if len(self.shp_idx) == 1 and self.shp_idx[0] == "china":
                self.china_bool = True

            if not self.china_bool:
                for index in range(0, len(china2.name)):
                    name = china2.name[index]
                    code = china2.adcode[index]
                    _bool = False
                    for _n in self.shp_idx:
                        if _n == name or _n == code or (name is not None and _n in name):
                            _bool = True

                    if not _bool:
                        continue
                    self.ax.add_feature(ShapelyFeature([china2["geometry"][index]], c_crs.PlateCarree()),
                                        facecolor='None', edgecolor="#111111", linewidth=0.8)

    def _set_x_y_axis(self):
        self.ax.set_xticks(self.x_ticks, crs=c_crs.PlateCarree())
        self.ax.set_yticks(self.y_ticks, crs=c_crs.PlateCarree())
        self.ax.tick_params(labelcolor='#2b2b2b', labelsize=15, width=1, top=True, right=True)
        # zero_direction_label用来设置经度的0度加不加E和W
        lon_formatter = LongitudeFormatter(zero_direction_label=False)
        lat_formatter = LatitudeFormatter()
        self.ax.xaxis.set_major_formatter(lon_formatter)
        self.ax.yaxis.set_major_formatter(lat_formatter)
        self.ax.grid(True, linestyle='--')

    def __set_grid(self):
        mi_loc = plt.MultipleLocator(2.5)
        self.ax.yaxis.set_minor_locator(mi_loc)
        self.ax.grid(True, linestyle='--', axis='y', which='minor')

    def _add_china_shp(self, ax):
        hyd1 = ShapelyFeature(Reader('{}/hyd1_4l.shp'.format(self.shp_folder)).geometries(), c_crs.PlateCarree())
        ax.add_feature(hyd1, facecolor='None', edgecolor="blue", linewidth=0.2)

        continents = ShapelyFeature(Reader('{}/continents_lines.shp'.format(self.shp_folder)).geometries(),
                                    c_crs.PlateCarree())
        ax.add_feature(continents, facecolor='None', edgecolor="#111111", linewidth=0.5)

        province = ShapelyFeature(Reader('{}/province_l.shp'.format(self.shp_folder)).geometries(), c_crs.PlateCarree())
        ax.add_feature(province, facecolor='None', edgecolor="#111111", linewidth=0.8)

    def _draw_world_map(self, land_color, ocean_color):
        self.ax.coastlines(resolution='50m', edgecolor='#111111', lw=0.2)
        self.ax.add_feature(c_feature.OCEAN.with_scale('110m'), facecolor=ocean_color)
        self.ax.add_feature(c_feature.LAND.with_scale('110m'), facecolor=land_color)

    def _add_sub_nine_dashed_line(self, land_color, ocean_color):
        sub_ax = self.fig.add_axes(self.sub_nine_dashed_extent, projection=c_crs.PlateCarree())
        self._add_china_shp(sub_ax)
        sub_ax.add_feature(c_feature.OCEAN.with_scale('110m'), facecolor=ocean_color)
        sub_ax.add_feature(c_feature.LAND.with_scale('110m'), facecolor=land_color)
        sub_ax.set_extent([105, 125, 0, 25])

    def add_scatter(self, arr_list):
        for arr in arr_list:
            self.__add_scatter(arr)

    def __add_scatter(self, arr):
        if len(arr) == 6:
            self.ax.scatter(arr[0], arr[1], s=arr[2], marker=arr[3], c=arr[4], label=arr[5])
        if len(arr) == 5:
            self.ax.scatter(arr[0], arr[1], c=arr[2], vmin=arr[3], vmax=arr[4], cmap=plt.get_cmap("jet"))
            # self.ax.scatter(arr[0], arr[1], c=arr[2], vmin=arr[3], vmax=arr[4], cmap="jet")
        if len(arr) == 7:
            self.ax.scatter(arr[0], arr[1], c=arr[2], vmin=arr[3], vmax=arr[4], cmap=arr[5])
            for i in range(0, len(arr[0])):
                self.ax.annotate(arr[6], xy=(arr[0][i], arr[1][i]), xytext=(arr[0][i] + 0.1, arr[1][i] + 0.1))

    def add_annotate(self, arr_list):
        for arr in arr_list:
            self.__add_annotate(arr[0], arr[1], arr[2], arr[3], arr[4])

    def __add_annotate(self, x, y, describe, c, font_size):
        self.ax.text(x, y, describe, c=c, fontsize=font_size)

    def add_legend(self):
        self.__add_legend()

    def __add_legend(self):
        self.ax.legend(loc='upper left', fontsize=15)

    def add_color_bar(self, value_min, value_max):
        ax2 = self.fig.add_axes([self.ax.get_position().x1 + 0.01, self.ax.get_position().y0, 0.02, self.ax.get_position().height])
        norm = plt.Normalize(value_min, value_max)
        mpl.colorbar.ColorbarBase(ax2, norm=norm, cmap=plt.get_cmap("jet"), orientation='vertical')

    def add_color_bar_set(self, value_min, value_max):
        ax2 = self.fig.add_axes([self.ax.get_position().x1 + 0.01, self.ax.get_position().y0, 0.02, self.ax.get_position().height])
        norm = plt.Normalize(value_min, value_max)
        mpl.colorbar.ColorbarBase(ax2, norm=norm, cmap=plt.get_cmap("Set1"), orientation='vertical')

    def save_fig(self, save_file):
        config.mkdir(save_file)
        logger.info(save_file)
        self.fig.savefig(save_file)