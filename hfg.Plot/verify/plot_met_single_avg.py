# -- coding: utf-8 --
# @Time : 2023/7/5 14:13
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : plot_met_single_avg.py
# @Software: PyCharm
import logging
import os.path
import xarray as xr
import meteva.base as meb
from verify.config_single import *
import metdig
from verify.plot_model_single import horizontal_pallete_test
from datetime import datetime, timedelta
import numpy as np
from utils import MICAPS4 as M4
from metdig.graphics import draw_compose, contourf_method, pcolormesh_method
from verify.plot_model_single_avg import PlotHgtWindProd_sg


REGION_NAME = ["CHN", "NE", "HB", "HHJH", "JNHN", "XN", "NW"]
REGION = [
    [70, 140, 10, 60],
    [110, 138, 35, 57],
    [105, 125, 30, 47],
    [104, 125, 26, 41],
    [104, 125, 16, 33],
    [92, 115, 20, 35],
    [73, 123, 37, 50]
]

cmap_tp = ['#{:02x}{:02x}{:02x}'.format(*tuple(i)) for i in tp_color]
cmap_tp_hour = ['#{:02x}{:02x}{:02x}'.format(*tuple(i)) for i in tp_hour_color]
cmap_r = ['#{:02x}{:02x}{:02x}'.format(*tuple(i)) for i in r_color]
cmap_tem_change = ['#{:02x}{:02x}{:02x}'.format(*tuple(i)) for i in tem_change_color]
cmap_tem_min = ['#{:02x}{:02x}{:02x}'.format(*tuple(i)) for i in t2m_min_color]
cmap_exwind = ['#{:02x}{:02x}{:02x}'.format(*tuple(i)) for i in exwind_color]

path_Model = os.path.join(os.path.dirname(__file__), "mask_CHN25.dat")
#path_Model = os.path.join(os.path.dirname(__file__), "mask_NH25.dat")
path_CLDAS = os.path.join(os.path.dirname(__file__), "mask_005.dat")

Dict_situation = ['gh500_wind850_wvfldiv', 'gh500_wind850_wvfl', 'gh500_wind850_q', 'gh500_wind850_r', 'rcr', 'gh500_speed',
                'gh500_wind850_t', 'gh500_wind850_rcr', 'gh500_wind500_t', 'gh500_wind850_kindex',  'gh500_wind850_cth',
                'gh500_wind850_msl', 'gh500_wind850_tcwv', 'gh500_wind850_cape', 'gh500_wind700_q', 'gh500_wind850_hpbl']

Config_Info = {
    'r': [rh_title, rh_var, rh_units, rh_colorbar, cmap_r],
    'tem': [t2m_title, t2m_var, t2m_units, t2m_colorbar, cmap_tem],
    'tem_max': [t2m_high_title, t2m_high_var, t2m_high_units, t2m_high_colorbar, cmap_tem_high],
    'tem_min': [t2m_min_title, t2m_min_var, t2m_min_units, t2m_min_colorbar, cmap_tem_min],
    'tem_exmax': [t2m_max_title, t2m_max_var, t2m_min_units, t2m_min_colorbar, cmap_tem_min],
    'tem_change': [tem_change_title, tem_change_var, tem_change_units, tem_change_colorbar, cmap_tem_change],
    'tem_change_48': [tem_change_title, tem_change_var, tem_change_units, tem_change_colorbar, cmap_tem_change],
    'pre03': [tp_title, tp_var, tp_units, tp_colorbar2, cmap_tp_hour],
    'pre06': [tp_title, tp_var, tp_units, tp_colorbar2, cmap_tp_hour],
    'pre12': [tp_title, tp_var, tp_units, tp_colorbar2, cmap_tp_hour],
    'pre24_hgt': [tp_title, tp_var, tp_units, tp_colorbar, cmap_tp],
    'pre12_cp': [cp_title, cp_var, tp_units, tp_colorbar2, cmap_tp_hour],
    'pre24_cp': [cp_title, cp_var, tp_units, tp_colorbar, cmap_tp],
    'pre24_lsp': [lsp_title, lsp_var, tp_units, tp_colorbar, cmap_tp],
    'sf03': [sd_hour_title, sd_hour_var, sd_units, sd_hour_colorbar, cmap_sd],
    'sf06': [sd_hour_title, sd_hour_var, sd_units, sd_hour_colorbar, cmap_sd],
    'sf12': [sd_hour_title, sd_hour_var, sd_units, sd_hour_colorbar, cmap_sd],
    'sf24': [sd_title, sd_var, sd_units, sd_colorbar, cmap_sd],
    'pre_sf24': [tp_sd_title, tp_sd_var, tp_units, cmap_tp_sd],
    'pre_sf_class': [tp_sd_title, tp_sd_var, tp_units, cmap_tp, cmap_sd_hour],
    'gustwind': [wind_title, wind_var, exwind_units, exwind_colorbar, cmap_exwind],
    'exwind_24': [exwind_title, exwind_var, exwind_units, exwind_colorbar, cmap_exwind],
    'wind': None,
}

# 掩膜数据
def read_mask():
    if os.path.exists(path_Model):
        grd_mask = meb.read_griddata_from_micaps4(path_Model)
    else:
        grd_mask = None
    if os.path.exists(path_CLDAS):
        grd_mask_cldas = meb.read_griddata_from_micaps4(path_CLDAS)
    else:
        grd_mask_cldas = None

    return np.squeeze(grd_mask.data), np.squeeze(grd_mask_cldas.data)
mask_array, mask_array_cldas = read_mask()

# UV风数据读取
def get_org_data(file_path, model_name, report_time, cst, lev, scale=1):
    if not os.path.exists(file_path):
        return None
    lat_lon_data = M4.open_m4(file_path)
    if model_name == "CLDAS":
        mask = mask_array_cldas
    else:
        mask = mask_array
    lat_lon_data.data[mask == 0] = np.nan
    data_array = lat_lon_data.data
    latitudes = np.linspace(lat_lon_data.start_lat, lat_lon_data.end_lat, lat_lon_data.lat_count)
    longitudes = np.linspace(lat_lon_data.start_lon, lat_lon_data.end_lon, lat_lon_data.lon_count)
    if model_name == "CLDAS":
        data_array = data_array[::4, ::4]
        latitudes = latitudes[::4]
        longitudes = longitudes[::4]
    if lev != "":
        xr_data = xr.DataArray([[[[data_array * scale]]]],
                               coords=[[model_name.replace("_", "-")], [report_time], [cst], [int(lev)], latitudes,
                                       longitudes],
                               dims=["member", "time", "dtime", "level", "lat", "lon"])
    else:
        xr_data = xr.DataArray([[[data_array * scale]]],
                               coords=[[model_name.replace("_", "-")], [report_time], [cst], latitudes, longitudes],
                               dims=["member", "time", "dtime", "lat", "lon"])
    return xr_data

# 绘制单要素空间分布图
def metdig_single_plot(config_list, lat_lon_data, drw, data, extend='both'):
    lats = np.linspace(lat_lon_data.start_lat, lat_lon_data.end_lat, lat_lon_data.lat_count)
    lons = np.linspace(lat_lon_data.start_lon, lat_lon_data.end_lon, lat_lon_data.lon_count)
    xr_data = xr.DataArray(data, coords=(lats, lons), dims=("lat", "lon"))
    std_data = metdig.utl.xrda_to_gridstda(xr_data, level_dim='level', time_dim='time', lat_dim='lat',
                                           lon_dim='lon', dtime_dim='dtime', np_input_units=config_list[2])
    contourf_method.contourf_2d(drw.ax, std_data, levels=config_list[-2], cb_label=config_list[1], extend=extend,
                                cb_ticks=config_list[-2], cmap=config_list[-1], alpha=1,
                                colorbar_kwargs={'pad': 0.06, 'tick_label': config_list[-2]})

# 绘制极大风分布图
def metdig_exwind_plot(config_list, lat_lon_data, drw, data):
    lats = np.linspace(lat_lon_data.start_lat, lat_lon_data.end_lat, lat_lon_data.lat_count)
    lons = np.linspace(lat_lon_data.start_lon, lat_lon_data.end_lon, lat_lon_data.lon_count)
    xr_data = xr.DataArray(data, coords=(lats, lons), dims=("lat", "lon"))
    std_data = metdig.utl.xrda_to_gridstda(xr_data, level_dim='level', time_dim='time', lat_dim='lat',
                                           lon_dim='lon', dtime_dim='dtime',np_input_units=config_list[2])
    contourf_method.contourf_2d(drw.ax, std_data, levels=config_list[3], cb_label=config_list[1], cb_ticks=[i+0.5 for i in config_list[3][:-1]],
                                extend='min', cmap=config_list[-1], alpha=1, colorbar_kwargs={'pad': 0.06, 'tick_label': config_list[3][1:]})

# 绘制多要素空间分布图
def metdig_multi_plot(config_list, lat_lon_data, drw, data_tp, data_sd):
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
                                           lon_dim='lon', dtime_dim='dtime', np_input_units=config_list[2])
    contourf_method.contourf_2d(drw.ax, std_data, levels=[0, 1, 2, 5], cb_label=config_list[1],
                                extend='neither', alpha=1, cb_ticks=[0.5, 1.5, 3.5],
                                cmap=config_list[-1], colorbar_kwargs={'pad': 0.06, 'tick_label': ['无', '雨', '雪']})

def metdig_tp_sd_class(config_list, lat_lon_data, drw, data_tp, data_sd):
    lats = np.linspace(lat_lon_data.start_lat, lat_lon_data.end_lat, lat_lon_data.lat_count)
    lons = np.linspace(lat_lon_data.start_lon, lat_lon_data.end_lon, lat_lon_data.lon_count)
    xr_data_tp = xr.DataArray(data_tp, coords=(lats, lons), dims=("lat", "lon"))
    std_data_tp = metdig.utl.xrda_to_gridstda(xr_data_tp, level_dim='level', time_dim='time', lat_dim='lat',
                                              lon_dim='lon', dtime_dim='dtime', np_input_units=config_list[2])
    xr_data_sd = xr.DataArray(data_sd, coords=(lats, lons), dims=("lat", "lon"))
    std_data_sd = metdig.utl.xrda_to_gridstda(xr_data_sd, level_dim='level', time_dim='time', lat_dim='lat',
                                              lon_dim='lon', dtime_dim='dtime', np_input_units=config_list[2])
    contourf_method.contourf_2d(drw.ax, std_data_tp, levels=tp_colorbar, cb_label=' ',
                                extend='both', alpha=1, cmap=config_list[-2], colorbar_kwargs={'pad': 0.05})
    contourf_method.contourf_2d(drw.ax, std_data_sd, levels=sd_colorbar, cb_label=config_list[1],
                                extend='neither', alpha=1, cmap=config_list[-1], colorbar_kwargs={'pad': 0.1})


def draw_contourf(model_name, report_time, report_time2, cst, file_list, var):
    obs_time_dc = '起报时次：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(report_time)
    fst_time_dc = '预报时次：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(report_time2)
    forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时平均值'.format(int(cst))
    if not os.path.exists(file_list[0]):
        logging.error('输入文件文件不存在: ' + file_list[0])
        return
    try:
        lat_lon_data = M4.open_m4_org(file_list[0])
        mask = mask_array
        lat_lon_data.data[mask == 0] = np.nan
        drw_dataArray = lat_lon_data.data
        for idx in range(len(REGION)):
            region_name, map_extent = REGION_NAME[idx], tuple(REGION[idx])
            output_dir = file_list[2]
            base_name = "{region}_{rp_T:%Y%m%d%H}.{cst:03d}.png".format(region=region_name, rp_T=report_time2, cst=cst)
            if os.path.exists(os.path.join(output_dir, base_name)):
                continue
            else:
                if region_name == 'CHN' or region_name == 'JNHN':
                    add_scs_value = True
                else:
                    add_scs_value = False
                if var in ['sf03', 'sf06', 'sf12']:
                    title = file_list[-1][0].format(model_name, int(var[-2:]))
                    file_list[-1][1] = file_list[-1][1].format(int(var[-2:]))
                    drw_dataArray = drw_dataArray * 1000
                else:
                    title = file_list[-1][0].format(model_name)
                    if var == 'sf24':
                        drw_dataArray = drw_dataArray * 1000
                    if model_name == 'NCEP' and var in ['pre24_hgt', 'pre03', 'pre06', 'pre12']:
                        drw_dataArray = drw_dataArray / 1000

                fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                                  add_south_china_sea=add_scs_value)
                drw = draw_compose.horizontal_compose(title=title, add_city=False,
                                                      description=forcast_info, add_tag=False, fig=fig, ax=ax,
                                                      output_dir=output_dir, png_name=base_name,
                                                      is_clean_plt=True, map_extent=map_extent)
                drw.ax.tick_params(labelsize=16)
                metdig_single_plot(file_list[-1], lat_lon_data, drw, lat_lon_data.data)
                drw.save()
    except Exception as e:
        print(e)

def draw_contourf_obs(report_time, report_time2, cst, file_list, var):
    file_stime = report_time + timedelta(hours=int(cst))
    file_etime = report_time2 + timedelta(hours=int(cst))
    forcast_info = '实况时间：{}年{}月{}日-{}年{}月{}日 {}时平均值'.format(
        file_stime.year, file_stime.month, file_stime.day,
        file_etime.year, file_etime.month, file_etime.day, file_etime.hour)
    if not os.path.exists(file_list[1]):
        logging.error('输入文件文件不存在: '+file_list[1])
        return
    try:
        try:
            lat_lon_data = M4.open_m4(file_list[1], encoding='GBK')
        except:
            lat_lon_data = M4.open_m4(file_list[1])

        lat_lon_data.data[mask_array_cldas == 0] = np.nan
        for idx in range(len(REGION)):
            region_name, map_extent = REGION_NAME[idx], tuple(REGION[idx])
            output_dir = file_list[3]
            base_name = "{region}_{rp_T:%Y%m%d%H}.000.png".format(region=region_name, rp_T=file_etime)
            if os.path.exists(os.path.join(output_dir, base_name)):
                logging.info('文件已存在')
                continue
            else:
                if region_name == 'CHN' or region_name == 'JNHN':
                    add_scs_value = True
                else:
                    add_scs_value = False
                if var in ['sf03', 'sf06', 'sf12']:
                    title = file_list[-1][0].format('CLDAS', int(var[-2:]))
                    file_list[-1][1] = file_list[-1][1].format(int(var[-2:]))
                else:
                    title = file_list[-1][0].format('CLDAS')

                fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                                  add_south_china_sea=add_scs_value)
                drw = draw_compose.horizontal_compose(title=title, add_city=False,
                                                      description=forcast_info, add_tag=False, fig=fig, ax=ax,
                                                      output_dir=output_dir, png_name=base_name,
                                                      is_clean_plt=True, map_extent=map_extent)
                drw.ax.tick_params(labelsize=16)
                metdig_single_plot(file_list[-1], lat_lon_data, drw, lat_lon_data.data)
                drw.save()
    except Exception as e:
        print(e)

def draw_contourf_pre_sf(model_name, report_time, report_time2, cst, file_list, var):
    obs_time_dc = '起报时次：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(report_time)
    fst_time_dc = '预报时次：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(report_time2)
    forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时平均值'.format(int(cst))
    file_name_dir, file_name_orgin = os.path.split(file_list[0])
    tp_file = os.path.join(file_name_dir, 'r'+file_name_orgin)
    sd_file = os.path.join(file_name_dir, 's'+file_name_orgin)
    if not os.path.exists(tp_file) or not os.path.exists(sd_file):
        logging.error('输入文件文件不存在')
        return
    try:
        lat_lon_data_tp = M4.open_m4(tp_file)
        lat_lon_data_sd = M4.open_m4(sd_file)
        mask = mask_array
        data_array_tp = lat_lon_data_tp.data
        data_array_sd = lat_lon_data_sd.data
        data_array_tp[mask == 0] = np.nan
        data_array_sd[mask == 0] = np.nan

        for idx in range(len(REGION)):
            region_name, map_extent = REGION_NAME[idx], tuple(REGION[idx])
            output_dir = file_list[2]
            base_name = "{region}_{rp_T:%Y%m%d%H}.{cst:03d}.png".format(region=region_name, rp_T=report_time2, cst=cst)
            if os.path.exists(os.path.join(output_dir, base_name)):
                logging.info('文件已存在')
                continue
            else:
                if region_name == 'CHN' or region_name == 'JNHN':
                    add_scs_value = True
                else:
                    add_scs_value = False
                title = file_list[-1][0].format(model_name)
                fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                                  add_south_china_sea=add_scs_value)
                drw = draw_compose.horizontal_compose(title=title, add_city=False,
                                                      description=forcast_info, add_tag=False, fig=fig, ax=ax,
                                                      output_dir=output_dir, png_name=base_name,
                                                      is_clean_plt=True, map_extent=map_extent)
                drw.ax.tick_params(labelsize=16)
                if var == 'pre_sf24':
                    metdig_multi_plot(file_list[-1], lat_lon_data_tp, drw, data_array_tp, data_array_sd)
                else:
                    metdig_tp_sd_class(file_list[-1], lat_lon_data_tp, drw, data_array_tp, data_array_sd)
                drw.save()
    except Exception as e:
        print(e)

def draw_contourf_gust(model_name, report_time, report_time2, cst, file_list, var):
    obs_time_dc = '起报时次：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(report_time)
    fst_time_dc = '预报时次：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(report_time2)
    forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时平均值'.format(int(cst))
    if not os.path.exists(file_list[0]):
        logging.error('输入文件文件不存在')
        return
    try:
        lat_lon_data = M4.open_m4(file_list[0])
        mask = mask_array
        data_array = lat_lon_data.data
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
            output_dir = file_list[1]
            base_name = "{region}_{rp_T:%Y%m%d%H}.{cst:03d}.png".format(region=region_name, rp_T=report_time2, cst=cst)
            if os.path.exists(os.path.join(output_dir, base_name)):
                logging.info('文件已存在')
                continue
            else:
                if region_name == 'CHN' or region_name == 'JNHN':
                    add_scs_value = True
                else:
                    add_scs_value = False

                title = file_list[-1][0].format(model_name)
                fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                                  add_south_china_sea=add_scs_value)
                drw = draw_compose.horizontal_compose(title=title, add_city=False,
                                                      description=forcast_info, add_tag=False, fig=fig, ax=ax,
                                                      output_dir=output_dir, png_name=base_name,
                                                      is_clean_plt=True, map_extent=map_extent)
                drw.ax.tick_params(labelsize=16)
                metdig_exwind_plot(file_list[-1], lat_lon_data, drw, data_array)
                drw.save()
    except Exception as e:
        print(e)

def draw_wind(model_name, report_time, report_time2, cst, file_list, var):
    nafp_file_name_dir, nafp_file_name_orgin = os.path.split(file_list[0])
    obs_file_name_dir, obs_file_name_orgin = os.path.split(file_list[1])
    u_nafp_file = os.path.join(nafp_file_name_dir, 'u' + nafp_file_name_orgin)
    v_nafp_file = os.path.join(nafp_file_name_dir, 'v' + nafp_file_name_orgin)
    u_obs_file = os.path.join(obs_file_name_dir, 'u' + obs_file_name_orgin)
    v_obs_file = os.path.join(obs_file_name_dir, 'v' + obs_file_name_orgin)
    try:
        u_nafp_data = get_org_data(u_nafp_file, model_name, report_time, cst, lev='')
        v_nafp_data = get_org_data(v_nafp_file, model_name, report_time, cst, lev='')
        pwp = PlotHgtWindProd_sg(model_name, u_nafp_data, v_nafp_data, None, None)
        for idx in range(len(REGION)):
            file_name = "{region}_{rp_T:%Y%m%d%H}.{cst:03d}.png".format(region=REGION_NAME[idx], rp_T=report_time2, cst=cst)
            file_path = os.path.join(file_list[2], file_name)
            if not os.path.exists(file_path):
                pwp.plot_hgt_wind_speed_sg(REGION_NAME[idx], REGION[idx], file_path)
    except Exception as e:
        logging.error('绘制模式预报风速图错误')
        print(e)
    try:
        u_obs_data = get_org_data(u_obs_file, 'CLDAS', report_time2, 0, lev='')
        v_obs_data = get_org_data(v_obs_file, 'CLDAS', report_time2, 0, lev='')
        pwp = PlotHgtWindProd_sg('CLDAS', u_obs_data, v_obs_data, None, None)
        for idx in range(len(REGION)):
            file_name = "{region}_{rp_T:%Y%m%d%H}.000.png".format(region=REGION_NAME[idx], rp_T=report_time2+timedelta(hours=int(cst)))
            file_path = os.path.join(file_list[3], file_name)
            if not os.path.exists(file_path):
                pwp.plot_hgt_wind_speed_sg(REGION_NAME[idx], REGION[idx], file_path)
    except Exception as e:
        logging.error('绘制实况风速图错误')
        print(e)


def single_plot(model_name, report_time, report_time2, cst, var):
    NAFP_PATH = "/data/cpvs/DataBase/MOD/{model}/{element}/{lev}/{report_time:%Y}/{report_time:%Y%m%d%H}/" \
                "{report_time2:%Y%m%d%H}.{cst:03d}"
    OBS_PATH = "/data/cpvs/DataBase/OBS/CLDAS/{element}/{lev}/{report_time:%Y}/{report_time:%Y%m%d%H}/" \
                "{report_time2:%Y%m%d%H}.000"
    NAFP_PNG_PATH = "/data/cpvs/Product/synoptic/{model}/{report_time:%Y%m%d%H}/{out_name}/{lev}"
    OBS_PNG_PATH = "/data/cpvs/Product/synoptic/CLDAS/{report_time:%Y%m%d%H}/{out_name}/{lev}"

    element_name = 'avg_' + var
    file_list = [NAFP_PATH.format(model=model_name, report_time=report_time, report_time2=report_time2, cst=cst,
                                  element=element_name, lev=''),
                 OBS_PATH.format(report_time=report_time + timedelta(hours=cst),
                                 report_time2=report_time2 + timedelta(hours=cst), element=element_name, lev=''),
                 os.path.dirname(NAFP_PNG_PATH).format(model=model_name, report_time=report_time, out_name=element_name,
                                                  lev=''),
                 os.path.dirname(OBS_PNG_PATH).format(report_time=report_time + timedelta(hours=cst),
                                                       out_name=element_name, lev=''),
                 Config_Info.get(var)]
    if var == 'pre_sf24' or var == 'pre_sf_class':
        draw_contourf_pre_sf(model_name, report_time, report_time2, cst, file_list, var)
    elif var == 'gustwind' or var == 'exwind_24':
        draw_contourf_gust(model_name, report_time, report_time2, cst, file_list, var)
    elif var == 'wind':
        draw_wind(model_name, report_time, report_time2, cst, file_list, var)
    else:
        draw_contourf(model_name, report_time, report_time2, cst, file_list, var)
        draw_contourf_obs(report_time, report_time2, cst, file_list, var)