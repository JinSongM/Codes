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
from metdig.graphics import draw_compose, contourf_method
import xarray as xr
import sys

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

path_GFS = os.path.join(os.path.dirname(__file__), "mask_NH25.dat")
path_Model = os.path.join(os.path.dirname(__file__), "mask_0p25.dat")
path_CLDAS = os.path.join(os.path.dirname(__file__), "mask_005.dat")


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


def single_plot(model_name, report_time, report_time2, cst):
    FILE_PATH = "/data/cpvs/DataBase/MOD/{model}/{element}/{lev}/{report_time:%Y}/{report_time:%Y%m%d%H}/" \
                "{report_time2:%Y%m%d%H}.{cst:03d}"
    PNG_PATH = "/data/cpvs/Product/synoptic/{model}/{report_time:%Y%m%d%H}/{out_name}/{lev}/" \
               "{region}_{report_time2:%Y%m%d%H}.{cst:03d}.png"
    file_tp = [FILE_PATH.format(model=model_name, report_time=report_time, report_time2=report_time2, cst=cst,
                                element='avg_pre24', lev=''),
               os.path.dirname(PNG_PATH).format(model=model_name, report_time=report_time,
                                                report_time2=report_time2,
                                                out_name='avg_pre24', lev='', cst=cst),
               tp_title.format(model_name), tp_var, tp_units, tp_colorbar, cmap_tp
               ]
    single_model_tp(file_tp, report_time, report_time2,cst)


def single_model_tp(Infile_list, report_time, report_time2, cst):
    print(1)
    File_Name = os.path.split(Infile_list[0])[1]
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])
    try:
        obs_time_dc = '开始时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(report_time)
        fst_time_dc = '结束时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(report_time2)
        forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时'.format(cst)
        lat_lon_data = M4.open_m4(Infile_list[0])

        if "NCEP" in Infile_list[1]:
            lat_lon_data_obs = lat_lon_data.data / 1000
        else:
            lat_lon_data_obs = lat_lon_data.data
        # if "CMA_GFS" in Infile_list[1]:
        #     mask = GFS_mask
        # else:
        #     mask = mask_array
        #
        # lat_lon_data_obs[mask == 0] = np.nan
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
                drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info,
                                                      add_tag=False,
                                                      output_dir=Infile_list[1], add_city=False, fig=fig, ax=ax,
                                                      is_clean_plt=True, map_extent=map_extent,
                                                      png_name=region_name + '_' + File_Name + ".png")
                drw.ax.tick_params(labelsize=16)
                metdig_single_plot(Infile_list, lat_lon_data, drw, lat_lon_data_obs, Infile_list[6])
                drw.save()
    except:
        print(File_Name)
