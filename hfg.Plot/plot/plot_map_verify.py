import matplotlib as mpl
import pandas as pd
from PIL import Image

mpl.use('AGG')

import matplotlib.pyplot as plt
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import cartopy.feature as c_feature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import geopandas
import cartopy.crs as ccrs
from matplotlib.path import Path
from matplotlib.patches import PathPatch
import shapefile
import numpy as np
import matplotlib.font_manager as font_manager
import xarray as xr
import cartopy.io.img_tiles as cimgt

font_manager.fontManager.addfont('./fonts/HELVETI1.TTF')
font_manager.fontManager.addfont('./fonts/simkai.ttf')
mpl.rcParams['font.sans-serif'] = 'Kaiti'  # 显示中文标签
mpl.rcParams['axes.unicode_minus'] = False  # 显示中文标签

CONF = {
    "ERT": ccrs.Robinson,
    "ORT": ccrs.Orthographic,
    "TERRAIN": ccrs.GOOGLE_MERCATOR
}


class DrawImages(object):
    def __init__(self, shp_idx=None, axes=None, extent=None, x_scale=10, y_scale=10, central_longitude=160, dpi=200,
                 region=None):
        self.shp_idx = shp_idx
        self.extent = extent
        if extent is None:
            extent = [70, 140, 10, 55]
        if axes is None:
            axes = [0.0, 0.0, 0.9, 0.9]
        self.fig = plt.figure(figsize=[12, 10], dpi=dpi)
        self.region = region
        if region in CONF.keys():
            if region == "ORT":
                self.ax = self.fig.add_axes(axes, projection=CONF[region](central_longitude=central_longitude,
                                                                          central_latitude=35.0))
            elif region == "ERT":
                self.ax = self.fig.add_axes(axes,
                                            projection=CONF[region](central_longitude=central_longitude, globe=None))
            else:
                self.ax = self.fig.add_axes(axes, projection=CONF[region])
            self.ax.set_global()
            # self.ax.set_extent(extent, crs=ccrs.PlateCarree())
        else:
            self.ax = self.fig.add_axes(axes, projection=ccrs.PlateCarree(central_longitude=central_longitude))
            self.ax.set_extent(extent, crs=ccrs.PlateCarree())
            self.x_ticks = np.arange(extent[0], extent[1] + 1, x_scale)
            self.y_ticks = np.arange(extent[2], extent[3] + 1, y_scale)
        self.shp_folder = "./plot/shp"
        self.china_bool = False

        self.color_bar_extent = [0.91, 0.18, 0.02, 0.6]
        self.sub_poss = ["left", "right"]

    def _add_china_shp(self, ax):
        hyd1 = ShapelyFeature(Reader('{}/hyd1_4l.shp'.format(self.shp_folder)).geometries(),
                              ccrs.PlateCarree())
        ax.add_feature(hyd1, facecolor='None', edgecolor="blue", linewidth=0.1, zorder=1)

        bou1 = ShapelyFeature(Reader('{}/bou1_4l.shp'.format(self.shp_folder)).geometries(),
                              ccrs.PlateCarree())
        ax.add_feature(bou1, facecolor='None', edgecolor="#404040", linewidth=0.8, zorder=1)

        province = ShapelyFeature(
            Reader('{}/province_l.shp'.format(self.shp_folder)).geometries(),
            ccrs.PlateCarree())
        ax.add_feature(province, facecolor='None', edgecolor="#111111", linewidth=0.4, zorder=1)

    def _add_sub_nine_dashed_line(self, sub_pos="left", land_color="#ffffff", ocean_color="#aadaff", sub_offset_y=0):
        if sub_pos not in self.sub_poss:
            raise Exception(str(self.sub_poss))
        pos1 = self.ax.get_position()
        sub_nine_extent = [pos1.x0, pos1.y0 + sub_offset_y, 0.1, 0.20]
        if sub_pos == "right":
            sub_nine_extent = [pos1.x1 - 0.1, pos1.y0, 0.1, 0.20]
        sub_ax = self.fig.add_axes(sub_nine_extent, projection=ccrs.PlateCarree())
        self._add_china_shp(sub_ax)
        sub_ax.add_feature(c_feature.OCEAN.with_scale('110m'), facecolor=ocean_color)
        sub_ax.add_feature(c_feature.LAND.with_scale('110m'), facecolor=land_color)
        sub_ax.set_extent([105, 125, 0, 25])

    def _draw_world_map(self, resolution="110m", ocean_color="#aadaff", land_color="#ffffff", lakes_color="#aadaff",
                        add_world_countries=True):
        self.ax.add_feature(c_feature.OCEAN.with_scale(resolution), lw=0.4, facecolor=ocean_color, zorder=-1)
        self.ax.add_feature(c_feature.LAND.with_scale(resolution), lw=0.4, facecolor=land_color, zorder=-1)
        self.ax.add_feature(c_feature.LAKES.with_scale(resolution), facecolor=lakes_color, zorder=-1)

        all_countries = ShapelyFeature(
            Reader('{}/{}/World_Countries.shp'.format(self.shp_folder, "shp_glb"), ).geometries(),
            ccrs.PlateCarree())
        self.ax.add_feature(all_countries, facecolor='None', edgecolor="blue", linewidth=0.4, zorder=1)

    def set_left_and_right_text_and_title(self, title, left_text, right_text):
        self.set_title(title, y=1.05)
        self.set_text(0, 1.01, left_text)
        self.set_text(0.78, 1.01, right_text)

    def _set_x_y_axis(self):
        self.ax.set_xticks(self.x_ticks, crs=ccrs.PlateCarree())
        self.ax.set_yticks(self.y_ticks, crs=ccrs.PlateCarree())
        self.ax.tick_params(labelcolor='#2b2b2b', labelsize=10, width=0.5, top=False, right=False)
        # zero_direction_label用来设置经度的0度加不加E和W
        lon_formatter = LongitudeFormatter(zero_direction_label=False)
        lat_formatter = LatitudeFormatter()
        self.ax.xaxis.set_major_formatter(lon_formatter)
        self.ax.yaxis.set_major_formatter(lat_formatter)

    def set_title(self, title=None, y=0.75, family="helvetica"):
        font_family = {
            "size": 24,
        }
        if title is not None:
            self.ax.set_title(title, zorder=0, y=y, fontdict=font_family)

    def add_one_or_multi_province(self, add_china_shp=True, add_world_shp=True,
                                  add_sub_nine_dashed=True, sub_pos="left", resolution="110m", ocean_color="#aadaff",
                                  land_color="#ffffff",
                                  lakes_color="#aadaff", sub_offset_y=0, add_terrain=False, add_world_countries=True):
        if self.region not in CONF.keys():
            self._set_x_y_axis()
        self.ax.plot([116.39], [39.9], markersize=10, marker="*", c="red", transform=ccrs.PlateCarree())
        if add_china_shp:
            self._add_china_shp(self.ax)

        if add_world_shp:
            self._draw_world_map(resolution=resolution, ocean_color=ocean_color, land_color=land_color,
                                 lakes_color=lakes_color, add_world_countries=add_world_countries)

        if add_terrain:
            self.add_terrain()

        if add_sub_nine_dashed:
            self._add_sub_nine_dashed_line(sub_pos=sub_pos, ocean_color=ocean_color, land_color=land_color,
                                           sub_offset_y=sub_offset_y)

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
                    self.ax.add_feature(ShapelyFeature([china2["geometry"][index]], ccrs.PlateCarree()),
                                        facecolor='None',
                                        edgecolor="#111111", linewidth=0.8)

    def _mask_out(self, cf, proj=None):

        if self.shp_idx is not None:
            sf = shapefile.Reader("{}/all_full/all.shp".format(self.shp_folder))

            if self.china_bool:
                sf = shapefile.Reader("{}/all/all.shp".format(self.shp_folder))

            vertices = []
            codes = []
            for shape_rec in sf.shapeRecords():
                code = shape_rec.record.adcode
                name = shape_rec.record.name

                if not self.china_bool:
                    _bool = False
                    for _n in self.shp_idx:
                        if _n == name or _n == code or _n in name:
                            _bool = True

                    if not _bool:
                        continue
                pts = shape_rec.shape.points
                prt = list(shape_rec.shape.parts) + [len(pts)]
                for i in range(len(prt) - 1):
                    for j in range(prt[i], prt[i + 1]):
                        if proj:
                            vertices.append(proj.transform_point(pts[j][0], pts[j][1], ccrs.Geodetic()))
                        else:
                            vertices.append((pts[j][0], pts[j][1]))
                    codes += [Path.MOVETO]
                    codes += [Path.LINETO] * (prt[i + 1] - prt[i] - 2)
                    codes += [Path.CLOSEPOLY]
                clip = Path(vertices, codes)
                clip = PathPatch(clip, transform=self.ax.transData)

            for contour in cf.collections:
                contour.set_clip_path(clip)

    def add_logo(self, x=250, y=2450):
        img = Image.open('./plot/logo.png')
        img.thumbnail((300, 300), Image.ANTIALIAS)
        self.fig.figimage(img, xo=x, yo=y, zorder=3)

    def add_color_bar(self, colors=None, levels=None, color_bar_label=None, extend='both', bar_bounds_name=None,
                      axes=None, cmap_f=None, orientation="vertical"):

        if axes is None:
            pos1 = self.ax.get_position()
            _height = pos1.height / 3 * 2
            _width = pos1.width / 4 * 3
            axes = [pos1.x1 + 0.02, pos1.y0 + (pos1.height - _height) / 2, 0.02, _height]
            if orientation == "horizontal":
                axes = [pos1.x0 + (pos1.width - _width) / 2, pos1.y0 - 0.06, _width, 0.02]

        ax2 = self.fig.add_axes(axes)
        new_level = np.array(levels)
        if cmap_f is not None:
            cmap = plt.get_cmap(cmap_f)
        else:
            new_color = np.array(colors)

            cmap = mpl.colors.ListedColormap(new_color)
            if extend == "both":
                # new_color = new_color[1:-1]
                # new_level = new_level[1:-1]
                cmap = mpl.colors.ListedColormap(new_color)
                # cmap.set_over(colors[len(colors) - 1])
                # cmap.set_under(colors[0])

            if extend == "min":
                new_color = new_color[1:]
                new_level = new_level[1:]
                cmap = mpl.colors.ListedColormap(new_color)
                cmap.set_under(colors[0])

            if extend == "max":
                new_color = new_color[0:-1]
                new_level = new_level[0:-1]
                cmap = mpl.colors.ListedColormap(new_color)
                cmap.set_over(colors[len(colors) - 1])

        bounds = new_level

        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
        cb2 = mpl.colorbar.ColorbarBase(ax2, cmap=cmap,
                                        norm=norm,
                                        boundaries=bounds,
                                        extend=extend,
                                        extendfrac='auto',
                                        orientation=orientation,
                                        ticks=bounds)
        if color_bar_label is not None:
            cb2.set_label(color_bar_label, labelpad=-0.1)

        if bar_bounds_name is not None:
            loc = []
            for idx in range(len(levels) - 1):
                loc.append(np.nanmean([levels[idx], levels[idx + 1]]))
            cb2.locator = mpl.ticker.FixedLocator(loc)
            cb2.formatter = mpl.ticker.FixedFormatter(bar_bounds_name)
            cb2.update_ticks()

    def add_contourf(self, longs, lats, data, levels, colors=None, extend="both",
                     add_color_bar=True, if_mask_out=False, save_file=None, cmap=None, color_bar_label=None):

        if cmap is not None:
            cf = self.ax.contourf(longs, lats, data, levels=levels, cmap=cmap, extend=extend, zorder=0,
                                  transform=ccrs.PlateCarree())

        else:

            cf = self.ax.contourf(longs, lats, data, levels=levels, colors=colors, extend=extend, zorder=0,
                                  transform=ccrs.PlateCarree())

        if add_color_bar:
            self.add_color_bar(colors, levels, color_bar_label, extend=extend, cmap_f=cmap)

        if if_mask_out:
            self.mask_out_glb(cf, proj=ccrs.PlateCarree())

        if save_file is not None:
            self.save_fig(save_file)

    def add_plot(self, _x, _y, marker="o", ls="-", ms=2, c="black"):
        self.ax.plot(_x, _y, marker=marker, ls=ls, ms=ms, color=c, lw=1, transform=ccrs.PlateCarree())

    def add_wind_bar(self, lons, lats, u, v, save_file=None, length=4.8, barb_color="blue",
                     flag_color="#111111"):
        xr_data = xr.Dataset({"u": (['lat', 'lon'], u), "v": (['lat', 'lon'], v)}, coords={"lat": lats, "lon": lons})
        num_x = 48
        num_y = 24

        scale_x = (self.extent[1] - self.extent[0]) / num_x / ((self.extent[1] - self.extent[0]) / num_x)
        scale_y = (abs(self.extent[3] - self.extent[2])) / num_y / ((self.extent[3] - self.extent[2]) / num_y)

        new_num_x = int(num_x * scale_x)
        new_num_y = int(num_y * scale_y)
        new_lon, new_lat = np.linspace(lons[0], lons[-1], new_num_x), np.linspace(lats[0], lats[-1], new_num_y)

        new_data = xr_data.interp(lat=new_lat, lon=new_lon)
        new_lon, new_lat = np.meshgrid(new_lon, new_lat)
        flip_barb = np.empty(new_lon.shape)
        flip_barb[:, :] = False
        flip_barb[new_lat <= 0] = True
        # 0度以下，翻转
        self.ax.barbs(new_lon, new_lat, new_data["u"].values,
                      new_data["v"].values, length=length, barbcolor=barb_color, transform=ccrs.PlateCarree(),
                      barb_increments=dict(half=2, full=4, flag=20),
                      flagcolor=flag_color, rounding=False,
                      sizes=dict(emptybarb=0, height=0.45, spacing=0.25, linewidth=0.01),
                      flip_barb=flip_barb)
        if save_file is not None:
            self.save_fig(save_file)

    def add_marker(self, pd_data, levels, colors, save_file=None, func=None, value_key="value", marker="o",
                   markerSize=6):
        _l = 1
        if colors[0] == "#ffffff":
            _l = 2

        for idx in range(_l, len(levels)):
            _tmp_data = pd_data[(pd_data[value_key] >= levels[idx - 1]) & (pd_data[value_key] < levels[idx])]
            self.ax.scatter(_tmp_data.lon,
                            _tmp_data.lat,
                            marker=marker,
                            edgecolor=colors[idx - 1],
                            linewidth=0.5, s=markerSize, alpha=1, c=colors[idx - 1], transform=ccrs.PlateCarree(),
                            zorder=99)

        if func is not None:
            func(self.ax)

        if save_file is not None:
            self.save_fig(save_file)

    def add_contour(self, lons, lats, data, levels, colors, save_file=None, if_mask_out=False, fontcolor="black",
                    fontsize=8,
                    **kwargs):
        CS = self.ax.contour(lons, lats, data, levels=levels, colors=colors,
                             transform=ccrs.PlateCarree(), **kwargs)

        if if_mask_out:
            self.mask_out_glb(CS)

        self.ax.clabel(CS, inline=0.02, fontsize=fontsize, colors=[fontcolor], fmt="%.2f")

        if save_file is not None:
            self.save_fig(save_file)

    def set_text(self, x, y, text, size=16):
        font_family = {
            "size": size,
        }
        self.ax.text(x, y, text, transform=self.ax.transAxes, fontdict=font_family)

    def set_text_for_map(self, pd_data: pd.DataFrame, value_key=None, font_size=3, font_color="blue", offset_x=0.15,
                         offset_y=0, ):
        font_family = {
            "size": font_size,
            "color": font_color,
        }
        for idx in range(len(pd_data.lat)):
            f_one = pd_data.iloc[idx]
            text = ""
            for val in value_key:
                text = "{},{}".format(text, f_one[val])
            self.ax.text(f_one.lon + offset_x, f_one.lat + offset_y, text[1:],
                         transform=ccrs.PlateCarree(),
                         fontdict=font_family)

    def save_fig(self, save_file):
        from os import path, makedirs
        if not path.exists(path.dirname(save_file)):
            makedirs(path.dirname(save_file))
        self.fig.savefig(save_file, bbox_inches="tight", pad_inches=0.15)

    def __del__(self):
        plt.close(self.fig)
        # self.fig.clf()

    def add_more_color_bar(self, param, gap=0.01, scale=9):
        pos1 = self.ax.get_position()
        all_height = pos1.height / 10 * scale
        _height = all_height / len(param)
        for idx, par in enumerate(param):
            axes = [pos1.x1 + 0.02, (pos1.y0 + (pos1.height - all_height) / 2) + _height * idx + gap, 0.02,
                    _height - gap]
            extend = "both"
            color_bar_label = None
            bar_bounds_name = None
            if "extend" in par.keys():
                extend = par["extend"]
            if "color_bar_label" in par.keys():
                color_bar_label = par["color_bar_label"]
            if "bar_bounds_name" in par.keys():
                bar_bounds_name = par["bar_bounds_name"]
            self.add_color_bar(par["colors"], par["levels"], color_bar_label=color_bar_label, extend=extend,
                               bar_bounds_name=bar_bounds_name, axes=axes)

    def run_func(self, func, kwargs):
        if func is None:
            raise Exception("func can not is None")

        func(self.ax, self.fig, plt, ccrs, kwargs)

    def mask_out_glb(self, cf, proj=None):

        sf = shapefile.Reader("{}/shp_glb/World_Countries.shp".format(self.shp_folder))
        vertices = []
        codes = []
        for shape_rec in sf.shapeRecords():
            country = shape_rec.record.COUNTRY
            pts = shape_rec.shape.points
            bbox = shape_rec.shape.bbox
            noc = "Israel, Lebanon, Syria, Iraq, Iran, Kuwait, UNITED Arab Emirates, Qatar, Saudi Arabia, Yemen,Bahrain, Oman, Afghanistan, Cyprus,Jordan,Greece,Azerbaijan,United Arab Emirates"
            # if country.strip() == "Saudi Arabia" or country.strip() == "Syria" or country.strip() == "Yemen" or country.strip() == "Iran" or country.strip() == "Afghanistan":
            #     continue
            #             # if country in noc:
            #             #     continue
            prt = list(shape_rec.shape.parts) + [len(pts)]
            print(country)
            for i in range(len(prt) - 1):
                for j in range(prt[i], prt[i + 1]):
                    lon = pts[j][0]

                    if proj:
                        vertices.append(proj.transform_point(lon, pts[j][1], ccrs.Geodetic()))
                    else:
                        vertices.append((lon, pts[j][1]))
                codes += [Path.MOVETO]
                codes += [Path.LINETO] * (prt[i + 1] - prt[i] - 2)
                codes += [Path.CLOSEPOLY]

        clip = Path(vertices, codes)
        clip = PathPatch(clip, transform=self.ax.transData)
        for contour in cf.collections:
            contour.set_clip_path(clip)
