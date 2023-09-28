import logging
import os.path
import math
import matplotlib.pyplot as plt
import meteva.base as meb
import pandas as pd
from matplotlib.ticker import MultipleLocator
from metdig.cal import other
from verify.config_single import *
import metdig
from metpy.units import units
from metpy import calc as mp_calc
from verify.plot_model_single import horizontal_pallete_test
from datetime import datetime, timedelta
import numpy as np
from utils import MICAPS4 as M4
from metdig.graphics import draw_compose, contourf_method, pcolormesh_method
from verify.plot_model_single import PlotHgtWindProd_sg
import xarray as xr


# REGION_NAME = ["CHN", "NE", "HB", "HHJH", "JNHN", "XN", "NW"]
# REGION = [
#     [70, 140, 10, 60],
#     [110, 138, 35, 57],
#     [105, 125, 30, 47],
#     [104, 125, 26, 41],
#     [104, 125, 16, 33],
#     [92, 115, 20, 35],
#     [73, 123, 37, 50]
# ]
REGION_NAME = ["CHN"]
REGION = [
    [70, 140, 10, 60]
]
cmap_tp = ['#{:02x}{:02x}{:02x}'.format(*tuple(i)) for i in tp_color]
cmap_tp_hour = ['#{:02x}{:02x}{:02x}'.format(*tuple(i)) for i in tp_hour_color]
cmap_r = ['#{:02x}{:02x}{:02x}'.format(*tuple(i)) for i in r_color]
cmap_tem_change = ['#{:02x}{:02x}{:02x}'.format(*tuple(i)) for i in tem_change_color]
cmap_tem_min = ['#{:02x}{:02x}{:02x}'.format(*tuple(i)) for i in t2m_min_color]
cmap_exwind = ['#{:02x}{:02x}{:02x}'.format(*tuple(i)) for i in exwind_color]

path_GFS = os.path.join(os.path.dirname(__file__), "mask_NH25.dat")
path_Model = os.path.join(os.path.dirname(__file__), "mask_0p25.dat")
path_CLDAS = os.path.join(os.path.dirname(__file__), "mask_005.dat")

def creat_M4_grd(lon, lat, data_array):
    """
    构建m4标准格式
    :param Lon_list: 经度列表[起始经度，终止经度，经向间隔]
    :param Lat_list: 维度列表
    :param Data_list: 数据列表
    :return:
    """
    grid0 = meb.grid(lon, lat)
    data = data_array
    grd = meb.grid_data(grid0, data=data)
    meb.set_griddata_coords(grd, name="data0", level_list=[0], gtime=["2023-01-01:08"],
                            dtime_list=[1], member_list=["models"])
    return grd

def gain_tp_max(lat_lon_data, map_extent, lat_lon_dataarray):

    M4_grd_lon = [lat_lon_data.start_lon, lat_lon_data.end_lon, lat_lon_data.delt_lon]
    M4_grd_lat = [lat_lon_data.start_lat, lat_lon_data.end_lat, lat_lon_data.delt_lat]
    grd_roi = meb.grid([map_extent[0], map_extent[1], lat_lon_data.delt_lon],
                       [map_extent[2], map_extent[3], lat_lon_data.delt_lat])
    M4_grd = creat_M4_grd(M4_grd_lon, M4_grd_lat, lat_lon_dataarray)
    M4_grd_roi = meb.interp_gg_linear(M4_grd, grd_roi)
    index = np.nanargmax(np.squeeze(M4_grd_roi.data))
    lat_index, lon_index = divmod(index, np.squeeze(M4_grd_roi.data).shape[1])
    lon = map_extent[0] + lon_index * lat_lon_data.delt_lon
    lat = map_extent[2] + lat_index * lat_lon_data.delt_lat
    return M4_grd_roi, lon, lat

def calc_relative_humidity(t_data, d_data):
    """

    :param t_data: 单位：℃
    :param d_data:单位：℃
    :return:
    """
    return np.array(mp_calc.relative_humidity_from_dewpoint(t_data * units.degC, d_data * units.degC),
                    dtype=float) * 100

def createdir(arg_dir):
    import os
    if os.path.exists(arg_dir):
        print('file path exists: ' + arg_dir)
    else:
        os.makedirs(arg_dir)
        print('Create file path: ' + arg_dir)

def loss_data(file_path):
    name = os.path.split(file_path)[1][0:-4] + '.txt'
    outpath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'loss_data', 'error', name)
    if not os.path.exists(os.path.dirname(outpath)):
        os.makedirs(os.path.dirname(outpath))
    with open(outpath, 'a') as f:
        f.write(file_path)
        f.write('\r\n')
        f.close()

# 掩膜数据
def read_mask():
    if os.path.exists(path_Model):
        grd_mask = meb.read_griddata_from_micaps4(path_Model)
    else:
        grd_mask = None
    if os.path.exists(path_GFS):
        GFS_mask = meb.read_griddata_from_micaps4(path_GFS)
    else:
        GFS_mask = None
    if os.path.exists(path_CLDAS):
        grd_mask_cldas = meb.read_griddata_from_micaps4(path_CLDAS)
    else:
        grd_mask_cldas = None

    return GFS_mask.data[0][0][0][0], grd_mask.data[0][0][0][0], grd_mask_cldas[0][0][0][0]
GFS_mask, mask_array, mask_array_cldas = read_mask()
# UV风数据读取
def get_org_data(model_name: str, report_time, cst, element, lev, scale=1):
    if model_name == 'CLDAS':
        file_path = MODEL_ROOT_CLDAS.format(model=model_name, report_time=report_time, cst=cst, element=element,
                                            lev=lev)
        file_path = file_path.replace('2M_ABOVE_GROUND', '10M_ABOVE_GROUND')
        if not os.path.exists(file_path):
            loss_data(file_path)
            return None
        lats, lons, array_U, array_V = M4.open_m11_uv(file_path)
        array_U[mask_array_cldas == 0] = np.nan
        array_V[mask_array_cldas == 0] = np.nan
        array_U[array_U >= 90] = np.nan
        array_V[array_V >= 90] = np.nan
        array_U[array_U <= -90] = np.nan
        array_V[array_V <= -90] = np.nan

        if lev != "":
            xr_data_u = xr.DataArray([[[[array_U * scale]]]],
                                     coords=[[model_name.replace("_", "-")], [report_time], [cst], [int(lev)], lats,
                                             lons],
                                     dims=["member", "time", "dtime", "level", "lat", "lon"])
            xr_data_v = xr.DataArray([[[[array_V * scale]]]],
                                     coords=[[model_name.replace("_", "-")], [report_time], [cst], [int(lev)], lats,
                                             lons],
                                     dims=["member", "time", "dtime", "level", "lat", "lon"])
        else:
            xr_data_u = xr.DataArray([[[array_U * scale]]],
                                     coords=[[model_name.replace("_", "-")], [report_time], [cst], lats, lons],
                                     dims=["member", "time", "dtime", "lat", "lon"])
            xr_data_v = xr.DataArray([[[array_V * scale]]],
                                     coords=[[model_name.replace("_", "-")], [report_time], [cst], lats, lons],
                                     dims=["member", "time", "dtime", "lat", "lon"])

        return xr_data_u, xr_data_v, None, None
    else:
        file_path = MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element=element, lev=lev)
        if not os.path.exists(file_path):
            loss_data(file_path)
            return None
        lat_lon_data = M4.open_m4(file_path)
        if model_name == "CMA_GFS":
            mask = GFS_mask
        else:
            mask = mask_array
        lat_lon_data.data[mask == 0] = np.nan
        latitudes = np.linspace(lat_lon_data.start_lat, lat_lon_data.end_lat, lat_lon_data.lat_count)
        longitudes = np.linspace(lat_lon_data.start_lon, lat_lon_data.end_lon, lat_lon_data.lon_count)
        if lev != "":
            xr_data = xr.DataArray([[[[lat_lon_data.data * scale]]]],
                                   coords=[[model_name.replace("_", "-")], [report_time], [cst], [int(lev)], latitudes,
                                           longitudes],
                                   dims=["member", "time", "dtime", "level", "lat", "lon"])
        else:
            xr_data = xr.DataArray([[[lat_lon_data.data * scale]]],
                                   coords=[[model_name.replace("_", "-")], [report_time], [cst], latitudes, longitudes],
                                   dims=["member", "time", "dtime", "lat", "lon"])

        return xr_data

# 绘制单要素空间分布图
def metdig_single_plot(Infile_list, lat_lon_data, drw, data, cmap, extend='both'):
    lats = np.linspace(lat_lon_data.start_lat, lat_lon_data.end_lat, lat_lon_data.lat_count)
    lons = np.linspace(lat_lon_data.start_lon, lat_lon_data.end_lon, lat_lon_data.lon_count)
    xr_data = xr.DataArray(data, coords=(lats, lons), dims=("lat", "lon"))
    std_data = metdig.utl.xrda_to_gridstda(xr_data, level_dim='level', time_dim='time', lat_dim='lat',
                                           lon_dim='lon', dtime_dim='dtime',
                                           var_name=Infile_list[3], np_input_units=Infile_list[4])
    contourf_method.contourf_2d(drw.ax, std_data, levels=Infile_list[5], cb_label=Infile_list[3], extend=extend,
                                cmap=cmap, alpha=1, colorbar_kwargs={'pad': 0.06})

# 绘制单要素空间数值过滤分布图
def metdig_single_plot_filter(Infile_list, lat_lon_data, drw, data, cmap, extend='both'):
    lats = np.linspace(lat_lon_data.start_lat, lat_lon_data.end_lat, lat_lon_data.lat_count)
    lons = np.linspace(lat_lon_data.start_lon, lat_lon_data.end_lon, lat_lon_data.lon_count)
    xr_data = xr.DataArray(data, coords=(lats, lons), dims=("lat", "lon"))
    std_data = metdig.utl.xrda_to_gridstda(xr_data, level_dim='level', time_dim='time', lat_dim='lat',
                                           lon_dim='lon', dtime_dim='dtime',
                                           var_name=Infile_list[3], np_input_units=Infile_list[4])
    pcolormesh_method.pcolormesh_2d(drw.ax, std_data, levels=Infile_list[5], cb_label=Infile_list[3], extend=extend,
                                cmap=cmap, alpha=1, colorbar_kwargs={'pad': 0.06})
    # contourf_method.contourf_2d(drw.ax, std_data, levels=Infile_list[5], cb_label=Infile_list[3], extend=extend,
    #                             cmap=cmap, alpha=1, colorbar_kwargs={'pad': 0.06})

# 绘制单要素空间逐刻度标签分布图
def metdig_single_plot_temex(Infile_list, lat_lon_data, drw, data, cmap, extend='both'):
    lats = np.linspace(lat_lon_data.start_lat, lat_lon_data.end_lat, lat_lon_data.lat_count)
    lons = np.linspace(lat_lon_data.start_lon, lat_lon_data.end_lon, lat_lon_data.lon_count)
    xr_data = xr.DataArray(data, coords=(lats, lons), dims=("lat", "lon"))
    std_data = metdig.utl.xrda_to_gridstda(xr_data, level_dim='level', time_dim='time', lat_dim='lat',
                                           lon_dim='lon', dtime_dim='dtime',
                                           var_name=Infile_list[3], np_input_units=Infile_list[4])
    contourf_method.contourf_2d(drw.ax, std_data, levels=Infile_list[5], cb_label=Infile_list[3], extend=extend,
                                cb_ticks=Infile_list[5],
                                cmap=cmap, alpha=1, colorbar_kwargs={'pad': 0.06, 'tick_label': Infile_list[5]})

# 绘制极大风分布图
def metdig_exwind_plot(Infile_list, lat_lon_data, drw, data, cmap, extend):
    lats = np.linspace(lat_lon_data.start_lat, lat_lon_data.end_lat, lat_lon_data.lat_count)
    lons = np.linspace(lat_lon_data.start_lon, lat_lon_data.end_lon, lat_lon_data.lon_count)
    xr_data = xr.DataArray(data, coords=(lats, lons), dims=("lat", "lon"))
    std_data = metdig.utl.xrda_to_gridstda(xr_data, level_dim='level', time_dim='time', lat_dim='lat',
                                           lon_dim='lon', dtime_dim='dtime',
                                           var_name=Infile_list[3], np_input_units=Infile_list[4])
    contourf_method.contourf_2d(drw.ax, std_data, levels=Infile_list[5], cb_label=Infile_list[3], cb_ticks=[i+0.5 for i in Infile_list[5][:-1]],
                                extend=extend, cmap=cmap, alpha=1, colorbar_kwargs={'pad': 0.06, 'tick_label': Infile_list[5][1:]})

# 绘制多要素空间分布图
def metdig_multi_plot(Infile_list, lat_lon_data, drw, data_tp, data_sd, cmap):
    lats = np.linspace(lat_lon_data.start_lat, lat_lon_data.end_lat, lat_lon_data.lat_count)
    lons = np.linspace(lat_lon_data.start_lon, lat_lon_data.end_lon, lat_lon_data.lon_count)
    tp_data = np.full_like(data_tp, 0)
    sd_data = np.full_like(data_sd, 0)
    tp_data[data_tp >= 0.1] = 1.5
    tp_data[data_tp < 0.1] = 0
    sd_data[data_sd >= 0.1] = 2.5
    sd_data[data_sd < 0.1] = 0
    statistics_data = tp_data + sd_data
    xr_data = xr.DataArray(statistics_data, coords=(lats, lons), dims=("lat", "lon"))
    std_data = metdig.utl.xrda_to_gridstda(xr_data, level_dim='level', time_dim='time', lat_dim='lat',
                                           lon_dim='lon', dtime_dim='dtime', np_input_units=Infile_list[5])
    contourf_method.contourf_2d(drw.ax, std_data, levels=[0, 1, 2, 5], cb_label=Infile_list[4],
                                extend='neither', alpha=1, cb_ticks=[0.5, 1.5, 3.5],
                                cmap=cmap, colorbar_kwargs={'pad': 0.06, 'tick_label': ['无', '雨', '雪']})

def metdig_tp_sd_class(Infile_list, lat_lon_data, drw, data_tp, data_sd, cmap_tp, cmap_sd):
    lats = np.linspace(lat_lon_data.start_lat, lat_lon_data.end_lat, lat_lon_data.lat_count)
    lons = np.linspace(lat_lon_data.start_lon, lat_lon_data.end_lon, lat_lon_data.lon_count)
    xr_data_tp = xr.DataArray(data_tp, coords=(lats, lons), dims=("lat", "lon"))
    std_data_tp = metdig.utl.xrda_to_gridstda(xr_data_tp, level_dim='level', time_dim='time', lat_dim='lat',
                                              lon_dim='lon', dtime_dim='dtime', np_input_units=Infile_list[5])
    xr_data_sd = xr.DataArray(data_sd, coords=(lats, lons), dims=("lat", "lon"))
    std_data_sd = metdig.utl.xrda_to_gridstda(xr_data_sd, level_dim='level', time_dim='time', lat_dim='lat',
                                              lon_dim='lon', dtime_dim='dtime', np_input_units=Infile_list[5])
    contourf_method.contourf_2d(drw.ax, std_data_tp, levels=tp_colorbar, cb_label=' ',
                                extend='both', alpha=1, cmap=cmap_tp, colorbar_kwargs={'pad': 0.05})
    contourf_method.contourf_2d(drw.ax, std_data_sd, levels=sd_colorbar, cb_label=Infile_list[4],
                                extend='neither', alpha=1, cmap=cmap_sd, colorbar_kwargs={'pad': 0.1})

def single_model_tp(Infile_list, hour, is_overwrite):
    File_Name = os.path.split(Infile_list[0])[1]
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])
    try:
        obs_time, step_time = os.path.basename(Infile_list[0]).split('.')
        OBS_time = datetime.strptime(obs_time, '%Y%m%d%H')
        FST_time = OBS_time + timedelta(hours=int(step_time))
        obs_time_dc = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(OBS_time)
        fst_time_dc = '预报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(FST_time)
        forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时'.format(int(step_time))
        file_dir, file_name = os.path.split(Infile_list[0])
        if int(File_Name[-3:]) >= int(hour) and int(File_Name[-3:]) % 12 == 0:
            file_name_24 = '%.3f' % (float(file_name) - int(hour) / 1000)
            file_dir_24 = os.path.join(file_dir, str(file_name_24))

            lat_lon_data = M4.open_m4_org(Infile_list[0])
            if Infile_list[1].__contains__("NCEP"):
                if File_Name.split('.')[1] == '024':
                    lat_lon_data_24_data = np.zeros_like(lat_lon_data.data)
                else:
                    lat_lon_data_24_data = M4.open_m4_org(file_dir_24).data
            else:
                lat_lon_data_24_data = M4.open_m4_org(file_dir_24).data
            if Infile_list[1].__contains__("NCEP"):
                lat_lon_data_obs = (lat_lon_data.data - lat_lon_data_24_data) / 1000
            else:
                lat_lon_data_obs = lat_lon_data.data - lat_lon_data_24_data
            if Infile_list[1].__contains__("CMA_GFS"):
                mask = GFS_mask
            else:
                mask = mask_array
            lat_lon_data_obs[mask == 0] = np.nan
            for idx in range(len(REGION)):
                region_name, map_extent = REGION_NAME[idx], tuple(REGION[idx])
                if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
                    continue
                if region_name == 'CHN' or region_name == 'JNHN':
                    add_scs_value = True
                else:
                    add_scs_value = False
                fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                                  add_south_china_sea=add_scs_value)
                drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info,
                                                      add_tag=False,
                                                      output_dir=Infile_list[1], add_city=False, fig=fig, ax=ax,
                                                      is_clean_plt=True, map_extent=map_extent,
                                                      is_overwrite=is_overwrite,
                                                      png_name=region_name + '_' + File_Name + ".png")
                M4_grd_roi, lon, lat = gain_tp_max(lat_lon_data, map_extent, lat_lon_data_obs)
                notice_info = '最大降水:{0}mm 经度:{1}°E 纬度:{2}°N'.format(
                    '%.1f' % np.nanmax(np.squeeze(M4_grd_roi.data)),
                    '%.2f' % lon, '%.2f' % lat)
                ax.set_title(notice_info, loc='right', fontsize=16)
                drw.ax.tick_params(labelsize=16)
                metdig_single_plot(Infile_list, lat_lon_data, drw, lat_lon_data_obs, Infile_list[6])
                drw.save()
    except Exception as e:
        logging.info(e)

def single_model_tp_sd(Infile_list, hour, is_overwrite):
    File_Name = os.path.split(Infile_list[0])[1]
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])
    try:
        if Infile_list[1].__contains__("CMA_GFS"):
            mask = GFS_mask
        else:
            mask = mask_array
        obs_time, step_time = os.path.basename(Infile_list[0]).split('.')
        OBS_time = datetime.strptime(obs_time, '%Y%m%d%H')
        FST_time = OBS_time + timedelta(hours=int(step_time))
        obs_time_dc = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(OBS_time)
        fst_time_dc = '预报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(FST_time)
        forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时'.format(int(step_time))
        file_dir_tp, file_name_tp = os.path.split(Infile_list[0])
        file_dir_sd, file_name_sd = os.path.split(Infile_list[1])
        if int(File_Name[-3:]) >= int(hour) and int(File_Name[-3:]) % 12 == 0:
            file_name_24 = '%.3f' % (float(file_name_tp) - int(hour) / 1000)
            file_dir_24_tp = os.path.join(file_dir_tp, str(file_name_24))
            file_dir_24_sd = os.path.join(file_dir_sd, str(file_name_24))
            if os.path.exists(Infile_list[0]) and os.path.exists(Infile_list[1]) \
                    and os.path.exists(file_dir_24_tp) and os.path.exists(file_dir_24_sd):
                lat_lon_data_tp = M4.open_m4(Infile_list[0])
                lat_lon_data_24_tp = M4.open_m4(file_dir_24_tp)
                lat_lon_data_sd = M4.open_m4(Infile_list[1])
                lat_lon_data_24_sd = M4.open_m4(file_dir_24_sd)
                lat_lon_data_obs_sd = (lat_lon_data_sd.data - lat_lon_data_24_sd.data) * 1000
                if Infile_list[1].__contains__("NCEP"):
                    lat_lon_data_obs_tp = (lat_lon_data_tp.data - lat_lon_data_24_tp.data) / 1000
                else:
                    lat_lon_data_obs_tp = lat_lon_data_tp.data - lat_lon_data_24_tp.data
                lat_lon_data_obs_tp[mask == 0] = np.nan
                lat_lon_data_obs_sd[mask == 0] = np.nan
                for idx in range(len(REGION)):
                    region_name, map_extent = REGION_NAME[idx], tuple(REGION[idx])
                    if os.path.exists(Infile_list[2] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
                        continue
                    if region_name == 'CHN' or region_name == 'JNHN':
                        add_scs_value = True
                    else:
                        add_scs_value = False
                    fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                                      add_south_china_sea=add_scs_value)
                    drw = draw_compose.horizontal_compose(title=Infile_list[3], description=forcast_info,
                                                          add_tag=False, is_overwrite=is_overwrite,
                                                          output_dir=Infile_list[2], add_city=False, fig=fig, ax=ax,
                                                          is_clean_plt=True, map_extent=map_extent,
                                                          png_name=region_name + '_' + File_Name + ".png")
                    drw.ax.tick_params(labelsize=16)
                    metdig_multi_plot(Infile_list, lat_lon_data_tp, drw, lat_lon_data_obs_tp, lat_lon_data_obs_sd,
                                      Infile_list[6])
                    drw.save()
    except Exception as e:
        logging.info(e)


def single_model_tp_sd_class(Infile_list, hour, is_overwrite):
    File_Name = os.path.split(Infile_list[0])[1]
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])
    try:
        if Infile_list[1].__contains__("CMA_GFS"):
            mask = GFS_mask
        else:
            mask = mask_array
        obs_time, step_time = os.path.basename(Infile_list[0]).split('.')
        OBS_time = datetime.strptime(obs_time, '%Y%m%d%H')
        FST_time = OBS_time + timedelta(hours=int(step_time))
        obs_time_dc = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(OBS_time)
        fst_time_dc = '预报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(FST_time)
        forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时'.format(int(step_time))
        file_dir_tp, file_name_tp = os.path.split(Infile_list[0])
        file_dir_sd, file_name_sd = os.path.split(Infile_list[1])
        if int(File_Name[-3:]) >= int(hour) and int(File_Name[-3:]) % 12 == 0:
            file_name_24 = '%.3f' % (float(file_name_tp) - int(hour) / 1000)
            file_dir_24_tp = os.path.join(file_dir_tp, str(file_name_24))
            file_dir_24_sd = os.path.join(file_dir_sd, str(file_name_24))
            if os.path.exists(Infile_list[0]) and os.path.exists(Infile_list[1]) \
                    and os.path.exists(file_dir_24_tp) and os.path.exists(file_dir_24_sd):
                lat_lon_data_tp = M4.open_m4(Infile_list[0])
                lat_lon_data_24_tp = M4.open_m4(file_dir_24_tp)
                lat_lon_data_sd = M4.open_m4(Infile_list[1])
                lat_lon_data_24_sd = M4.open_m4(file_dir_24_sd)
                lat_lon_data_obs_sd = (lat_lon_data_sd.data - lat_lon_data_24_sd.data) * 1000
                if Infile_list[1].__contains__("NCEP"):
                    lat_lon_data_obs_tp = (lat_lon_data_tp.data - lat_lon_data_24_tp.data) / 1000
                else:
                    lat_lon_data_obs_tp = lat_lon_data_tp.data - lat_lon_data_24_tp.data
                lat_lon_data_obs_tp[mask == 0] = np.nan
                lat_lon_data_obs_sd[mask == 0] = np.nan
                for idx in range(len(REGION)):
                    region_name, map_extent = REGION_NAME[idx], tuple(REGION[idx])
                    if os.path.exists(Infile_list[2] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
                        continue
                    if region_name == 'CHN' or region_name == 'JNHN':
                        add_scs_value = True
                    else:
                        add_scs_value = False
                    fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                                      add_south_china_sea=add_scs_value)
                    drw = draw_compose.horizontal_compose(title=Infile_list[3], description=forcast_info,
                                                          add_tag=False, is_overwrite=is_overwrite,
                                                          output_dir=Infile_list[2], add_city=False, fig=fig, ax=ax,
                                                          is_clean_plt=True, map_extent=map_extent,
                                                          png_name=region_name + '_' + File_Name + ".png")
                    drw.ax.tick_params(labelsize=16)
                    metdig_tp_sd_class(Infile_list, lat_lon_data_tp, drw, lat_lon_data_obs_tp, lat_lon_data_obs_sd,
                                       Infile_list[6], Infile_list[7])
                    drw.save()
    except Exception as e:
        logging.info(e)


def single_model_Change(Infile_list, hour, step, is_overwrite):
    '变温/降雪/对流性/大尺度'
    File_Name = os.path.split(Infile_list[0])[1]
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])
    try:
        obs_time, step_time = os.path.basename(Infile_list[0]).split('.')
        OBS_time = datetime.strptime(obs_time, '%Y%m%d%H')
        FST_time = OBS_time + timedelta(hours=int(step_time))
        obs_time_dc = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(OBS_time)
        fst_time_dc = '预报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(FST_time)
        forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时'.format(int(step_time))
        file_dir, file_name = os.path.split(Infile_list[0])
        if int(File_Name[-3:]) >= int(hour) and int(File_Name[-3:]) % step == 0:
            file_name_24 = '%.3f' % (float(file_name) - int(hour) / 1000)
            file_dir_24 = os.path.join(file_dir, str(file_name_24))
            if os.path.exists(file_dir_24):
                lat_lon_data = M4.open_m4(Infile_list[0])
                lat_lon_data_24 = M4.open_m4(file_dir_24)
                lat_lon_data_obs = lat_lon_data.data - lat_lon_data_24.data
                if Infile_list[1].__contains__("CMA_GFS"):
                    mask = GFS_mask
                else:
                    mask = mask_array
                lat_lon_data_obs[mask == 0] = np.nan
                if '降雪' in Infile_list[2]:
                    lat_lon_data_obs = lat_lon_data_obs * 1000

                for idx in range(len(REGION)):
                    region_name, map_extent = REGION_NAME[idx], tuple(REGION[idx])
                    if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
                        continue
                    if region_name == 'CHN' or region_name == 'JNHN':
                        add_scs_value = True
                    else:
                        add_scs_value = False
                    fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                                      add_south_china_sea=add_scs_value)
                    drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info,
                                                          add_tag=False, is_overwrite=is_overwrite,
                                                          output_dir=Infile_list[1], add_city=False, fig=fig, ax=ax,
                                                          is_clean_plt=True, map_extent=map_extent,
                                                          png_name=region_name + '_' + File_Name + ".png")
                    if Infile_list[2].__contains__("降水"):
                        M4_grd_roi, lon, lat = gain_tp_max(lat_lon_data, map_extent, lat_lon_data_obs)
                        notice_info = '最大降水:{0}mm 经度:{1}°E 纬度:{2}°N'.format(
                            '%.1f' % np.nanmax(np.squeeze(M4_grd_roi.data)),
                            '%.2f' % lon, '%.2f' % lat)
                        ax.set_title(notice_info, loc='right', fontsize=16)
                    drw.ax.tick_params(labelsize=16)
                    metdig_single_plot_temex(Infile_list, lat_lon_data, drw, lat_lon_data_obs, Infile_list[6])
                    drw.save()
    except Exception as e:
        logging.info(e)

def single_model_tem_ex_High(Infile_list, hour):
    File_Name = os.path.split(Infile_list[0])[1]
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])
    try:
        obs_time, step_time = os.path.basename(Infile_list[0]).split('.')
        OBS_time = datetime.strptime(obs_time, '%Y%m%d%H')
        FST_time = OBS_time + timedelta(hours=int(step_time))
        obs_time_dc = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(OBS_time)
        fst_time_dc = '预报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(FST_time)
        forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时'.format(int(step_time))

        if os.path.exists(Infile_list[0]):
            lat_lon_data = M4.open_m4(Infile_list[0])
            if Infile_list[1].__contains__("CMA_GFS"):
                mask = GFS_mask
            else:
                mask = mask_array
            lat_lon_data.data[mask == 0] = np.nan
            for idx in range(len(REGION)):
                region_name, map_extent = REGION_NAME[idx], tuple(REGION[idx])
                if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png"):
                    continue
                else:
                    if region_name == 'CHN' or region_name == 'JNHN':
                        add_scs_value = True
                    else:
                        add_scs_value = False
                    fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                                      add_south_china_sea=add_scs_value)
                    drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info, add_tag=False,
                                                          output_dir=Infile_list[1], add_city=False, fig=fig, ax=ax,
                                                          is_clean_plt=True, map_extent=map_extent,
                                                          png_name=region_name + '_' + File_Name + ".png")
                    drw.ax.tick_params(labelsize=16)
                    metdig_single_plot(Infile_list, lat_lon_data, drw, lat_lon_data.data, Infile_list[6])
                    drw.save()
    except:
        print(File_Name)

def single_model_t2m_High(Infile_list, hour):
    File_Name = os.path.split(Infile_list[0])[1]
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])
    try:
        obs_time, step_time = os.path.basename(Infile_list[0]).split('.')
        OBS_time = datetime.strptime(obs_time, '%Y%m%d%H')
        FST_time = OBS_time + timedelta(hours=int(step_time))
        obs_time_dc = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(OBS_time)
        fst_time_dc = '预报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(FST_time)
        forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时'.format(int(step_time))

        if os.path.exists(Infile_list[0]):
            lat_lon_data = M4.open_m4(Infile_list[0])
            if Infile_list[1].__contains__("CMA_GFS"):
                mask = GFS_mask
            else:
                mask = mask_array
            lat_lon_data.data[mask == 0] = np.nan
            for idx in range(len(REGION)):
                region_name, map_extent = REGION_NAME[idx], tuple(REGION[idx])
                if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png"):
                    continue
                else:
                    if region_name == 'CHN' or region_name == 'JNHN':
                        add_scs_value = True
                    else:
                        add_scs_value = False
                    fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                                      add_south_china_sea=add_scs_value)
                    drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info, add_tag=False,
                                                          output_dir=Infile_list[1], add_city=False, fig=fig, ax=ax,
                                                          is_clean_plt=True, map_extent=map_extent,
                                                          png_name=region_name + '_' + File_Name + ".png")
                    drw.ax.tick_params(labelsize=16)
                    metdig_single_plot(Infile_list, lat_lon_data, drw, lat_lon_data.data, Infile_list[6])
                    drw.save()
    except:
        print(File_Name)


def single_model_r2m(Infile_list, hour, is_overwrite):
    File_Name = os.path.split(Infile_list[0])[1]
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])
    try:
        obs_time, step_time = os.path.basename(Infile_list[0]).split('.')
        OBS_time = datetime.strptime(obs_time, '%Y%m%d%H')
        FST_time = OBS_time + timedelta(hours=int(step_time))
        obs_time_dc = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(OBS_time)
        fst_time_dc = '预报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(FST_time)
        forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时'.format(int(step_time))

        if "ECMWF" in Infile_list[1]:
            t2m_array = get_org_data(Infile_list[-1][0], Infile_list[-1][1], Infile_list[-1][2], element="t2m",
                                     lev='')
            d2m_array = get_org_data(Infile_list[-1][0], Infile_list[-1][1], Infile_list[-1][2], element="d2m",
                                     lev='')
            lat_lon_value = calc_relative_humidity(t2m_array, d2m_array)
            Infile_list[0] = Infile_list[0].replace('r2m', 't2m')
            lat_lon_data = M4.open_m4(Infile_list[0])
            lat_lon_data_array = lat_lon_value[0][0][0]
        else:
            lat_lon_data = M4.open_m4(Infile_list[0])
            lat_lon_data_array = lat_lon_data.data
        if Infile_list[1].__contains__("CMA_GFS"):
            mask = GFS_mask
        else:
            mask = mask_array
        lat_lon_data.data[mask == 0] = np.nan

        for idx in range(len(REGION)):
            region_name, map_extent = REGION_NAME[idx], tuple(REGION[idx])
            if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
                continue
            if region_name == 'CHN' or region_name == 'JNHN':
                add_scs_value = True
            else:
                add_scs_value = False
            fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                              add_south_china_sea=add_scs_value)
            drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info, add_tag=False,
                                                  output_dir=Infile_list[1], add_city=False, fig=fig, ax=ax,
                                                  is_clean_plt=True, map_extent=map_extent,
                                                  is_overwrite=is_overwrite,
                                                  png_name=region_name + '_' + File_Name + ".png")
            drw.ax.tick_params(labelsize=16)
            metdig_single_plot(Infile_list, lat_lon_data, drw, lat_lon_data_array, Infile_list[6])
            drw.save()
    except Exception as e:
        logging.info(e)


def single_model_t2m(Infile_list, hour, is_overwrite):
    File_Name = os.path.split(Infile_list[0])[1]
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])
    try:
        obs_time, step_time = os.path.basename(Infile_list[0]).split('.')
        OBS_time = datetime.strptime(obs_time, '%Y%m%d%H')
        FST_time = OBS_time + timedelta(hours=int(step_time))
        obs_time_dc = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(OBS_time)
        fst_time_dc = '预报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(FST_time)
        forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时'.format(int(step_time))
        lat_lon_data = M4.open_m4(Infile_list[0])
        if Infile_list[1].__contains__("CMA_GFS"):
            mask = GFS_mask
        else:
            mask = mask_array
        lat_lon_data.data[mask == 0] = np.nan
        for idx in range(len(REGION)):
            region_name, map_extent = REGION_NAME[idx], tuple(REGION[idx])
            if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
                continue
            if region_name == 'CHN' or region_name == 'JNHN':
                add_scs_value = True
            else:
                add_scs_value = False
            fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                              add_south_china_sea=add_scs_value)
            drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info, add_tag=False,
                                                  output_dir=Infile_list[1], add_city=False, fig=fig, ax=ax,
                                                  is_clean_plt=True, map_extent=map_extent,
                                                  is_overwrite=is_overwrite,
                                                  png_name=region_name + '_' + File_Name + ".png")
            drw.ax.tick_params(labelsize=16)
            metdig_single_plot(Infile_list, lat_lon_data, drw, lat_lon_data.data, Infile_list[6])
            drw.save()
    except Exception as e:
        logging.info(e)

def minimum(A, B):
    return np.minimum(A, B)

def maximum(A, B):
    return np.maximum(A, B)

def gain_maximum(array_list, func):
    func_dict = {'min': minimum, 'max': maximum}
    if len(array_list) >= 2:
        array_A, array_B = array_list[0], array_list[1]
        array_C = func_dict.get(func)(array_A, array_B)
        for i in array_list[2:]:
            array_C = func_dict.get(func)(array_C, i)
        return array_C
    else:
        return None

def single_model_t2m_min(Infile_list, Infile_list_t2m_High, hour, fc, is_overwrite):
    File_Name = os.path.split(Infile_list[0])[1]
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])
    if not os.path.exists(Infile_list_t2m_High[1]):
        os.makedirs(Infile_list_t2m_High[1])

    try:
        obs_time, step_time = os.path.basename(Infile_list[0]).split('.')
        OBS_time = datetime.strptime(obs_time, '%Y%m%d%H')
        FST_time = OBS_time + timedelta(hours=int(step_time))
        obs_time_dc = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(OBS_time)
        fst_time_dc = '预报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(FST_time)
        forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时'.format(int(step_time))
        if int(step_time) >= hour:
            step_time_list = [obs_time + '.'+ '%03d'%i for i in range(int(step_time) - 24, int(step_time) + 3, 3)]
            file_path_list = [os.path.join(os.path.dirname(Infile_list[0]), i) for i in step_time_list]
            file_exist_list = [i for i in file_path_list if os.path.exists(i)]
            data_array_list = [M4.open_m4(i).data for i in file_exist_list]
            data_array = gain_maximum(data_array_list, fc)
            lat_lon_data = M4.open_m4(Infile_list[0])
            if Infile_list[1].__contains__("CMA_GFS"):
                mask = GFS_mask
            else:
                mask = mask_array
            data_array[mask == 0] = np.nan
            for idx in range(len(REGION)):
                region_name, map_extent = REGION_NAME[idx], tuple(REGION[idx])
                if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
                    continue
                if region_name == 'CHN' or region_name == 'JNHN':
                    add_scs_value = True
                else:
                    add_scs_value = False
                fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                                  add_south_china_sea=add_scs_value)
                drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info, add_tag=False,
                                                      output_dir=Infile_list[1], add_city=False, fig=fig, ax=ax,
                                                      is_overwrite=is_overwrite,
                                                      is_clean_plt=True, map_extent=map_extent,
                                                      png_name=region_name + '_' + File_Name + ".png")
                drw.ax.tick_params(labelsize=16)
                metdig_single_plot_temex(Infile_list, lat_lon_data, drw, data_array, Infile_list[6])
                drw.save()
            if fc == 'max':
                for idx in range(len(REGION)):
                    region_name, map_extent = REGION_NAME[idx], tuple(REGION[idx])
                    if os.path.exists(Infile_list_t2m_High[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
                        return
                    if region_name == 'CHN' or region_name == 'JNHN':
                        add_scs_value = True
                    else:
                        add_scs_value = False
                    fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                                      add_south_china_sea=add_scs_value)
                    drw = draw_compose.horizontal_compose(title=Infile_list_t2m_High[2], description=forcast_info,
                                                          add_tag=False, output_dir=Infile_list_t2m_High[1],
                                                          add_city=False, fig=fig, ax=ax,
                                                          is_overwrite=is_overwrite,
                                                          is_clean_plt=True, map_extent=map_extent,
                                                          png_name=region_name + '_' + File_Name + ".png")
                    drw.ax.tick_params(labelsize=16)
                    metdig_single_plot_filter(Infile_list_t2m_High, lat_lon_data, drw, data_array, Infile_list_t2m_High[6])
                    drw.save()
    except Exception as e:
        logging.info(e)

def single_model_gustwind(Infile_list, hour, is_overwrite):
    File_Name = os.path.split(Infile_list[0])[1]
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])
    try:
        obs_time, step_time = os.path.basename(Infile_list[0]).split('.')
        OBS_time = datetime.strptime(obs_time, '%Y%m%d%H')
        FST_time = OBS_time + timedelta(hours=int(step_time))
        obs_time_dc = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(OBS_time)
        fst_time_dc = '预报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(FST_time)
        forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时'.format(int(step_time))
        if int(step_time) >= hour - hour:

            lat_lon_data = M4.open_m4(Infile_list[0])
            data_array = lat_lon_data.data
            if Infile_list[1].__contains__("CMA_GFS"):
                mask = GFS_mask
            else:
                mask = mask_array
            data_array[mask == 0] = np.nan
            data_array[data_array <= 10.8] = 5
            data_array[(data_array <= 13.9) & (data_array > 10.8)] = 6
            data_array[(data_array <= 17.2) & (data_array > 13.9)] = 7
            data_array[(data_array <= 20.8) & (data_array > 17.2)] = 8
            data_array[(data_array <= 24.5) & (data_array > 20.8)] = 9
            data_array[(data_array <= 28.5) & (data_array > 24.5)] = 10
            data_array[(data_array <= 32.7) & (data_array > 28.5)] = 11
            data_array[(data_array <= 37) & (data_array > 32.7)] = 12
            data_array[(data_array <= 41.5) & (data_array > 37)] = 13
            data_array[(data_array <= 46.2) & (data_array > 41.5)] = 14
            data_array[(data_array <= 51) & (data_array > 46.2)] = 15
            data_array[(data_array <= 56.1) & (data_array > 51)] = 16
            data_array[(data_array <= 61.3) & (data_array > 56.1)] = 17

            for idx in range(len(REGION)):
                region_name, map_extent = REGION_NAME[idx], tuple(REGION[idx])
                if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
                    continue
                if region_name == 'CHN' or region_name == 'JNHN':
                    add_scs_value = True
                else:
                    add_scs_value = False
                fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                                  add_south_china_sea=add_scs_value)
                drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info, add_tag=False,
                                                      output_dir=Infile_list[1], add_city=False, fig=fig, ax=ax,
                                                      is_clean_plt=True, map_extent=map_extent,
                                                      is_overwrite=is_overwrite,
                                                      png_name=region_name + '_' + File_Name + ".png")
                drw.ax.tick_params(labelsize=16)
                metdig_exwind_plot(Infile_list, lat_lon_data, drw, data_array, Infile_list[6], extend='min')
                drw.save()
    except Exception as e:
        logging.info(e)

def single_model_exwind(Infile_list, hour, is_overwrite):
    File_Name = os.path.split(Infile_list[0])[1]
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])
    try:
        obs_time, step_time = os.path.basename(Infile_list[0]).split('.')
        OBS_time = datetime.strptime(obs_time, '%Y%m%d%H')
        FST_time = OBS_time + timedelta(hours=int(step_time))
        obs_time_dc = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(OBS_time)
        fst_time_dc = '预报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(FST_time)
        forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时'.format(int(step_time))
        if int(step_time) >= hour:
            step_time_list = [obs_time + '.'+ '%03d'%i for i in range(int(step_time) - 24, int(step_time) + 3, 3)]
            file_path_list = [os.path.join(os.path.dirname(Infile_list[0]), i) for i in step_time_list]
            file_exist_list = [i for i in file_path_list if os.path.exists(i)]
            data_array_list = [M4.open_m4(i).data for i in file_exist_list]
            data_array = gain_maximum(data_array_list, 'max')

            lat_lon_data = M4.open_m4(Infile_list[0])
            if Infile_list[1].__contains__("CMA_GFS"):
                mask = GFS_mask
            else:
                mask = mask_array
            data_array[mask == 0] = np.nan
            data_array[data_array <= 10.8] = 5
            data_array[(data_array <= 13.9) & (data_array > 10.8)] = 6
            data_array[(data_array <= 17.2) & (data_array > 13.9)] = 7
            data_array[(data_array <= 20.8) & (data_array > 17.2)] = 8
            data_array[(data_array <= 24.5) & (data_array > 20.8)] = 9
            data_array[(data_array <= 28.5) & (data_array > 24.5)] = 10
            data_array[(data_array <= 32.7) & (data_array > 28.5)] = 11
            data_array[(data_array <= 37) & (data_array > 32.7)] = 12
            data_array[(data_array <= 41.5) & (data_array > 37)] = 13
            data_array[(data_array <= 46.2) & (data_array > 41.5)] = 14
            data_array[(data_array <= 51) & (data_array > 46.2)] = 15
            data_array[(data_array <= 56.1) & (data_array > 51)] = 16
            data_array[(data_array <= 61.3) & (data_array > 56.1)] = 17

            for idx in range(len(REGION)):
                region_name, map_extent = REGION_NAME[idx], tuple(REGION[idx])
                if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
                    continue
                if region_name == 'CHN' or region_name == 'JNHN':
                    add_scs_value = True
                else:
                    add_scs_value = False
                fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                                  add_south_china_sea=add_scs_value)
                drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info, add_tag=False,
                                                      output_dir=Infile_list[1], add_city=False, fig=fig, ax=ax,
                                                      is_clean_plt=True, map_extent=map_extent,
                                                      is_overwrite=is_overwrite,
                                                      png_name=region_name + '_' + File_Name + ".png")
                drw.ax.tick_params(labelsize=16)
                metdig_exwind_plot(Infile_list, lat_lon_data, drw, data_array, Infile_list[6], extend='min')
                drw.save()
    except Exception as e:
        logging.info(e)

# 温度、相对湿度和降水（降水为累计）数据准备——CLDAS实况数据
def single_CLDAS_temC(Infile_list, hour, is_overwrite):
    File_Name = os.path.split(Infile_list[0])[1]
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])
    try:
        if os.path.exists(Infile_list[0]):
            file_time = os.path.basename(Infile_list[0]).split('.')[0]
            file_dir, file_name = os.path.split(Infile_list[0])
            father_file_dir = os.path.dirname(file_dir)
            father_file_dir_name = (datetime.strptime(str(int(os.path.split(file_dir)[1])), '%Y%m%d') - timedelta(
                days=int(hour / 24)))
            father_file_name = father_file_dir_name.strftime('%y%m%d') + file_name[-6:]
            father_file = os.path.join(father_file_dir, father_file_dir_name.strftime('%Y%m%d'), father_file_name)
            file_time_end = datetime.strptime(file_time, '%y%m%d%H')
            file_time_start = file_time_end - timedelta(days=int(hour / 24))
            forcast_info = '实况时间：{}年{}月{}日{}时-{}年{}月{}日{}时'.format(file_time_start.year, file_time_start.month,
                                                                   file_time_start.day, file_time_start.hour,
                                                                   file_time_end.year, file_time_end.month,
                                                                   file_time_end.day, file_time_end.hour)
            if father_file_name[-6:-4] == '08' or father_file_name[-6:-4] == '20':
                if os.path.exists(father_file) and os.path.exists(Infile_list[0]):
                    lat_lon_data = M4.open_m4(Infile_list[0], encoding='GBK')
                    lat_lon_data_24 = M4.open_m4(father_file, encoding='GBK')
                    lat_lon_data_obs = lat_lon_data.data - lat_lon_data_24.data
                    lat_lon_data_obs[mask_array_cldas == 0] = np.nan
                    for idx in range(len(REGION)):
                        region_name, map_extent = REGION_NAME[idx], tuple(REGION[idx])
                        if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
                            return
                        if region_name == 'CHN' or region_name == 'JNHN':
                            add_scs_value = True
                        else:
                            add_scs_value = False
                        fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                                          add_south_china_sea=add_scs_value)
                        drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info,
                                                              fig=fig, ax=ax,
                                                              output_dir=Infile_list[1], add_city=False,
                                                              add_tag=False, is_overwrite=is_overwrite,
                                                              is_clean_plt=True, map_extent=map_extent,
                                                              png_name=region_name + '_20' + File_Name + ".png")
                        drw.ax.tick_params(labelsize=16)
                        metdig_single_plot_temex(Infile_list, lat_lon_data, drw, lat_lon_data_obs, Infile_list[6])
                        drw.save()
    except Exception as e:
        logging.info(e)


def single_CLDAS_t2m_High(Infile_list, hour):
    File_Name = os.path.split(Infile_list[0])[1]
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])
    try:
        if os.path.exists(Infile_list[0]):
            file_time = os.path.basename(Infile_list[0]).split('.')[0]
            file_time_DATE = datetime.strptime(file_time, '%y%m%d%H')
            forcast_info = '实况时间：{}年{}月{}日{}时'.format(file_time_DATE.year, file_time_DATE.month, file_time_DATE.day,
                                                      file_time_DATE.hour)
            lat_lon_data = M4.open_m4(Infile_list[0], encoding='GBK')
            lat_lon_data.data[mask_array_cldas == 0] = np.nan
            for idx in range(len(REGION)):
                region_name, map_extent = REGION_NAME[idx], tuple(REGION[idx])
                if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png"):
                    continue
                else:
                    if region_name == 'CHN' or region_name == 'JNHN':
                        add_scs_value = True
                    else:
                        add_scs_value = False
                    fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                                      add_south_china_sea=add_scs_value)
                    drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info, fig=fig,
                                                          ax=ax,
                                                          output_dir=Infile_list[1], add_city=False, add_tag=False,
                                                          is_clean_plt=True, map_extent=map_extent,
                                                          png_name=region_name + '_' + File_Name + ".png")
                    drw.ax.tick_params(labelsize=16)
                    metdig_single_plot(Infile_list, lat_lon_data, drw, lat_lon_data.data, Infile_list[6])
                    drw.save()
    except:
        print(File_Name)


def single_CLDAS_tp(Infile_list, hour, is_overwrite):
    File_Name = os.path.split(Infile_list[0])[1]
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])
    try:
        if os.path.exists(Infile_list[0]):
            file_time = os.path.basename(Infile_list[0]).split('.')[0]
            file_time_end = datetime.strptime(file_time, '%y%m%d%H')
            file_time_start = file_time_end - timedelta(days=1)
            forcast_info = '实况时间：{}年{}月{}日{}时-{}年{}月{}日{}时'.format(file_time_start.year, file_time_start.month,
                                                                   file_time_start.day, file_time_start.hour,
                                                                   file_time_end.year, file_time_end.month,
                                                                   file_time_end.day, file_time_end.hour)
            file_dir, file_name = os.path.split(Infile_list[0])
            if file_name[-6:-4] == '08' or file_name[-6:-4] == '20':
                lat_lon_data = M4.open_m4(Infile_list[0], encoding='GBK')
                lat_lon_data.data[mask_array_cldas == 0] = np.nan
                for idx in range(len(REGION)):
                    region_name, map_extent = REGION_NAME[idx], tuple(REGION[idx])
                    if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
                        return
                    if region_name == 'CHN' or region_name == 'JNHN':
                        add_scs_value = True
                    else:
                        add_scs_value = False
                    fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                                      add_south_china_sea=add_scs_value)
                    drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info, fig=fig,
                                                          ax=ax, is_overwrite=is_overwrite,
                                                          output_dir=Infile_list[1], add_city=False,
                                                          is_clean_plt=True, map_extent=map_extent,
                                                          png_name=region_name + '_20' + File_Name + ".png",
                                                          add_tag=False)
                    M4_grd_roi, lon, lat = gain_tp_max(lat_lon_data, map_extent, lat_lon_data.data)
                    notice_info = '最大降水:{0}mm 经度:{1}°E 纬度:{2}°N'.format(
                        '%.1f' % np.nanmax(np.squeeze(M4_grd_roi.data)),
                        '%.2f' % lon, '%.2f' % lat)
                    ax.set_title(notice_info, loc='right', fontsize=16)
                    drw.ax.tick_params(labelsize=16)
                    metdig_single_plot(Infile_list, lat_lon_data, drw, lat_lon_data.data, Infile_list[6])
                    drw.save()
    except Exception as e:
        logging.info(e)


def single_CLDAS_other(Infile_list, hour, is_overwrite):
    File_Name = os.path.split(Infile_list[0])[1]
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])
    try:
        if os.path.exists(Infile_list[0]):
            file_time = os.path.basename(Infile_list[0]).split('.')[0]
            file_time_DATE = datetime.strptime(file_time, '%y%m%d%H')
            forcast_info = '实况时间：{}年{}月{}日{}时'.format(file_time_DATE.year, file_time_DATE.month, file_time_DATE.day,
                                                      file_time_DATE.hour)
            lat_lon_data = M4.open_m4(Infile_list[0], encoding='GBK')
            lat_lon_data.data[mask_array_cldas == 0] = np.nan
            for idx in range(len(REGION)):
                region_name, map_extent = REGION_NAME[idx], tuple(REGION[idx])
                if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
                    return
                if region_name == 'CHN' or region_name == 'JNHN':
                    add_scs_value = True
                else:
                    add_scs_value = False
                fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                                  add_south_china_sea=add_scs_value)
                drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info, fig=fig,
                                                      ax=ax, is_overwrite=is_overwrite,
                                                      output_dir=Infile_list[1], add_city=False, add_tag=False,
                                                      is_clean_plt=True, map_extent=map_extent,
                                                      png_name=region_name + '_20' + File_Name + ".png")
                drw.ax.tick_params(labelsize=16)
                metdig_single_plot(Infile_list, lat_lon_data, drw, lat_lon_data.data, Infile_list[6])
                drw.save()
    except Exception as e:
        logging.info(e)

def single_CLDAS_t2m_min(Infile_list, Infile_list_t2m_High, hour, fc, is_overwrite):
    File_Name = os.path.split(Infile_list[0])[1]
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])
    if not os.path.exists(Infile_list_t2m_High[1]):
        os.makedirs(Infile_list_t2m_High[1])
    try:
        if os.path.exists(Infile_list[0]):
            step_time_list = []
            file_time = os.path.basename(Infile_list[0]).split('.')[0]
            file_time_DATE = datetime.strptime(file_time, '%y%m%d%H')
            file_time_start = file_time_DATE - timedelta(hours=hour)
            forcast_info = '实况时间：{}年{}月{}日{}时-{}年{}月{}日{}时'.format(file_time_start.year, file_time_start.month,
                                                      file_time_start.day, file_time_start.hour, file_time_DATE.year,
                                                      file_time_DATE.month, file_time_DATE.day, file_time_DATE.hour)
            # while file_time_start <= file_time_DATE:
            #     step_time_list.append(file_time_start)
            #     file_time_start += timedelta(hours=1)
            # base_path = os.path.dirname(os.path.dirname(Infile_list[0]))
            # file_path_list = [os.path.join(base_path, i.strftime('%Y%m%d'), i.strftime('%y%m%d%H') + '.000') for i in step_time_list]
            # file_exist_list = [i for i in file_path_list if os.path.exists(i)]
            # data_array_list = [M4.open_m4(i, encoding='GBK').data for i in file_exist_list]
            # data_array = gain_maximum(data_array_list, fc)

            lat_lon_data = M4.open_m4(Infile_list[0], encoding='GBK')
            data_array = lat_lon_data.data
            data_array[mask_array_cldas == 0] = np.nan
            for idx in range(len(REGION)):
                region_name, map_extent = REGION_NAME[idx], tuple(REGION[idx])
                if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
                    return
                if region_name == 'CHN' or region_name == 'JNHN':
                    add_scs_value = True
                else:
                    add_scs_value = False
                fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                                  add_south_china_sea=add_scs_value)
                drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info, fig=fig,
                                                      ax=ax, is_overwrite=is_overwrite,
                                                      output_dir=Infile_list[1], add_city=False, add_tag=False,
                                                      is_clean_plt=True, map_extent=map_extent,
                                                      png_name=region_name + '_20' + File_Name + ".png")
                drw.ax.tick_params(labelsize=16)
                metdig_single_plot_temex(Infile_list, lat_lon_data, drw, data_array, Infile_list[6])
                drw.save()
            if fc == 'max':
                for idx in range(len(REGION)):
                    region_name, map_extent = REGION_NAME[idx], tuple(REGION[idx])
                    if os.path.exists(Infile_list_t2m_High[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
                        return
                    if region_name == 'CHN' or region_name == 'JNHN':
                        add_scs_value = True
                    else:
                        add_scs_value = False
                    fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                                      add_south_china_sea=add_scs_value)
                    drw = draw_compose.horizontal_compose(title=Infile_list_t2m_High[2], description=forcast_info,
                                                          fig=fig, ax=ax, output_dir=Infile_list_t2m_High[1],
                                                          add_city=False, add_tag=False, is_overwrite=is_overwrite,
                                                          is_clean_plt=True, map_extent=map_extent,
                                                          png_name=region_name + '_20' + File_Name + ".png")
                    drw.ax.tick_params(labelsize=16)
                    metdig_single_plot_filter(Infile_list_t2m_High, lat_lon_data, drw, data_array, Infile_list_t2m_High[6])
                    drw.save()
    except Exception as e:
        logging.info(e)


def met_model_single_plot_tp(Infile_list, step, is_overwrite):
    File_Name = os.path.split(Infile_list[0])[1]
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])
    try:
        if os.path.exists(Infile_list[0]):
            file_dir, file_name = os.path.split(Infile_list[0])
            if int(file_name[-3:]) >= step and int(file_name[-3:]) % step == 0:
                file_name_24 = '%.3f' % (float(file_name) - step / 1000)
                file_dir_24 = os.path.join(file_dir, str(file_name_24))
                if os.path.exists(file_dir_24):
                    lat_lon_data = M4.open_m4_org(Infile_list[0])
                    lat_lon_data_24 = M4.open_m4_org(file_dir_24)
                    lat_lon_data_obs = lat_lon_data.data - lat_lon_data_24.data
                    if Infile_list[1].__contains__("CMA_GFS"):
                        mask = GFS_mask
                    else:
                        mask = mask_array
                    if '对流性' not in Infile_list[2]:
                        if Infile_list[1].__contains__("NCEP"):
                            lat_lon_data_obs = lat_lon_data_obs / 1000
                    lat_lon_data_obs[mask == 0] = np.nan
                    for idx in range(len(REGION)):
                        region_name, map_extent = REGION_NAME[idx], tuple(REGION[idx])
                        if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
                            continue
                        obs_time, step_time = os.path.basename(Infile_list[0]).split('.')
                        if step_time != '000':
                            OBS_time = datetime.strptime(obs_time, '%Y%m%d%H')
                            FST_time = OBS_time + timedelta(hours=int(step_time))
                            obs_time_dc = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(OBS_time)
                            fst_time_dc = '预报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(FST_time)
                            forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时'.format(
                                int(step_time))
                            if region_name == 'CHN' or region_name == 'JNHN':
                                add_scs_value = True
                            else:
                                add_scs_value = False
                            fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                                              add_south_china_sea=add_scs_value)
                            png_name = region_name + '_' + File_Name + ".png"
                            drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info,
                                                                  add_tag=False, is_overwrite=is_overwrite,
                                                                  output_dir=Infile_list[1], add_city=False,
                                                                  fig=fig, ax=ax,
                                                                  is_clean_plt=True, map_extent=map_extent,
                                                                  png_name=png_name)
                            M4_grd_roi, lon, lat = gain_tp_max(lat_lon_data, map_extent, lat_lon_data_obs)
                            notice_info = '最大降水:{0}mm 经度:{1}°E 纬度:{2}°N'.format(
                                '%.1f' % np.nanmax(np.squeeze(M4_grd_roi.data)),
                                '%.2f' % lon, '%.2f' % lat)
                            ax.set_title(notice_info, loc='right', fontsize=16)
                            drw.ax.tick_params(labelsize=16)
                            metdig_single_plot(Infile_list, lat_lon_data, drw, lat_lon_data_obs, Infile_list[6])
                            drw.save()
                        else:
                            continue
    except Exception as e:
        logging.info(e)


def met_model_single_plot_tp_CLDAS(Infile_list, step, is_overwrite):
    File_Name = os.path.split(Infile_list[0])[1]
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])
    try:
        # if os.path.exists(Infile_list[0]):
        file_dir, file_name = os.path.split(Infile_list[0])
        father_file_dir = os.path.dirname(file_dir)
        lat_lon, freq = M4.open_m4(Infile_list[0]), 0
        lat_lon_data = lat_lon.data
        lat_lon_data[lat_lon_data == 9999] = np.nan
        for i in range(1, step):
            father_file_dir_name = (datetime.strptime(str(os.path.splitext(file_name)[0]), '%y%m%d%H') - timedelta(
                hours=i)).strftime('%Y%m%d')
            father_file_name = (datetime.strptime(str(os.path.splitext(file_name)[0]), '%y%m%d%H') - timedelta(
                hours=i)).strftime('%y%m%d%H') + file_name[-4:]
            father_file = os.path.join(father_file_dir, father_file_dir_name, father_file_name)
            if os.path.exists(father_file):
                data_tmp = M4.open_m4(father_file).data
                data_tmp[data_tmp == 9999] = np.nan
                lat_lon_data += data_tmp
                freq += 1
            else:
                freq += 0
            lat_lon_data[mask_array_cldas == 0] = np.nan

        if freq == step - 1:
            for idx in range(len(REGION)):
                region_name, map_extent = REGION_NAME[idx], tuple(REGION[idx])
                if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
                    return
                file_time_end = datetime.strptime(str(os.path.splitext(file_name)[0]), '%y%m%d%H')
                file_time_start = datetime.strptime(str(os.path.splitext(file_name)[0]), '%y%m%d%H') - timedelta(
                    hours=step)
                forcast_info = '实况时间：{}年{}月{}日{}时-{}年{}月{}日{}时'.format(file_time_start.year,
                                                                       file_time_start.month,
                                                                       file_time_start.day, file_time_start.hour,
                                                                       file_time_end.year, file_time_end.month,
                                                                       file_time_end.day, file_time_end.hour)
                if region_name == 'CHN' or region_name == 'JNHN':
                    add_scs_value = True
                else:
                    add_scs_value = False
                fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                                  add_south_china_sea=add_scs_value)
                drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info, fig=fig,
                                                      ax=ax, output_dir=Infile_list[1], add_city=False,
                                                      is_overwrite=is_overwrite,
                                                      is_clean_plt=True, map_extent=map_extent, add_tag=False,
                                                      png_name=region_name + '_20' + File_Name + ".png")
                M4_grd_roi, lon, lat = gain_tp_max(lat_lon, map_extent, lat_lon_data)
                notice_info = '最大降水:{0}mm 经度:{1}°E 纬度:{2}°N'.format(
                    '%.1f' % np.nanmax(np.squeeze(M4_grd_roi.data)),
                    '%.2f' % lon, '%.2f' % lat)
                ax.set_title(notice_info, loc='right', fontsize=16)
                drw.ax.tick_params(labelsize=16)
                metdig_single_plot(Infile_list, lat_lon, drw, lat_lon_data, Infile_list[6])
                drw.save()
    except Exception as e:
        logging.info(e)


# 温度、变温、相对湿度和降水——模式预报数据
def single_plot(model_name, report_time, cst, is_overwrite):
    file_t2m = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='t2m', lev=''),
                os.path.dirname(MODEL_SAVE_OUT).format(model=model_name, report_time=report_time, out_name='tem',
                                                       lev=''),
                t2m_title.format(model_name), t2m_var, t2m_units, t2m_colorbar, cmap_tem
                ]

    file_t2m_min = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='t2m', lev=''),
                os.path.dirname(MODEL_SAVE_OUT).format(model=model_name, report_time=report_time, out_name='tem_min',
                                                       lev=''),
                t2m_min_title.format(model_name), t2m_min_var, t2m_min_units, t2m_min_colorbar, cmap_tem_min
                ]

    file_t2m_max = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='t2m', lev=''),
                os.path.dirname(MODEL_SAVE_OUT).format(model=model_name, report_time=report_time, out_name='tem_exmax',
                                                       lev=''),
                t2m_max_title.format(model_name), t2m_max_var, t2m_min_units, t2m_min_colorbar, cmap_tem_min
                ]

    file_t2m_High = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='t2m', lev=''),
                     os.path.dirname(MODEL_SAVE_OUT).format(model=model_name, report_time=report_time,
                                                            out_name='tem_max',
                                                            lev=''),
                     t2m_high_title.format(model_name), t2m_high_var, t2m_high_units, t2m_high_colorbar, cmap_tem_high
                     ]

    file_temC_24 = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='t2m', lev=''),
                    os.path.dirname(MODEL_SAVE_OUT).format(model=model_name, report_time=report_time,
                                                           out_name='tem_change', lev=''),
                    tem_change_title.format(model_name), tem_change_var, tem_change_units, tem_change_colorbar,
                    cmap_tem_change
                    ]

    file_temC_48 = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='t2m', lev=''),
                    os.path.dirname(MODEL_SAVE_OUT).format(model=model_name, report_time=report_time,
                                                           out_name='tem_change_48', lev=''),
                    tem_change_title.format(model_name), tem_change_var, tem_change_units, tem_change_colorbar,
                    cmap_tem_change
                    ]

    file_wind = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='gust', lev=''),
                os.path.dirname(MODEL_SAVE_OUT).format(model=model_name, report_time=report_time, out_name='gustwind',
                                                       lev=''),
                wind_title.format(model_name), wind_var, exwind_units, exwind_colorbar, cmap_exwind
                ]

    file_exwind = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='gust', lev=''),
                os.path.dirname(MODEL_SAVE_OUT).format(model=model_name, report_time=report_time, out_name='exwind_24',
                                                       lev=''),
                exwind_title.format(model_name), exwind_var, exwind_units, exwind_colorbar, cmap_exwind
                ]

    file_sd_24 = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='sd', lev=''),
                  os.path.dirname(MODEL_SAVE_OUT).format(model=model_name, report_time=report_time, out_name='sf24',
                                                         lev=''),
                  sd_title.format(model_name), sd_var, sd_units, sd_colorbar, cmap_sd
                  ]

    file_sd_3 = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='sd', lev=''),
                 os.path.dirname(MODEL_SAVE_OUT).format(model=model_name, report_time=report_time, out_name='sf03',
                                                        lev=''),
                 sd_hour_title.format(model_name, 3), sd_hour_var.format(3), sd_units, sd_hour_colorbar, cmap_sd
                 ]

    file_sd_6 = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='sd', lev=''),
                 os.path.dirname(MODEL_SAVE_OUT).format(model=model_name, report_time=report_time, out_name='sf06',
                                                        lev=''),
                 sd_hour_title.format(model_name, 6), sd_hour_var.format(6), sd_units, sd_hour_colorbar, cmap_sd
                 ]

    file_sd_12 = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='sd', lev=''),
                  os.path.dirname(MODEL_SAVE_OUT).format(model=model_name, report_time=report_time, out_name='sf12',
                                                         lev=''),
                  sd_hour_title.format(model_name, 12), sd_hour_var.format(12), sd_units, sd_hour_colorbar, cmap_sd
                  ]

    file_r2m = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='r2m', lev=''),
                os.path.dirname(MODEL_SAVE_OUT).format(model=model_name, report_time=report_time, out_name='r',
                                                       lev=''),
                rh_title.format(model_name), rh_var, rh_units, rh_colorbar, cmap_r, [model_name, report_time, cst]
                ]

    file_tp = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='tp', lev=''),
               os.path.dirname(MODEL_SAVE_OUT).format(model=model_name, report_time=report_time,
                                                      out_name='pre24_hgt', lev=''),
               tp_title.format(model_name), tp_var, tp_units, tp_colorbar, cmap_tp
               ]

    file_cp = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='cp', lev=''),
               os.path.dirname(MODEL_SAVE_OUT).format(model=model_name, report_time=report_time,
                                                      out_name='pre24_cp', lev=''),
               cp_title.format(model_name), cp_var, tp_units, tp_colorbar, cmap_tp
               ]

    file_lsp = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='lsp', lev=''),
                os.path.dirname(MODEL_SAVE_OUT).format(model=model_name, report_time=report_time,
                                                       out_name='pre24_lsp', lev=''),
                lsp_title.format(model_name), lsp_var, tp_units, tp_colorbar, cmap_tp
                ]

    file_tp_3 = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='tp', lev=''),
                 os.path.dirname(MODEL_SAVE_OUT).format(model=model_name, report_time=report_time, out_name='pre03',
                                                        lev=''),
                 tp_title.format(model_name), tp_var, tp_units, tp_colorbar2, cmap_tp_hour
                 ]

    file_tp_6 = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='tp', lev=''),
                 os.path.dirname(MODEL_SAVE_OUT).format(model=model_name, report_time=report_time, out_name='pre06',
                                                        lev=''),
                 tp_title.format(model_name), tp_var, tp_units, tp_colorbar2, cmap_tp_hour
                 ]

    file_tp_12 = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='tp', lev=''),
                  os.path.dirname(MODEL_SAVE_OUT).format(model=model_name, report_time=report_time,
                                                         out_name='pre12', lev=''),
                  tp_title.format(model_name), tp_var, tp_units, tp_colorbar2, cmap_tp_hour
                  ]

    file_cp_12 = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='cp', lev=''),
                  os.path.dirname(MODEL_SAVE_OUT).format(model=model_name, report_time=report_time,
                                                         out_name='pre12_cp', lev=''),
                  cp_title.format(model_name), cp_var, tp_units, tp_colorbar2, cmap_tp_hour
                  ]
    file_tp_sd = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='tp', lev=''),
                  MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='sd', lev=''),
                  os.path.dirname(MODEL_SAVE_OUT).format(model=model_name, report_time=report_time,
                                                         out_name='pre_sf24', lev=''),
                  tp_sd_title.format(model_name), tp_sd_var, tp_units, cmap_tp_sd]

    file_tp_sd_class = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='tp', lev=''),
                        MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='sd', lev=''),
                        os.path.dirname(MODEL_SAVE_OUT).format(model=model_name, report_time=report_time,
                                                               out_name='pre_sf_class', lev=''),
                        tp_sd_title.format(model_name), tp_sd_var, tp_units, cmap_tp, cmap_sd_hour]
    try:
        single_model_t2m(file_t2m, 3, is_overwrite)
        single_model_t2m_min(file_t2m_min, file_t2m_High, 24, 'min', is_overwrite)
        single_model_t2m_min(file_t2m_max, file_t2m_High, 24, 'max', is_overwrite)
        single_model_gustwind(file_wind, 3, is_overwrite)
        single_model_exwind(file_exwind, 24, is_overwrite)
        single_model_Change(file_sd_3, 3, 3, is_overwrite)
        single_model_Change(file_sd_6, 6, 6, is_overwrite)
        single_model_Change(file_sd_12, 12, 12, is_overwrite)
        single_model_Change(file_sd_24, 24, 12, is_overwrite)
        single_model_Change(file_temC_24, 24, 12, is_overwrite)
        single_model_Change(file_temC_48, 48, 12, is_overwrite)
        single_model_r2m(file_r2m, 3, is_overwrite)
        single_model_tp(file_tp, 24, is_overwrite)
        single_model_tp_sd(file_tp_sd, 24, is_overwrite)
        single_model_tp_sd_class(file_tp_sd_class, 24, is_overwrite)
        met_model_single_plot_tp(file_tp_3, 3, is_overwrite)
        met_model_single_plot_tp(file_tp_6, 6, is_overwrite)
        met_model_single_plot_tp(file_tp_12, 12, is_overwrite)
        met_model_single_plot_tp(file_cp_12, 12, is_overwrite)
        single_model_Change(file_cp, 24, 12, is_overwrite)
        single_model_Change(file_lsp, 24, 12, is_overwrite)
    except:
        print('singe model eror')


# 温度、变温、相对湿度和降水——CLDAS实况数据
def single_plot_CLDAS(model_name, report_time, cst, is_overwrite):
    CLDAS_t2m = [MODEL_ROOT_CLDAS.format(model=model_name, report_time=report_time, cst=cst, element='TMP', lev=''),
                 os.path.dirname(MODEL_SAVE_OUT_CLDAS).format(model=model_name, report_time=report_time,
                                                              out_name='tem', lev=''),
                 t2m_title.format(model_name), t2m_var, t2m_units, t2m_colorbar, cmap_tem
                 ]

    CLDAS_t2m_min = [MODEL_ROOT_CLDAS.format(model=model_name, report_time=report_time, cst=cst, element='MINIMUM_TEMPERATURE', lev=''),
                 os.path.dirname(MODEL_SAVE_OUT_CLDAS).format(model=model_name, report_time=report_time,
                                                              out_name='tem_min', lev=''),
                 t2m_min_title.format(model_name), t2m_min_var, t2m_min_units, t2m_min_colorbar, cmap_tem_min
                 ]

    CLDAS_t2m_max = [MODEL_ROOT_CLDAS.format(model=model_name, report_time=report_time, cst=cst, element='MAXIMUM_TEMPERATURE', lev=''),
                 os.path.dirname(MODEL_SAVE_OUT_CLDAS).format(model=model_name, report_time=report_time,
                                                              out_name='tem_exmax', lev=''),
                 t2m_max_title.format(model_name), t2m_max_var, t2m_min_units, t2m_min_colorbar, cmap_tem_min
                 ]

    CLDAS_t2m_High = [MODEL_ROOT_CLDAS.format(model=model_name, report_time=report_time, cst=cst, element='TMP', lev=''),
        os.path.dirname(MODEL_SAVE_OUT_CLDAS).format(model=model_name, report_time=report_time,
                                                     out_name='tem_max', lev=''),
        t2m_high_title.format(model_name), t2m_high_var, t2m_high_units, t2m_high_colorbar, cmap_tem_high
        ]

    CLDAS_temC_24 = [
        MODEL_ROOT_CLDAS.format(model=model_name, report_time=report_time, cst=cst, element='TMP', lev=''),
        os.path.dirname(MODEL_SAVE_OUT_CLDAS).format(model=model_name, report_time=report_time,
                                                     out_name='tem_change', lev=''),
        tem_change_title.format(model_name), tem_change_var, tem_change_units, tem_change_colorbar, cmap_tem_change
    ]

    CLDAS_temC_48 = [
        MODEL_ROOT_CLDAS.format(model=model_name, report_time=report_time, cst=cst, element='TMP', lev=''),
        os.path.dirname(MODEL_SAVE_OUT_CLDAS).format(model=model_name, report_time=report_time,
                                                     out_name='tem_change_48', lev=''),
        tem_change_title.format(model_name), tem_change_var, tem_change_units, tem_change_colorbar, cmap_tem_change
    ]

    CLDAS_r2m = [MODEL_ROOT_CLDAS.format(model=model_name, report_time=report_time, cst=cst, element='RH', lev=''),
                 os.path.dirname(MODEL_SAVE_OUT_CLDAS).format(model=model_name, report_time=report_time,
                                                              out_name='r', lev=''),
                 rh_title.format(model_name), rh_var, rh_units, rh_colorbar, cmap_r
                 ]

    CLDAS_tp = [
        MODEL_ROOT_CLDAS_TP.format(model=model_name, report_time=report_time, cst=cst, element='tp', lev=''),
        os.path.dirname(MODEL_SAVE_OUT_CLDAS).format(model=model_name, report_time=report_time,
                                                     out_name='pre24_hgt', lev=''),
        tp_title.format(model_name), tp_var, tp_units, tp_colorbar, cmap_tp
    ]

    CLDAS_tp_3 = [
        MODEL_ROOT_CLDAS_TP_1h.format(model=model_name, report_time=report_time, cst=cst, element='tp', lev=''),
        os.path.dirname(MODEL_SAVE_OUT_CLDAS).format(model=model_name, report_time=report_time, out_name='pre03',
                                                     lev=''),
        tp_title.format(model_name), tp_var, tp_units, tp_colorbar2, cmap_tp_hour
    ]

    CLDAS_tp_6 = [
        MODEL_ROOT_CLDAS_TP_1h.format(model=model_name, report_time=report_time, cst=cst, element='tp', lev=''),
        os.path.dirname(MODEL_SAVE_OUT_CLDAS).format(model=model_name, report_time=report_time, out_name='pre06',
                                                     lev=''),
        tp_title.format(model_name), tp_var, tp_units, tp_colorbar2, cmap_tp_hour
    ]

    CLDAS_tp_12 = [
        MODEL_ROOT_CLDAS_TP_1h.format(model=model_name, report_time=report_time, cst=cst, element='tp', lev=''),
        os.path.dirname(MODEL_SAVE_OUT_CLDAS).format(model=model_name, report_time=report_time, out_name='pre12',
                                                     lev=''),
        tp_title.format(model_name), tp_var, tp_units, tp_colorbar2, cmap_tp_hour
    ]

    try:
        single_CLDAS_other(CLDAS_t2m, 3, is_overwrite)
        single_CLDAS_other(CLDAS_r2m, 3, is_overwrite)
        single_CLDAS_temC(CLDAS_temC_24, 24, is_overwrite)
        single_CLDAS_temC(CLDAS_temC_48, 48, is_overwrite)
        single_CLDAS_t2m_min(CLDAS_t2m_min, CLDAS_t2m_High, 24, 'min', is_overwrite)
        single_CLDAS_t2m_min(CLDAS_t2m_max, CLDAS_t2m_High, 24, 'max', is_overwrite)
        single_CLDAS_tp(CLDAS_tp, 24, is_overwrite)
        met_model_single_plot_tp_CLDAS(CLDAS_tp_3, 3, is_overwrite)
        met_model_single_plot_tp_CLDAS(CLDAS_tp_6, 6, is_overwrite)
        met_model_single_plot_tp_CLDAS(CLDAS_tp_12, 12, is_overwrite)
    except:
        print('cldas eror')


# 绘制模式预报风速图
def plot_wind_speed_single(model_name, report_time, cst, is_overwrite):
    try:
        u_data = get_org_data(model_name, report_time, cst, element="u10", lev='')
        v_data = get_org_data(model_name, report_time, cst, element="v10", lev='')
        pwp = PlotHgtWindProd_sg(model_name, u_data, v_data, None, None)
        for idx in range(len(REGION)):
            file_path = MODEL_SAVE_OUT.format(model=model_name, out_name=windspeend_name, report_time=report_time,
                                              cst=cst, lev='', region=REGION_NAME[idx])
            pwp.plot_hgt_wind_speed_sg(REGION_NAME[idx], REGION[idx], file_path, is_overwrite=is_overwrite)
    except:
        print('绘制模式预报风速图错误：' + model_name + '\t' + report_time.strftime('%Y%m%d%H') + '\t' + str(cst))

# 绘制CLDAS实况风速图
def plot_wind_speed_single_CLDAS(model_name, report_time, cst, is_overwrite):
    try:
        u_data, v_data, u, v = get_org_data(model_name, report_time, cst, element="WIND", lev='')
        pwp = PlotHgtWindProd_sg(model_name, u_data, v_data, u, v)
        for idx in range(len(REGION)):
            file_path = MODEL_SAVE_OUT_CLDAS.format(model=model_name, out_name=windspeend_name, report_time=report_time,
                                                    cst=cst, lev='', add='.000', region=REGION_NAME[idx])
            pwp.plot_hgt_wind_speed_sg(REGION_NAME[idx], REGION[idx], file_path, is_overwrite=is_overwrite)
    except:
        print('绘制CLDAS实况风速图错误：' + model_name + '\t' + report_time.strftime('%Y%m%d') + '\t' + str(cst))

def creat_file_path(file_path):
    dir_name = os.path.dirname(file_path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

def gain_BJ_obs(file_list):
    TMP, windV, windD, DPT = [], [], [], []
    for file in file_list:
        if os.path.exists(file):
            with open(file, encoding='utf-8') as f:
                for file_line in f:
                    if len(file_line) == 202:
                        notes = file_line.strip().split()
                        if int(float(notes[0])) == 54511:
                            TMP.append(float(notes[4]))
                            windV.append(float(notes[8]))
                            windD.append(float(notes[7]))
                            DPT.append(float(notes[6]))
        else:
            TMP.append(None)
            windV.append(None)
            windD.append(None)
            DPT.append(None)
    TMP = [None if i is not None and i >= 9999 else i for i in TMP]
    windV = [None if i is not None and i >= 9999 else i for i in windV]
    windD = [None if i is not None and i >= 9999 else i for i in windD]
    DPT = [None if i is not None and i >= 9999 else i for i in DPT]
    return TMP, windV, windD, DPT

def gain_BJ_fst(file_list, sta):
    value_list = []
    for file in file_list:
        if os.path.exists(file):
            sta_grd = meb.read_griddata_from_micaps4(file)
            inter_grd = meb.interp_gs_nearest(sta_grd, sta)
            value_list.append(inter_grd.data0[0])
        else:
            value_list.append(None)
    return value_list

def gain_BJ_fst_VD(file_list_u, file_list_v, sta):
    WV_list, WD_list = [], []
    for i in range(len(file_list_u)):
        if os.path.exists(file_list_u[i]) and os.path.exists(file_list_v[i]):
            u, v = meb.read_griddata_from_micaps4(file_list_u[i]), meb.read_griddata_from_micaps4(file_list_v[i])
            u_array = metdig.utl.xrda_to_gridstda(u, level_dim='level', time_dim='time', lat_dim='lat',
                                                 lon_dim='lon', dtime_dim='dtime',
                                                 var_name='u', np_input_units='m/s')
            v_array = metdig.utl.xrda_to_gridstda(v, level_dim='level', time_dim='time', lat_dim='lat',
                                                 lon_dim='lon', dtime_dim='dtime',
                                                 var_name='v', np_input_units='m/s')

            wind_speed = other.wind_speed(u_array, v_array)
            wind_direction = other.wind_direction(u_array, v_array)
            inter_speed, inter_direction  = meb.interp_gs_nearest(wind_speed, sta), meb.interp_gs_nearest(wind_direction, sta)
            WV_list.append(inter_speed.data0[0])
            WD_list.append(inter_direction.data0[0])
        else:
            WV_list.append(None)
            WD_list.append(None)
    return WV_list, WD_list

def gain_BJ_fst_uv(file_list_u, file_list_v, sta):
    u_list, v_list = [], []
    for i in range(len(file_list_u)):
        if os.path.exists(file_list_u[i]) and os.path.exists(file_list_v[i]):
            u, v = meb.read_griddata_from_micaps4(file_list_u[i]), meb.read_griddata_from_micaps4(file_list_v[i])
            inter_u, inter_v  = meb.interp_gs_nearest(u, sta), meb.interp_gs_nearest(v, sta)
            u_list.append(inter_u.data0[0])
            v_list.append(inter_v.data0[0])
        else:
            u_list.append(None)
            v_list.append(None)
    return u_list, v_list

def gain_BJ_obs_uv(file_list_windv, file_list_windD):
    U, V = [], []
    rad = np.pi / 180.0
    for i in range(len(file_list_windD)):
        if file_list_windv[i] is not None and file_list_windD[i] is not None:
            U_value = -file_list_windv[i] * np.sin(file_list_windD[i] * rad)
            V_value = -file_list_windv[i] * np.cos(file_list_windD[i] * rad)
            U.append(U_value)
            V.append(V_value)
        else:
            U.append(None)
            V.append(None)
    return U, V

def plot_station(report_time, obs_time):
    obs_hour = []
    if obs_time.hour == 8 or obs_time.hour == 20:
        star_obs_time = obs_time - timedelta(days=1)
        star_obs_time_tmp = star_obs_time
        # 构建站点数据标准格式
        M3_grd = {
            '站号': [54511],
            "经度": [116.47],
            "纬度": [39.81],
        }
        sta = meb.sta_data(pd.DataFrame(M3_grd), columns=["id", "lon", "lat"])
        meb.set_stadata_coords(sta, level=0, time=datetime(2000, 1, 1, 8, 0), dtime=0)

        while star_obs_time_tmp <= obs_time:
            obs_hour.append(star_obs_time_tmp)
            star_obs_time_tmp += timedelta(hours=1)

        report_t = [(report_time - timedelta(hours=12)) for i in obs_hour]
        cst = [(int((obs_hour[i] - report_t[i]).seconds / 3600) + (obs_hour[i] - report_t[i]).days * 24) for i in range(len(obs_hour))]
        GFS_TMP_files = [
            MODEL_ROOT.format(model='CMA_GFS', report_time=report_t[i], cst=cst[i], element='t2m', lev='') for i in
            range(len(obs_hour))]
        GFS_U_files = [
            MODEL_ROOT.format(model='CMA_GFS', report_time=report_t[i], cst=cst[i], element='u10', lev='') for i in
            range(len(obs_hour))]
        GFS_V_files = [
            MODEL_ROOT.format(model='CMA_GFS', report_time=report_t[i], cst=cst[i], element='v10', lev='') for i in
            range(len(obs_hour))]
        GFS_RH_files = [
            MODEL_ROOT.format(model='CMA_GFS', report_time=report_t[i], cst=cst[i], element='r2m', lev='') for i in
            range(len(obs_hour))]
        MESO_TMP_files = [
            MODEL_ROOT.format(model='CMA_MESO', report_time=report_t[i], cst=cst[i], element='t2m', lev='') for i in
            range(len(obs_hour))]
        MESO_U_files = [
            MODEL_ROOT.format(model='CMA_MESO', report_time=report_t[i], cst=cst[i], element='u10', lev='') for i in
            range(len(obs_hour))]
        MESO_V_files = [
            MODEL_ROOT.format(model='CMA_MESO', report_time=report_t[i], cst=cst[i], element='v10', lev='') for i in
            range(len(obs_hour))]
        MESO_RH_files = [
            MODEL_ROOT.format(model='CMA_MESO', report_time=report_t[i], cst=cst[i], element='r2m', lev='') for i in
            range(len(obs_hour))]

        TMP_series = STATION_out_PATH.format(model='RAWSH', report_time=obs_time, out_name='tem_series', lev='', region='54511', cst=obs_time.hour, add='.000')
        RH_series = STATION_out_PATH.format(model='RAWSH', report_time=obs_time, out_name='r_series', lev='', region='54511', cst=obs_time.hour, add='.000')
        windV_series = STATION_out_PATH.format(model='RAWSH', report_time=obs_time, out_name='windv', lev='', region='54511', cst=obs_time.hour, add='.000')
        creat_file_path(TMP_series)
        creat_file_path(RH_series)
        creat_file_path(windV_series)
        forcast_info = '{}年{}月{}日{}时-{}年{}月{}日{}时'.format(star_obs_time.year, star_obs_time.month, star_obs_time.day, star_obs_time.hour,
                                                          obs_time.year, obs_time.month, obs_time.day, obs_time.hour)

        GFS_TMP, GFS_RH = gain_BJ_fst(GFS_TMP_files, sta), gain_BJ_fst(GFS_RH_files, sta)
        MESO_TMP, MESO_RH = gain_BJ_fst(MESO_TMP_files, sta), gain_BJ_fst(MESO_RH_files, sta)
        GFS_WV, GFS_WD = gain_BJ_fst_VD(GFS_U_files, GFS_V_files, sta)
        MESO_WV, MESO_WD = gain_BJ_fst_VD(MESO_U_files, MESO_V_files, sta)
        GFS_U, GFS_V = gain_BJ_fst_uv(GFS_U_files, GFS_V_files, sta)
        MESO_U, MESO_V = gain_BJ_fst_uv(MESO_U_files, MESO_V_files, sta)

        station_files = [STATION_PATH.format(obs_t=i) for i in [j-timedelta(hours=8) for j in obs_hour]]
        X_labels = [i.strftime('%H')+'时' if i.hour != 8 and i.hour != 0 else i.strftime('%H')+'时'+'\n'+i.strftime('%m-%d') for i in obs_hour]
        xlabels = np.array([i for i in range(len(obs_hour))])
        TMP, windV, windD, DPT = gain_BJ_obs(station_files)
        U, V = gain_BJ_obs_uv(windV, windD)

        #温度
        plt.figure(figsize=(16, 6))
        GFS_TMP_mask = np.isfinite(np.array(GFS_TMP).astype(np.double))
        GFS_TMP_y = np.array(GFS_TMP)[GFS_TMP_mask]
        GFS_TMP_x = np.array(xlabels)[GFS_TMP_mask]
        MESO_TMP_mask = np.isfinite(np.array(MESO_TMP).astype(np.double))
        MESO_TMP_y = np.array(MESO_TMP)[MESO_TMP_mask]
        MESO_TMP_x = np.array(xlabels)[MESO_TMP_mask]
        TMP_mask = np.isfinite(np.array(TMP).astype(np.double))
        TMP_y = np.array(TMP)[TMP_mask]
        TMP_x = np.array(xlabels)[TMP_mask]

        plt.plot(GFS_TMP_x, GFS_TMP_y, label='CMA_GFS', linewidth=1.5, color='r', marker='o', markersize='4', markerfacecolor='none')
        plt.plot(MESO_TMP_x, MESO_TMP_y, label='CMA_MESO', linewidth=1.5, color='g', marker='o', markersize='4', markerfacecolor='none')
        plt.plot(TMP_x, TMP_y, label='OBS', linewidth=1.5, color='k', marker='o', markersize='4', markerfacecolor='none')
        ax = plt.gca()
        plt.yticks(size=16)
        plt.grid(True, linestyle="--", alpha=0.5, axis='x')
        plt.xticks(xlabels, X_labels, fontproperties='SimHei', size=16)
        ax.xaxis.set_major_locator(MultipleLocator(2))
        plt.title('温度(℃)', loc='left', fontproperties='SimHei', fontsize=22)
        plt.legend(fontsize=18, bbox_to_anchor=(0.5, -0.1), loc=9, ncol=3, frameon=False)
        plt.savefig(TMP_series, bbox_inches='tight', dpi=100)
        plt.close()

        #风速
        plt.figure(figsize=(16, 6))
        GFS_windV_mask = np.isfinite(np.array(GFS_WV).astype(np.double))
        GFS_windV_y = np.array(GFS_WV)[GFS_windV_mask]
        GFS_windV_x = np.array(xlabels)[GFS_windV_mask]
        GFS_U_mask = np.isfinite(np.array(GFS_U).astype(np.double))
        GFS_U_y = np.array(GFS_U)[GFS_U_mask]
        GFS_U_x = np.array(xlabels)[GFS_U_mask]
        GFS_V_mask = np.isfinite(np.array(GFS_V).astype(np.double))
        GFS_V_y = np.array(GFS_V)[GFS_V_mask]

        MESO_windV_mask = np.isfinite(np.array(MESO_WV).astype(np.double))
        MESO_windV_y = np.array(MESO_WV)[MESO_windV_mask]
        MESO_windV_x = np.array(xlabels)[MESO_windV_mask]
        MESO_U_mask = np.isfinite(np.array(MESO_U).astype(np.double))
        MESO_U_y = np.array(MESO_U)[MESO_U_mask]
        MESO_U_x = np.array(xlabels)[MESO_U_mask]
        MESO_V_mask = np.isfinite(np.array(MESO_V).astype(np.double))
        MESO_V_y = np.array(MESO_V)[MESO_V_mask]

        windV_mask = np.isfinite(np.array(windV).astype(np.double))
        windV_y = np.array(windV)[windV_mask]
        windV_x = np.array(xlabels)[windV_mask]
        U_mask = np.isfinite(np.array(U).astype(np.double))
        bars_y = windV_y[U_mask[windV_mask]]
        U_y = np.array(U)[U_mask]
        U_x = np.array(xlabels)[U_mask]
        V_mask = np.isfinite(np.array(V).astype(np.double))
        V_y = np.array(V)[V_mask]

        ax = plt.gca()
        plt.plot(windV_x, windV_y, label='OBS', linewidth=1.5, color='k', marker='o', markersize='4', markerfacecolor='none')
        plt.barbs(U_x, list(bars_y), list(U_y), list(V_y), flagcolor='k', alpha=0.8, sizes=dict(emptybarb=0), length=6.5)
        plt.plot(GFS_windV_x, GFS_windV_y, label='CMA_GFS', linewidth=1.5, color='r', marker='o', markersize='4', markerfacecolor='none')
        plt.barbs(GFS_U_x, list(GFS_windV_y), list(GFS_U_y), list(GFS_V_y), flagcolor='r', alpha=0.8, sizes=dict(emptybarb=0), length=6.5)
        plt.plot(MESO_windV_x, MESO_windV_y, label='CMA_MESO', linewidth=1.5, color='g', marker='o', markersize='4', markerfacecolor='none')
        plt.barbs(MESO_U_x, list(MESO_windV_y), list(MESO_U_y), list(MESO_V_y), flagcolor='g', alpha=0.8, sizes=dict(emptybarb=0), length=6.5)
        plt.grid(True, linestyle="--", alpha=0.5, axis='x')
        plt.yticks(size=16)
        plt.xticks(xlabels, X_labels, fontproperties='SimHei', size=16)
        ax.xaxis.set_major_locator(MultipleLocator(2))
        plt.title('风速(m/s)', loc='left', fontproperties='SimHei', fontsize=22)
        plt.legend(fontsize=18, bbox_to_anchor=(0.5, -0.1), loc=9, ncol=3, frameon=False)
        plt.savefig(windV_series, bbox_inches='tight', dpi=100)
        plt.close()

        #相对湿度
        plt.figure(figsize=(16, 6))
        GFS_RH_mask = np.isfinite(np.array(GFS_RH).astype(np.double))
        GFS_RH_y = np.array(GFS_RH)[GFS_RH_mask]
        GFS_RH_x = np.array(xlabels)[GFS_RH_mask]
        MESO_RH_mask = np.isfinite(np.array(MESO_RH).astype(np.double))
        MESO_RH_y = np.array(MESO_RH)[MESO_RH_mask]
        MESO_RH_x = np.array(xlabels)[MESO_RH_mask]
        DPT_mask = np.isfinite(np.array(DPT).astype(np.double))
        mask_TMP_DPT = TMP_mask & DPT_mask
        TMP_RH, DPT_RH = np.array(TMP)[mask_TMP_DPT], np.array(DPT)[mask_TMP_DPT]
        temp = [(1 - (TMP_RH[i] + 235) / (DPT_RH[i] + 235))/(TMP_RH[i] + 235)  for i in range(len(TMP_RH))]
        RH = [100 * math.exp(4030 * i) for i in temp]
        RH_x = np.array(xlabels)[mask_TMP_DPT]

        plt.plot(GFS_RH_x, GFS_RH_y, label='CMA_GFS', linewidth=1.5, color='r', marker='o', markersize='4', markerfacecolor='none')
        plt.plot(MESO_RH_x, MESO_RH_y, label='CMA_MESO', linewidth=1.5, color='g', marker='o', markersize='4', markerfacecolor='none')
        plt.plot(RH_x, RH, label='OBS', linewidth=1.5, color='k', marker='o', markersize='4', markerfacecolor='none')
        ax = plt.gca()
        plt.grid(True, linestyle="--", alpha=0.5, axis='x')
        plt.yticks(size=16)
        plt.xticks(xlabels, X_labels, fontproperties='SimHei', size=16)
        plt.ylim(0, 100)
        ax.xaxis.set_major_locator(MultipleLocator(2))
        ax.yaxis.set_major_locator(MultipleLocator(20))
        plt.title('相对湿度(%)', loc='left', fontproperties='SimHei', fontsize=22)
        plt.legend(fontsize=18, bbox_to_anchor=(0.5, -0.1), loc=9, ncol=3, frameon=False)
        plt.savefig(RH_series, bbox_inches='tight', dpi=100)
        plt.close()
