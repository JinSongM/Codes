import logging
import os.path
import meteva.base as meb
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


# 绘制极大风
def metdig_exwind_plot(Infile_list, lat_lon_data, drw, data, cmap, extend):
    lats = np.linspace(lat_lon_data.start_lat, lat_lon_data.end_lat, lat_lon_data.lat_count)
    lons = np.linspace(lat_lon_data.start_lon, lat_lon_data.end_lon, lat_lon_data.lon_count)
    xr_data = xr.DataArray(data, coords=(lats, lons), dims=("lat", "lon"))
    std_data = metdig.utl.xrda_to_gridstda(xr_data, level_dim='level', time_dim='time', lat_dim='lat',
                                           lon_dim='lon', dtime_dim='dtime',
                                           var_name=Infile_list[3], np_input_units=Infile_list[4])
    contourf_method.contourf_2d(drw.ax, std_data, levels=Infile_list[5], cb_label=Infile_list[3], cb_ticks=[i+0.5 for i in Infile_list[5][:-1]],
                                extend=extend, cmap=cmap, alpha=1, colorbar_kwargs={'pad': 0.06, 'tick_label': Infile_list[5][1:]})

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

def single_model_tp(Infile_list, hour, region, is_overwrite):
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
        region_name, map_extent = region.replace(',', '_'), tuple([float(i) for i in region.split(',')])
        if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
            return

        if int(File_Name[-3:]) >= int(hour) and int(File_Name[-3:]) % 12 == 0:
            file_name_24 = '%.3f' % (float(file_name) - int(hour) / 1000)
            file_dir_24 = os.path.join(file_dir, str(file_name_24))
            lat_lon_data = M4.open_m4_org(Infile_list[0])
            if Infile_list[1].__contains__("NCEP"):
                if File_Name.split('.')[1] == '024':
                    lat_lon_data_24_data = np.zeros_like(lat_lon_data.data)
                else:
                    lat_lon_data_24_data = M4.open_m4_org(file_dir_24).data
                lat_lon_data_obs = (lat_lon_data.data - lat_lon_data_24_data) / 1000.0

            else:
                lat_lon_data_24_data = M4.open_m4_org(file_dir_24).data
                lat_lon_data_obs = lat_lon_data.data - lat_lon_data_24_data
            if Infile_list[1].__contains__("CMA_GFS"):
                mask = GFS_mask
            else:
                mask = mask_array
            lat_lon_data_obs[mask == 0] = np.nan
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

def single_model_tp_sd(Infile_list, hour, region, is_overwrite):
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
        region_name, map_extent = region.replace(',', '_'), tuple([float(i) for i in region.split(',')])
        if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
            return

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


def single_model_tp_sd_class(Infile_list, hour, region, is_overwrite):
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
        region_name, map_extent = region.replace(',', '_'), tuple([float(i) for i in region.split(',')])
        if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
            return

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


def single_model_Change(Infile_list, hour, step, region, is_overwrite):
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
        region_name, map_extent = region.replace(',', '_'), tuple([float(i) for i in region.split(',')])
        if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
            return

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
                if Infile_list[2].__contains__('降雪'):
                    lat_lon_data_obs = lat_lon_data_obs * 1000
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


def single_model_r2m(Infile_list, hour, region, is_overwrite):
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
        region_name, map_extent = region.replace(',', '_'), tuple([float(i) for i in region.split(',')])
        if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
            return

        if Infile_list[1].__contains__("ECMWF"):
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

        if region_name == 'CHN' or region_name == 'JNHN':
            add_scs_value = True
        else:
            add_scs_value = False
        fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                          add_south_china_sea=add_scs_value)
        drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info, add_tag=False,
                                              output_dir=Infile_list[1], add_city=False, fig=fig, ax=ax,
                                              is_clean_plt=True, map_extent=map_extent, is_overwrite=is_overwrite,
                                              png_name=region_name + '_' + File_Name + ".png")
        drw.ax.tick_params(labelsize=16)
        metdig_single_plot(Infile_list, lat_lon_data, drw, lat_lon_data_array, Infile_list[6])
        drw.save()
    except Exception as e:
        logging.info(e)


def single_model_t2m(Infile_list, hour, region, is_overwrite):
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
        region_name, map_extent = region.replace(',', '_'), tuple([float(i) for i in region.split(',')])
        if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
            return

        lat_lon_data = M4.open_m4(Infile_list[0])
        if Infile_list[1].__contains__("CMA_GFS"):
            mask = GFS_mask
        else:
            mask = mask_array
        lat_lon_data.data[mask == 0] = np.nan
        if region_name == 'CHN' or region_name == 'JNHN':
            add_scs_value = True
        else:
            add_scs_value = False
        fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                          add_south_china_sea=add_scs_value)
        drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info, add_tag=False,
                                              output_dir=Infile_list[1], add_city=False, fig=fig, ax=ax,
                                              is_clean_plt=True, map_extent=map_extent, is_overwrite=is_overwrite,
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

def single_model_t2m_min(Infile_list, Infile_list_t2m_High, hour, fc, region, is_overwrite):
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
        region_name, map_extent = region.replace(',', '_'), tuple([float(i) for i in region.split(',')])
        if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
            return

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
            if region_name == 'CHN' or region_name == 'JNHN':
                add_scs_value = True
            else:
                add_scs_value = False
            fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                              add_south_china_sea=add_scs_value)
            drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info, add_tag=False,
                                                  output_dir=Infile_list[1], add_city=False, fig=fig, ax=ax,
                                                  is_clean_plt=True, map_extent=map_extent, is_overwrite=is_overwrite,
                                                  png_name=region_name + '_' + File_Name + ".png")
            drw.ax.tick_params(labelsize=16)
            metdig_single_plot_temex(Infile_list, lat_lon_data, drw, data_array, Infile_list[6])
            drw.save()
            if fc == 'max':
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
                                                      add_city=False, fig=fig, ax=ax, is_overwrite=is_overwrite,
                                                      is_clean_plt=True, map_extent=map_extent,
                                                      png_name=region_name + '_' + File_Name + ".png")
                drw.ax.tick_params(labelsize=16)
                metdig_single_plot_filter(Infile_list_t2m_High, lat_lon_data, drw, data_array, Infile_list_t2m_High[6])
                drw.save()
    except Exception as e:
        logging.info(e)

def single_model_gustwind(Infile_list, hour, region, is_overwrite):
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
        region_name, map_extent = region.replace(',', '_'), tuple([float(i) for i in region.split(',')])
        if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
            return

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

            if region_name == 'CHN' or region_name == 'JNHN':
                add_scs_value = True
            else:
                add_scs_value = False
            fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                              add_south_china_sea=add_scs_value)
            drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info, add_tag=False,
                                                  output_dir=Infile_list[1], add_city=False, fig=fig, ax=ax,
                                                  is_clean_plt=True, map_extent=map_extent, is_overwrite=is_overwrite,
                                                  png_name=region_name + '_' + File_Name + ".png")
            drw.ax.tick_params(labelsize=16)
            metdig_exwind_plot(Infile_list, lat_lon_data, drw, data_array, Infile_list[6], extend='min')
            drw.save()
    except Exception as e:
        logging.info(e)

def single_model_exwind(Infile_list, hour, region, is_overwrite):
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
        region_name, map_extent = region.replace(',', '_'), tuple([float(i) for i in region.split(',')])
        if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
            return

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

            if region_name == 'CHN' or region_name == 'JNHN':
                add_scs_value = True
            else:
                add_scs_value = False
            fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                              add_south_china_sea=add_scs_value)
            drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info, add_tag=False,
                                                  output_dir=Infile_list[1], add_city=False, fig=fig, ax=ax,
                                                  is_clean_plt=True, map_extent=map_extent, is_overwrite=is_overwrite,
                                                  png_name=region_name + '_' + File_Name + ".png")
            drw.ax.tick_params(labelsize=16)
            metdig_exwind_plot(Infile_list, lat_lon_data, drw, data_array, Infile_list[6], extend='min')
            drw.save()
    except Exception as e:
        logging.info(e)


# 温度、相对湿度和降水（降水为累计）数据准备——CLDAS实况数据
def single_CLDAS_temC(Infile_list, hour, region, is_overwrite):
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
                    region_name, map_extent = region.replace(',', '_'), tuple([float(i) for i in region.split(',')])
                    if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
                        return
                    lat_lon_data = M4.open_m4(Infile_list[0], encoding='GBK')
                    lat_lon_data_24 = M4.open_m4(father_file, encoding='GBK')
                    lat_lon_data_obs = lat_lon_data.data - lat_lon_data_24.data
                    lat_lon_data_obs[mask_array_cldas == 0] = np.nan
                    if region_name == 'CHN' or region_name == 'JNHN':
                        add_scs_value = True
                    else:
                        add_scs_value = False
                    fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                                      add_south_china_sea=add_scs_value)
                    drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info,
                                                          fig=fig, ax=ax, is_overwrite=is_overwrite,
                                                          output_dir=Infile_list[1], add_city=False,
                                                          add_tag=False, is_clean_plt=True, map_extent=map_extent,
                                                          png_name=region_name + '_20' + File_Name + ".png")
                    drw.ax.tick_params(labelsize=16)
                    metdig_single_plot(Infile_list, lat_lon_data, drw, lat_lon_data_obs, Infile_list[6])
                    drw.save()
    except Exception as e:
        logging.info(e)


def single_CLDAS_tp(Infile_list, hour, region, is_overwrite):
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
                region_name, map_extent = region.replace(',', '_'), tuple([float(i) for i in region.split(',')])
                if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
                    return

                lat_lon_data = M4.open_m4(Infile_list[0], encoding='GBK')
                lat_lon_data.data[mask_array_cldas == 0] = np.nan
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


def single_CLDAS_other(Infile_list, hour, region, is_overwrite):
    File_Name = os.path.split(Infile_list[0])[1]
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])
    try:
        if os.path.exists(Infile_list[0]):
            file_time = os.path.basename(Infile_list[0]).split('.')[0]
            file_time_DATE = datetime.strptime(file_time, '%y%m%d%H')
            forcast_info = '实况时间：{}年{}月{}日{}时'.format(file_time_DATE.year, file_time_DATE.month, file_time_DATE.day,
                                                      file_time_DATE.hour)
            region_name, map_extent = region.replace(',', '_'), tuple([float(i) for i in region.split(',')])
            if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
                return
            lat_lon_data = M4.open_m4(Infile_list[0], encoding='GBK')
            lat_lon_data.data[mask_array_cldas == 0] = np.nan
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

def single_CLDAS_t2m_min(Infile_list, Infile_list_t2m_High, hour, fc, region, is_overwrite):
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

            region_name, map_extent = region.replace(',', '_'), tuple([float(i) for i in region.split(',')])
            if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
                return

            lat_lon_data = M4.open_m4(Infile_list[0], encoding='GBK')
            data_array = lat_lon_data.data
            data_array[mask_array_cldas == 0] = np.nan
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


def met_model_single_plot_tp(Infile_list, step, region, is_overwrite):
    File_Name = os.path.split(Infile_list[0])[1]
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])
    try:
        if os.path.exists(Infile_list[0]):
            file_dir, file_name = os.path.split(Infile_list[0])
            if int(file_name[-3:]) >= step and int(file_name[-3:]) % step == 0:
                file_name_24 = '%.3f' % (float(file_name) - step / 1000)
                file_dir_24 = os.path.join(file_dir, str(file_name_24))
                region_name, map_extent = region.replace(',', '_'), tuple([float(i) for i in region.split(',')])
                if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
                    return
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
    except Exception as e:
        logging.info(e)


def met_model_single_plot_tp_CLDAS(Infile_list, step, region, is_overwrite):
    File_Name = os.path.split(Infile_list[0])[1]
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])
    try:
        # if os.path.exists(Infile_list[0]):
        file_dir, file_name = os.path.split(Infile_list[0])
        father_file_dir = os.path.dirname(file_dir)
        region_name, map_extent = region.replace(',', '_'), tuple([float(i) for i in region.split(',')])
        if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png") and is_overwrite==False:
            return
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
def single_plot(argv):

    model_name = argv[0]
    report_time = datetime.strptime(argv[1], '%Y%m%d%H')
    cst = int(argv[2])
    var = argv[3]
    region = argv[4]
    if argv[6] == '1':
        is_overwrite = True
    else:
        is_overwrite = False

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
                    os.path.dirname(MODEL_SAVE_OUT).format(model=model_name, report_time=report_time,
                                                           out_name='tem_exmax', lev=''),
                    t2m_max_title.format(model_name), t2m_max_var, t2m_min_units, t2m_min_colorbar, cmap_tem_min
                    ]

    file_t2m_High = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='t2m', lev=''),
                os.path.dirname(MODEL_SAVE_OUT).format(model=model_name, report_time=report_time, out_name='tem_max',
                                                       lev=''),
                t2m_high_title.format(model_name), t2m_high_var, t2m_high_units, t2m_high_colorbar, cmap_tem_high
                ]

    file_temC = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='t2m', lev=''),
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

    file_sd = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='sd', lev=''),
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

    file_wind = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='gust', lev=''),
                 os.path.dirname(MODEL_SAVE_OUT).format(model=model_name, report_time=report_time,
                                                        out_name='gustwind', lev=''),
                 wind_title.format(model_name), wind_var, exwind_units, exwind_colorbar, cmap_exwind
                 ]

    file_exwind = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='gust', lev=''),
                   os.path.dirname(MODEL_SAVE_OUT).format(model=model_name, report_time=report_time,
                                                          out_name='exwind_24', lev=''),
                   exwind_title.format(model_name), exwind_var, exwind_units, exwind_colorbar, cmap_exwind
                   ]

    Dict_t2m = {'tem': [file_t2m, 3]}
    Dict_r2m = {'r': [file_r2m, 3]}
    Dict_tem_min = {'tem_min': [file_t2m_min, 24, 'min'], 'tem_exmax': [file_t2m_max, 24, 'max']}
    Dict_wind, Dict_exwind = {'gustwind': [file_wind, 3]}, {'exwind_24': [file_exwind, 24]}
    Dict_tp_sd_class, Dict_tp_sd = {'pre_sf_class': [file_tp_sd_class, 24]}, {'pre_sf24': [file_tp_sd, 24]}
    Dict_t2m_High = {'tem_max': [file_t2m_High, 3]}
    Dict_Change = {'tem_change': [file_temC, 24, 12], 'tem_change_48': [file_temC_48, 48, 12],
                   'sf03': [file_sd_3, 3, 3],
                   'sf06': [file_sd_6, 6, 6], 'sf12': [file_sd_12, 12, 12],
                   'sf24': [file_sd, 24, 12], 'pre24_cp': [file_cp, 24, 12], 'pre24_lsp': [file_lsp, 24, 12]}
    Dict_tp = {'pre24_hgt': [file_tp, 24]}
    Dict_tp_hour = {'pre03': [file_tp_3, 3], 'pre06': [file_tp_6, 6], 'pre12': [file_tp_12, 12],
                    'pre12_cp': [file_cp_12, 12]}
    if var in Dict_t2m.keys():
        single_model_t2m(Dict_t2m.get(var)[0], Dict_t2m.get(var)[1], region, is_overwrite)
    elif var in Dict_tem_min.keys():
        var1 = 'tem_max'
        single_model_t2m_min(Dict_tem_min.get(var)[0], Dict_t2m_High.get(var1)[0],
                             Dict_tem_min.get(var)[1], Dict_tem_min.get(var)[2], region, is_overwrite)
    elif var in Dict_wind.keys():
        single_model_gustwind(Dict_wind.get(var)[0], Dict_wind.get(var)[1], region, is_overwrite)
    elif var in Dict_exwind.keys():
        single_model_exwind(Dict_exwind.get(var)[0], Dict_exwind.get(var)[1], region, is_overwrite)
    elif var in Dict_tp_sd.keys():
        single_model_tp_sd(Dict_tp_sd.get(var)[0], Dict_tp_sd.get(var)[1], region, is_overwrite)
    elif var in Dict_tp_sd_class.keys():
        single_model_tp_sd_class(Dict_tp_sd_class.get(var)[0], Dict_tp_sd_class.get(var)[1], region, is_overwrite)
    elif var in Dict_r2m.keys():
        single_model_r2m(Dict_r2m.get(var)[0], Dict_r2m.get(var)[1], region, is_overwrite)
    elif var in Dict_t2m_High.keys():
        var1 = 'tem_exmax'
        single_model_t2m_min(Dict_tem_min.get(var1)[0], Dict_t2m_High.get(var)[0],
                             Dict_tem_min.get(var1)[1], Dict_tem_min.get(var1)[2], region, is_overwrite)
    elif var in Dict_Change.keys():
        single_model_Change(Dict_Change.get(var)[0], Dict_Change.get(var)[1],
                            Dict_Change.get(var)[2], region, is_overwrite)
    elif var in Dict_tp.keys():
        single_model_tp(Dict_tp.get(var)[0], Dict_tp.get(var)[1], region, is_overwrite)
    elif var in Dict_tp_hour.keys():
        met_model_single_plot_tp(Dict_tp_hour.get(var)[0], Dict_tp_hour.get(var)[1], region, is_overwrite)
    else:
        print('输入变量有误')


# 温度、变温、相对湿度和降水——CLDAS实况数据
def single_plot_CLDAS(argv):

    model_name = argv[0]
    report_time = datetime.strptime(argv[1], '%Y%m%d%H')
    cst = int(argv[2])
    var = argv[3]
    region = argv[4]
    if argv[6] == '1':
        is_overwrite = True
    else:
        is_overwrite = False

    CLDAS_t2m = [MODEL_ROOT_CLDAS.format(model=model_name, report_time=report_time, cst=cst, element='TMP', lev=''),
                 os.path.dirname(MODEL_SAVE_OUT_CLDAS).format(model=model_name, report_time=report_time,
                                                              out_name='tem', lev=''),
                 t2m_title.format(model_name), t2m_var, t2m_units, t2m_colorbar, cmap_tem
                 ]

    CLDAS_t2m_min = [
        MODEL_ROOT_CLDAS.format(model=model_name, report_time=report_time, cst=cst, element='MINIMUM_TEMPERATURE', lev=''),
        os.path.dirname(MODEL_SAVE_OUT_CLDAS).format(model=model_name, report_time=report_time,
                                                     out_name='tem_min', lev=''),
        t2m_min_title.format(model_name), t2m_min_var, t2m_min_units, t2m_min_colorbar, cmap_tem_min
    ]

    CLDAS_t2m_max = [
        MODEL_ROOT_CLDAS.format(model=model_name, report_time=report_time, cst=cst, element='MAXIMUM_TEMPERATURE', lev=''),
        os.path.dirname(MODEL_SAVE_OUT_CLDAS).format(model=model_name, report_time=report_time,
                                                     out_name='tem_exmax', lev=''),
        t2m_max_title.format(model_name), t2m_max_var, t2m_min_units, t2m_min_colorbar, cmap_tem_min
    ]

    CLDAS_t2m_High = [MODEL_ROOT_CLDAS.format(model=model_name, report_time=report_time, cst=cst, element='TMP', lev=''),
                 os.path.dirname(MODEL_SAVE_OUT_CLDAS).format(model=model_name, report_time=report_time,
                                                              out_name='tem_max', lev=''),
                t2m_high_title.format(model_name), t2m_high_var, t2m_high_units, t2m_high_colorbar, cmap_tem_high
                ]

    CLDAS_temC = [
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

    Dict_other = {'tem': [CLDAS_t2m, 3], 'r': [CLDAS_r2m, 3]}
    Dict_tem_min = {'tem_min': [CLDAS_t2m_min, 24, 'min'], 'tem_exmax': [CLDAS_t2m_max, 24, 'max']}
    Dict_temC = {'tem_change': [CLDAS_temC, 24], 'tem_change_48': [CLDAS_temC_48, 48]}
    Dict_t2m_High = {'tem_max': [CLDAS_t2m_High, 3]}
    Dict_tp = {'pre24_hgt': [CLDAS_tp, 24]}
    Dict_tp_hour = {'pre03': [CLDAS_tp_3, 3], 'pre06': [CLDAS_tp_6, 6], 'pre12': [CLDAS_tp_12, 12]}
    if var in Dict_other.keys():
        single_CLDAS_other(Dict_other.get(var)[0], Dict_other.get(var)[1], region, is_overwrite)
    elif var in Dict_temC.keys():
        single_CLDAS_temC(Dict_temC.get(var)[0], Dict_temC.get(var)[1], region, is_overwrite)
    elif var in Dict_t2m_High.keys():
        var1 = 'tem_exmax'
        single_CLDAS_t2m_min(Dict_tem_min.get(var1)[0], Dict_t2m_High.get(var)[0],
                             Dict_tem_min.get(var1)[1], Dict_tem_min.get(var1)[2], region, is_overwrite)
    elif var in Dict_tp.keys():
        single_CLDAS_tp(Dict_tp.get(var)[0], Dict_tp.get(var)[1], region, is_overwrite)
    elif var in Dict_tp_hour.keys():
        met_model_single_plot_tp_CLDAS(Dict_tp_hour.get(var)[0], Dict_tp_hour.get(var)[1], region, is_overwrite)
    elif var in Dict_tem_min.keys():
        var1 = 'tem_max'
        single_CLDAS_t2m_min(Dict_tem_min.get(var)[0], Dict_t2m_High.get(var1)[0],
                             Dict_tem_min.get(var)[1], Dict_tem_min.get(var)[2], region, is_overwrite)
    else:
        print('输入变量有误')


# 绘制模式预报风速图
def plot_wind_speed_single(argv):
    model_name = argv[0]
    report_time = datetime.strptime(argv[1], '%Y%m%d%H')
    cst = int(argv[2])
    region = argv[4]
    if argv[6] == '1':
        is_overwrite = True
    else:
        is_overwrite = False

    region_name, map_extent = region.replace(',', '_'), tuple([float(i) for i in region.split(',')])
    file_path = MODEL_SAVE_OUT.format(model=model_name, out_name=windspeend_name, report_time=report_time,
                                      cst=cst, lev='', region=region_name)
    u_data = get_org_data(model_name, report_time, cst, element="u10", lev='')
    v_data = get_org_data(model_name, report_time, cst, element="v10", lev='')
    if u_data is not None and v_data is not None:
        pwp = PlotHgtWindProd_sg(model_name, u_data, v_data, None, None)
        try:
            pwp.plot_hgt_wind_speed_sg(region_name, map_extent, file_path, is_overwrite=is_overwrite)
        except Exception as e:
            logging.info(e)
    else:
        logging.error('读取UV数据失败')

# 绘制CLDAS实况风速图
def plot_wind_speed_single_CLDAS(argv):
    model_name = argv[0]
    report_time = datetime.strptime(argv[1], '%Y%m%d%H')
    cst = int(argv[2])
    region = argv[4]
    if argv[6] == '1':
        is_overwrite = True
    else:
        is_overwrite = False

    region_name, map_extent = region.replace(',', '_'), tuple([float(i) for i in region.split(',')])
    file_path = MODEL_SAVE_OUT_CLDAS.format(model=model_name, out_name=windspeend_name, report_time=report_time,
                                            cst=cst, lev='', add='.000', region=region_name)
    u_data, v_data, u, v = get_org_data(model_name, report_time, cst, element="WIND", lev='')
    if u_data is not None and v_data is not None:
        pwp = PlotHgtWindProd_sg(model_name, u_data, v_data, u, v)
        try:
            pwp.plot_hgt_wind_speed_sg(region_name, map_extent, file_path, is_overwrite=is_overwrite)
        except Exception as e:
            logging.info(e)
    else:
        logging.error('读取UV数据失败')