# -- coding: utf-8 --
# @Time : 2023/5/16 11:19
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : plot.py
# @Software: PyCharm
import sys
import os
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LatitudeFormatter, LongitudeFormatter
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from config_ptype import *
import meteva.base as meb
import matplotlib as mpl
import cartopy.feature as cf
from matplotlib import font_manager
from datetime import datetime, timedelta
from cartopy.io.shapereader import Reader
import matplotlib.colors as colors
from pathlib import Path
font_manager.fontManager.addfont(os.path.join(os.path.dirname(__file__), 'simhei.ttf'))
plt.rcParams.update({
    'font.family': 'simhei',
    'font.sans-serif': 'Times New Roman',
    })
plt.rcParams['axes.unicode_minus']=False
cmp = colors.ListedColormap(cmap_obs)
norm = colors.BoundaryNorm(ticks, cmp.N)
cmp_nafp = colors.ListedColormap(cmap_nafp)
norm_nafp = colors.BoundaryNorm(levels, cmp_nafp.N)
cmp_nafp_sta = colors.ListedColormap(cmap_sta)
norm_nafp_sta = colors.BoundaryNorm(levels_sta, cmp_nafp_sta.N)


def plot_sta(plot_dict, outpath, model, fst_time, cst):
    fig, axes = plt.subplots(nrows=2, ncols=3, subplot_kw=dict(projection=ccrs.PlateCarree(), aspect='auto'), figsize=(16, 8))
    plt.suptitle('实况与{}站点相态概率'.format(model), fontsize=20, y=1, font=Path('./simhei.ttf'))
    fig.text(x=0.5, y=0.93, s='\n{rp_t:%Y-%m-%d %H:00} +{cst:03d}H UTC'.format(rp_t=fst_time, cst=cst), fontsize=16, ha='center')
    # 标注坐标轴
    china_reader, worldmap_reader, coastline_reader = Reader(china_shp), Reader(worldmap_shp), Reader(coastline_shp)
    china = cf.ShapelyFeature(china_reader.geometries(), ccrs.PlateCarree(), edgecolor='grey', facecolor='none')
    worldmap = cf.ShapelyFeature(worldmap_reader.geometries(), ccrs.PlateCarree(), edgecolor='grey', facecolor='none')
    coastline = cf.ShapelyFeature(coastline_reader.geometries(), ccrs.PlateCarree(), edgecolor='grey', facecolor='none')

    for i, ax in zip(np.arange(0, 2 * 3), axes.flat):
        #设置显示范围
        box = [70, 140, 10,60]
        ax.set_xticks(np.arange(box[0], box[1] + step, step))
        ax.set_yticks(np.arange(box[2], box[3] + step, step))
        ax.set_extent(box, crs=ccrs.PlateCarree())
        ax.set_title(title_name[i], font=Path('./simhei.ttf'))
        #设置坐标轴
        lon_formatter = LongitudeFormatter(zero_direction_label=False)
        lat_formatter = LatitudeFormatter()
        ax.xaxis.set_major_formatter(lon_formatter)
        ax.yaxis.set_major_formatter(lat_formatter)

        # 添加数据
        if i < 1:
            ax.scatter(plot_dict['obs_lon'], plot_dict['obs_lat'], marker='.', s=1, c=plot_dict['obs_data'], cmap=cmp, norm=norm)

        else:
            ax.scatter(plot_dict['NAFP_lon'], plot_dict['NAFP_lat'], marker='.', s=1, c=plot_dict['prob'+str(i-1)], cmap=cmp_nafp, norm=norm_nafp)

        #添加边界
        ax.add_feature(china, linewidth=0.6)
        ax.add_feature(worldmap, linewidth=0.6)
        ax.add_feature(coastline, linewidth=0.6)

    local_obs = fig.add_axes([0.125, 0.05, 0.35, 0.02])
    im = mpl.cm.ScalarMappable(norm=norm, cmap=cmp)
    cs = fig.colorbar(im, cax=local_obs, aspect=50, pad=0.08, orientation='horizontal', extend='neither', ticks=ticks)
    cs.set_label('实况', font=Path('./simhei.ttf'))
    cs.ax.set_xticks(cb_ticks)
    cs.ax.set_xticklabels(tick_label, ha="center")

    local_nafp = fig.add_axes([0.55, 0.05, 0.35, 0.02])
    im_nafp = mpl.cm.ScalarMappable(norm=norm_nafp, cmap=cmp_nafp)
    cs = fig.colorbar(im_nafp, cax=local_nafp, aspect=50, pad=0.08, orientation='horizontal', extend='neither', extendfrac='auto')
    cs.set_label('站点相态概率', font=Path('./simhei.ttf'))

    #fig.subplots_adjust(hspace=0.5, wspace=0.5)
    if not os.path.exists(os.path.dirname(outpath)):
        os.makedirs(os.path.dirname(outpath))
    plt.savefig(outpath, bbox_inches='tight', dpi=300)
    print('成功输出至' + outpath)

def plot_hrd(plot_dict, outpath, model, fst_time, cst):
    fig, axes = plt.subplots(nrows=1, ncols=2, subplot_kw=dict(projection=ccrs.PlateCarree(), aspect='auto'), figsize=(16, 6))
    plt.suptitle('实况与{}确定性预报站点相态对比'.format(model), fontsize=20, y=1.01, font=Path('./simhei.ttf'))
    fig.text(x=0.5, y=0.94, s='\n{rp_t:%Y-%m-%d %H:00} +{cst:03d}H UTC'.format(rp_t=fst_time, cst=cst), fontsize=16, ha='center')
    # 标注坐标轴
    china_reader, worldmap_reader, coastline_reader = Reader(china_shp), Reader(worldmap_shp), Reader(coastline_shp)
    china = cf.ShapelyFeature(china_reader.geometries(), ccrs.PlateCarree(), edgecolor='grey', facecolor='none')
    worldmap = cf.ShapelyFeature(worldmap_reader.geometries(), ccrs.PlateCarree(), edgecolor='grey', facecolor='none')
    coastline = cf.ShapelyFeature(coastline_reader.geometries(), ccrs.PlateCarree(), edgecolor='grey', facecolor='none')

    for i, ax in zip(np.arange(0, 1 * 2), axes.flat):
        #设置显示范围
        box = [70, 140, 10,60]
        ax.set_xticks(np.arange(box[0], box[1] + step, step))
        ax.set_yticks(np.arange(box[2], box[3] + step, step))
        ax.set_extent(box, crs=ccrs.PlateCarree())
        ax.set_title(title_name_hrd[i], font=Path('./simhei.ttf'))
        #设置坐标轴
        lon_formatter = LongitudeFormatter(zero_direction_label=False)
        lat_formatter = LatitudeFormatter()
        ax.xaxis.set_major_formatter(lon_formatter)
        ax.yaxis.set_major_formatter(lat_formatter)

        # 添加数据
        if i < 1:
            ax.scatter(plot_dict['obs_lon'], plot_dict['obs_lat'], marker='.', s=1, c=plot_dict['obs_data'], cmap=cmp, norm=norm)
        else:
            ax.scatter(plot_dict['NAFP_lon'], plot_dict['NAFP_lat'], marker='.', s=1, c=plot_dict['NAFP_data'], cmap=cmp_nafp_sta, norm=norm_nafp_sta)

        #添加边界
        ax.add_feature(china, linewidth=0.6)
        ax.add_feature(worldmap, linewidth=0.6)
        ax.add_feature(coastline, linewidth=0.6)

    local_obs = fig.add_axes([0.125, 0.04, 0.35, 0.02])
    im = mpl.cm.ScalarMappable(norm=norm, cmap=cmp)
    cs = fig.colorbar(im, cax=local_obs, aspect=50, orientation='horizontal', extend='neither', ticks=ticks)
    # cs.set_label('实况')
    cs.ax.set_xticks(cb_ticks)
    cs.ax.set_xticklabels(tick_label, ha="center", font=Path('./simhei.ttf'))

    local_nafp = fig.add_axes([0.55, 0.04, 0.35, 0.02])
    im_nafp = mpl.cm.ScalarMappable(norm=norm_nafp_sta, cmap=cmp_nafp_sta)
    cs = fig.colorbar(im_nafp, cax=local_nafp, aspect=50, orientation='horizontal', extend='neither', extendfrac='auto')
    # cs.set_label('预报站点相态概率')
    cs.ax.set_xticks(cb_levels)
    cs.ax.set_xticklabels(levels_label, ha="center", font=Path('./simhei.ttf'))

    if not os.path.exists(os.path.dirname(outpath)):
        os.makedirs(os.path.dirname(outpath))
    plt.savefig(outpath, bbox_inches='tight', dpi=300)
    print('成功输出至' + outpath)

def plot_grid(plot_dict, outpath, model, fst_time, cst):
    fig, axes = plt.subplots(nrows=2, ncols=3, subplot_kw=dict(projection=ccrs.PlateCarree(), aspect='auto'), figsize=(16, 8))
    plt.suptitle('实况与{model}格点相态概率'.format(model=model), fontsize=20, y=1, font=Path('./simhei.ttf'))
    fig.text(x=0.5, y=0.93, s='\n{rp_t:%Y-%m-%d %H:00} +{cst:03d}H UTC'.format(rp_t=fst_time, cst=cst), fontsize=16, ha='center')
    # 标注坐标轴
    china_reader, worldmap_reader, coastline_reader = Reader(china_shp), Reader(worldmap_shp), Reader(coastline_shp)
    china = cf.ShapelyFeature(china_reader.geometries(), ccrs.PlateCarree(), edgecolor='grey', facecolor='none')
    worldmap = cf.ShapelyFeature(worldmap_reader.geometries(), ccrs.PlateCarree(), edgecolor='grey', facecolor='none')
    coastline = cf.ShapelyFeature(coastline_reader.geometries(), ccrs.PlateCarree(), edgecolor='grey', facecolor='none')

    for i, ax in zip(np.arange(0, 2 * 3), axes.flat):
        #设置显示范围
        box = [np.min(plot_dict['NAFP_lon']), np.max(plot_dict['NAFP_lon']),
               np.min(plot_dict['NAFP_lat']), np.max(plot_dict['NAFP_lat'])]
        ax.set_xticks(np.arange(box[0], box[1] + step, step))
        ax.set_yticks(np.arange(box[2], box[3] + step, step))
        ax.set_extent(box, crs=ccrs.PlateCarree())
        ax.set_title(title_name[i], font=Path('./simhei.ttf'))
        #设置坐标轴
        lon_formatter = LongitudeFormatter(zero_direction_label=False)
        lat_formatter = LatitudeFormatter()
        ax.xaxis.set_major_formatter(lon_formatter)
        ax.yaxis.set_major_formatter(lat_formatter)

        # 添加数据
        if i < 1:
            ax.scatter(plot_dict['obs_lon'], plot_dict['obs_lat'], marker='.', s=2, c=plot_dict['obs_data'], cmap=cmp, norm=norm)

        else:
            ax.contourf(plot_dict['NAFP_lon'], plot_dict['NAFP_lat'], plot_dict['NAFP_grd'+str(i-1)], colors=tuple(cmap_nafp), levels=levels)

        #添加边界
        ax.add_feature(china, linewidth=0.6)
        ax.add_feature(worldmap, linewidth=0.6)
        ax.add_feature(coastline, linewidth=0.6)

    local_obs = fig.add_axes([0.125, 0.05, 0.35, 0.02])
    im = mpl.cm.ScalarMappable(norm=norm, cmap=cmp)
    cs = fig.colorbar(im, cax=local_obs, aspect=50, pad=0.08, orientation='horizontal', extend='neither', ticks=ticks)
    cs.set_label('实况', font=Path('./simhei.ttf'))
    cs.ax.set_xticks(cb_ticks)
    cs.ax.set_xticklabels(tick_label, ha="center", font=Path('./simhei.ttf'))

    local_nafp = fig.add_axes([0.55, 0.05, 0.35, 0.02])
    cmp_nafp = colors.ListedColormap(cmap_nafp)
    norm_nafp = colors.BoundaryNorm(levels, cmp.N-1)
    im_nafp = mpl.cm.ScalarMappable(norm=norm_nafp, cmap=cmp_nafp)
    cs = fig.colorbar(im_nafp, cax=local_nafp, aspect=50, pad=0.08, orientation='horizontal', extend='neither', extendfrac='auto')
    cs.set_label('格点相态概率', font=Path('./simhei.ttf'))

    #fig.subplots_adjust(hspace=0.5, wspace=0.5)
    if not os.path.exists(os.path.dirname(outpath)):
        os.makedirs(os.path.dirname(outpath))
    plt.savefig(outpath, bbox_inches='tight', dpi=300)
    print('成功输出至' + outpath)

def gain_sta(fst_time, fst_h, model):
    obs_time = fst_time + timedelta(hours=fst_h)
    obsfile = land_obs6.format(rp_T=obs_time)
    if model == 'C3E':
        NAFP_file = c3e_Ppt1.format(rp_T=fst_time, cst=fst_h)
        outpath = NAFP_png.format(rp_T=fst_time, cst=fst_h, model=model, model_type='Ppt1')
    else:
        NAFP_file = c1d_Ppt2.format(rp_T=fst_time, cst=fst_h)
        outpath = NAFP_png.format(rp_T=fst_time, cst=fst_h, model=model, model_type='Ppt2')

    if os.path.exists(obsfile) and os.path.exists(NAFP_file):
        plot_dict = dict()
        obs_sta = meb.read_stadata_from_micaps3(obsfile)
        NAFP_df = pd.read_csv(NAFP_file)
        plot_dict['obs_lon'] = obs_sta.lon.to_list()
        plot_dict['obs_lat'] = obs_sta.lat.to_list()
        plot_dict['obs_data'] = obs_sta.data0.to_list()
        plot_dict['NAFP_lon'] = NAFP_df.get('lon').to_list()
        plot_dict['NAFP_lat'] = NAFP_df.get('lat').to_list()
        for i in range(5):
            key_name = 'prob' + str(i)
            plot_dict[key_name] = NAFP_df.get(key_name).to_list()
        return plot_dict, outpath
    else:
        return None, None

def gain_grid(fst_time, fst_h, model):
    obs_time = fst_time + timedelta(hours=fst_h)
    obsfile = land_obs6.format(rp_T=obs_time)
    if model == 'C3E':
        NAFP_file = c3e_pt1.format(rp_T=fst_time, cst=fst_h)
        outpath = NAFP_png.format(rp_T=fst_time, cst=fst_h, model=model, model_type='pt1')
    else:
        NAFP_file = c1d_pt2.format(rp_T=fst_time, cst=fst_h)
        outpath = NAFP_png.format(rp_T=fst_time, cst=fst_h, model=model, model_type='pt2')

    if os.path.exists(obsfile) and os.path.exists(NAFP_file):
        plot_dict = dict()
        obs_sta = meb.read_stadata_from_micaps3(obsfile)
        NAFP_grid = meb.read_griddata_from_nc(NAFP_file)
        plot_dict['obs_lon'] = obs_sta.lon.to_list()
        plot_dict['obs_lat'] = obs_sta.lat.to_list()
        plot_dict['obs_data'] = obs_sta.data0.to_list()
        plot_dict['NAFP_lon'] = NAFP_grid.lon.to_numpy()
        plot_dict['NAFP_lat'] = NAFP_grid.lat.to_numpy()
        for i in range(5):
            key_name = 'NAFP_grd' + str(i)
            plot_dict[key_name] = meb.in_level_list(NAFP_grid, [i]).data[0][0][0][0]
        return plot_dict, outpath
    else:
        return None, None

def gain_hrd(fst_time, fst_h, model):
    obs_time = fst_time + timedelta(hours=fst_h)
    obsfile = land_obs6.format(rp_T=obs_time)
    NAFP_file = c1d_Ppt2_sta.format(rp_T=fst_time, cst=fst_h)
    outpath = NAFP_png.format(rp_T=fst_time, cst=fst_h, model=model, model_type='Ppt2-sta')

    if os.path.exists(obsfile) and os.path.exists(NAFP_file):
        plot_dict = dict()
        obs_sta = meb.read_stadata_from_micaps3(obsfile)
        NAFP_sta = meb.read_stadata_from_micaps3(NAFP_file)
        plot_dict['obs_lon'] = obs_sta.lon.to_list()
        plot_dict['obs_lat'] = obs_sta.lat.to_list()
        plot_dict['obs_data'] = obs_sta.data0.to_list()
        plot_dict['NAFP_lon'] = NAFP_sta.lon.to_list()
        plot_dict['NAFP_lat'] = NAFP_sta.lat.to_list()
        plot_dict['NAFP_data'] = NAFP_sta.data0.to_list()
        return plot_dict, outpath
    else:
        return None, None

if __name__ == '__main__':
    #2023051000 EC HRD 3
    fst_time = datetime.strptime(sys.argv[1], '%Y%m%d%H')
    model = sys.argv[2]
    type = sys.argv[3]
    if len(sys.argv) == 4:
        fst_list = fst_h
    elif len(sys.argv) >= 5:
        fst_list = sys.argv[4:]
    else:
        fst_list = []

    for cst in fst_list:
        cst = int(cst)
        if type == 'GRID':
            plot_dict, outpath = gain_grid(fst_time, cst, model)
            if plot_dict is not None:
                plot_grid(plot_dict, outpath, model, fst_time, cst)
        elif type == 'STA':
            plot_dict, outpath = gain_sta(fst_time, cst, model)
            if plot_dict is not None:
                plot_sta(plot_dict, outpath, model, fst_time, cst)
        elif type == 'HRD' and model == 'C1D':
            plot_dict, outpath = gain_hrd(fst_time, cst, model)
            if plot_dict is not None:
                plot_hrd(plot_dict, outpath, model, fst_time, cst)
        else:
            print('类型参数错误')
