import os.path
import meteva.base as meb
from verify.config_single_Filter import *
import metdig
from metpy.units import units
from metpy import calc as mp_calc
from verify.plot_model_single import horizontal_pallete_test
from datetime import datetime, timedelta
import numpy as np
from utils import MICAPS4 as M4
from metdig.graphics import draw_compose, contourf_method
from verify.plot_model_single import PlotHgtWindProd_sg
import xarray as xr

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
LEV = [1000, 925, 850, 700, 500, 200, 100]

cmap_tp = ['#{:02x}{:02x}{:02x}'.format(*tuple(i)) for i in tp_color]
cmap_tp_hour = ['#{:02x}{:02x}{:02x}'.format(*tuple(i)) for i in tp_hour_color]
cmap_r = ['#{:02x}{:02x}{:02x}'.format(*tuple(i)) for i in r_color]
cmap_tem_change = ['#{:02x}{:02x}{:02x}'.format(*tuple(i)) for i in tem_change_color]
cmap_tem = 'guide/cs1'

def calc_relative_humidity(t_data, d_data):
    """

    :param t_data: 单位：℃
    :param d_data:单位：℃
    :return:
    """
    return np.array(mp_calc.relative_humidity_from_dewpoint(t_data * units.degC, d_data * units.degC),
                    dtype=float) * 100

def loss_data(file_path):
    name = os.path.split(file_path)[1][0:-4]
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'loss_data', name), 'a') as f:
        f.write(file_path)
        f.write('\r\n')
        f.close()

#掩膜数据
def read_mask():
    path_GFS = os.path.join(os.path.dirname(__file__), "mask_NH25.dat")
    path_Model = os.path.join(os.path.dirname(__file__), "mask_0p25.dat")
    path_CLDAS = os.path.join(os.path.dirname(__file__), "mask_005.dat")
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

#UV风数据读取
def get_org_data(model_name: str, report_time, cst, element, lev, scale=1):
    if model_name == 'CLDAS':
        file_path = MODEL_ROOT_CLDAS.format(model=model_name, report_time=report_time, cst=cst, element=element,
                                            lev=lev)
        if not os.path.exists(file_path):
            loss_data(file_path)
            return None
        lats, lons, array_U, array_V = M4.open_m11_uv(file_path)
        array_U[mask_array_cldas == 0] = np.nan
        array_V[mask_array_cldas == 0] = np.nan
        # lats_change = lats[::2]
        # lons_change = lons[::2]
        # u_change = array_U[::2,::2]
        # v_change = array_V[::2,::2]
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
            # u = xr.DataArray([[[[u_change * scale]]]],
            #                          coords=[[model_name.replace("_", "-")], [report_time], [cst], [int(lev)], lats_change,
            #                                  lons_change],
            #                          dims=["member", "time", "dtime", "level", "lat", "lon"])
            # v = xr.DataArray([[[[v_change * scale]]]],
            #                          coords=[[model_name.replace("_", "-")], [report_time], [cst], [int(lev)], lats_change,
            #                                  lons_change],
            #                          dims=["member", "time", "dtime", "level", "lat", "lon"])
        else:
            xr_data_u = xr.DataArray([[[array_U * scale]]],
                                     coords=[[model_name.replace("_", "-")], [report_time], [cst], lats, lons],
                                     dims=["member", "time", "dtime", "lat", "lon"])
            xr_data_v = xr.DataArray([[[array_V * scale]]],
                                     coords=[[model_name.replace("_", "-")], [report_time], [cst], lats, lons],
                                     dims=["member", "time", "dtime", "lat", "lon"])
            # u = xr.DataArray([[[u_change * scale]]],
            #                          coords=[[model_name.replace("_", "-")], [report_time], [cst], lats_change, lons_change],
            #                          dims=["member", "time", "dtime", "lat", "lon"])
            # v = xr.DataArray([[[v_change * scale]]],
            #                          coords=[[model_name.replace("_", "-")], [report_time], [cst], lats_change, lons_change],
            #                          dims=["member", "time", "dtime", "lat", "lon"])

        return xr_data_u, xr_data_v, None, None
    else:
        file_path = MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element=element, lev=lev)
        if not os.path.exists(file_path):
            loss_data(file_path)
            return None
        lat_lon_data = M4.open_m4(file_path)
        if model_name == "CMA_GFS" :
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

#绘制单要素空间分布图
def metdig_single_plot(Infile_list, lat_lon_data, drw, data, cmap):
    lats = np.linspace(lat_lon_data.start_lat, lat_lon_data.end_lat, lat_lon_data.lat_count)
    lons = np.linspace(lat_lon_data.start_lon, lat_lon_data.end_lon, lat_lon_data.lon_count)
    xr_data = xr.DataArray(data, coords=(lats, lons), dims=("lat", "lon"))
    std_data = metdig.utl.xrda_to_gridstda(xr_data, level_dim='level', time_dim='time', lat_dim='lat',
                                           lon_dim='lon', dtime_dim='dtime',
                                           var_name=Infile_list[3], np_input_units=Infile_list[4])
    contourf_method.contourf_2d(drw.ax, std_data, levels=Infile_list[5], cb_label=Infile_list[3], cmap=cmap, alpha=1, colorbar_kwargs = {'pad': 0.06})

def met_model_single_plot(Infile_list, region, hour, Filter_min=-9999.0, Filter_max=9999.0):
    File_Name = os.path.split(Infile_list[0])[1]
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])

    region_name, map_extent = region, tuple(REGION[REGION_NAME.index(region)])
    if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png"):
        os.remove(Infile_list[1] + region_name + '_' + File_Name + ".png")
    obs_time, step_time = os.path.basename(Infile_list[0]).split('.')
    OBS_time = datetime.strptime(obs_time, '%Y%m%d%H')
    FST_time = OBS_time + timedelta(hours=int(step_time))
    obs_time_dc = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(OBS_time)
    fst_time_dc = '预报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(FST_time)
    forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时'.format(int(step_time))
    fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info)
    drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info, add_tag=False,
                                          output_dir=Infile_list[1], add_city=False, fig=fig, ax=ax,
                                          is_clean_plt=True, map_extent=map_extent,
                                          png_name=region_name + '_' + File_Name + ".png")
    drw.ax.tick_params(labelsize=16)
    if '降水' in Infile_list[2] and '对流性' not in Infile_list[2] and '大尺度' not in Infile_list[2]:
        if "NCEP" in Infile_list[1]:
            file_dir, file_name = os.path.split(Infile_list[0])
            if int(File_Name[-3:]) >= 24 and int(File_Name[-3:]) % 12 == 0:
                file_name_24 = '%.3f' % (float(file_name) - 0.024)
                file_dir_24 = os.path.join(file_dir, str(file_name_24))
                if os.path.exists(file_dir_24):
                    lat_lon_data = M4.open_m4(Infile_list[0])
                    lat_lon_data_24 = M4.open_m4(file_dir_24)
                    lat_lon_data_obs = (lat_lon_data.data - lat_lon_data_24.data) / 1000
                    lat_lon_data_obs[mask_array == 0] = np.nan
                    lat_lon_data_obs[lat_lon_data_obs < Filter_min] = np.nan
                    lat_lon_data_obs[lat_lon_data_obs > Filter_max] = np.nan
                    metdig_single_plot(Infile_list, lat_lon_data, drw, lat_lon_data_obs, Infile_list[6])
                    drw.save()

        else:
            file_dir, file_name = os.path.split(Infile_list[0])
            if int(File_Name[-3:]) >= 24 and int(File_Name[-3:]) % 12 == 0:
                file_name_24 = '%.3f' % (float(file_name) - 0.024)
                file_dir_24 = os.path.join(file_dir, str(file_name_24))
                if os.path.exists(file_dir_24):
                    lat_lon_data = M4.open_m4(Infile_list[0])
                    lat_lon_data_24 = M4.open_m4(file_dir_24)
                    lat_lon_data_obs = lat_lon_data.data - lat_lon_data_24.data
                    if "CMA_GFS" in Infile_list[1]:
                        mask = GFS_mask
                    else:
                        mask = mask_array
                    lat_lon_data_obs[mask == 0] = np.nan
                    lat_lon_data_obs[lat_lon_data_obs < Filter_min] = np.nan
                    lat_lon_data_obs[lat_lon_data_obs > Filter_max] = np.nan
                    metdig_single_plot(Infile_list, lat_lon_data, drw, lat_lon_data_obs, Infile_list[6])
                    drw.save()

    elif '变' in Infile_list[2] or '降雪' in Infile_list[2] or '对流性' in Infile_list[2] or '大尺度' in Infile_list[2]:
        file_dir, file_name = os.path.split(Infile_list[0])
        if int(File_Name[-3:]) >= int(hour) and int(File_Name[-3:]) % 12 == 0:
            file_name_24 = '%.3f' % (float(file_name) - int(hour) / 1000)
            file_dir_24 = os.path.join(file_dir, str(file_name_24))
            if os.path.exists(file_dir_24):
                lat_lon_data = M4.open_m4(Infile_list[0])
                lat_lon_data_24 = M4.open_m4(file_dir_24)
                lat_lon_data_obs = lat_lon_data.data - lat_lon_data_24.data
                if "CMA_GFS" in Infile_list[1]:
                    mask = GFS_mask
                else:
                    mask = mask_array
                lat_lon_data_obs[mask == 0] = np.nan
                if '降雪' in Infile_list[2]:
                    lat_lon_data_obs = lat_lon_data_obs * 1000
                lat_lon_data_obs[lat_lon_data_obs < Filter_min] = np.nan
                lat_lon_data_obs[lat_lon_data_obs > Filter_max] = np.nan
                metdig_single_plot(Infile_list, lat_lon_data, drw, lat_lon_data_obs, Infile_list[6])
                drw.save()

    elif '相对湿度' in Infile_list[2]:
        if "ECMWF" in Infile_list[1]:
            t2m_array = get_org_data(Infile_list[-1][0], Infile_list[-1][1], Infile_list[-1][2], element="t2m",
                                     lev='')
            d2m_array = get_org_data(Infile_list[-1][0], Infile_list[-1][1], Infile_list[-1][2], element="d2m",
                                     lev='')
            lat_lon_value = calc_relative_humidity(t2m_array, d2m_array)
            Infile_list[0] = Infile_list[0].replace('r2m', 't2m')
            if os.path.exists(Infile_list[0]):
                lat_lon_data = M4.open_m4(Infile_list[0])
                lat_lon_value_array = lat_lon_value[0][0][0]
                lat_lon_value_array[lat_lon_value_array < Filter_min] = np.nan
                lat_lon_value_array[lat_lon_value_array > Filter_max] = np.nan
                metdig_single_plot(Infile_list, lat_lon_data, drw, lat_lon_value_array, Infile_list[6])
                drw.save()

        else:
            lat_lon_data = M4.open_m4(Infile_list[0])
            if "CMA_GFS" in Infile_list[1]:
                mask = GFS_mask
            else:
                mask = mask_array
            lat_lon_data.data[mask == 0] = np.nan
            lat_lon_data.data[lat_lon_data.data < Filter_min] = np.nan
            lat_lon_data.data[lat_lon_data.data > Filter_max] = np.nan
            metdig_single_plot(Infile_list, lat_lon_data, drw, lat_lon_data.data, Infile_list[6])
            drw.save()

    elif '高温' in Infile_list[2]:
        if os.path.exists(Infile_list[0]):
            lat_lon_data = M4.open_m4(Infile_list[0])
            if "CMA_GFS" in Infile_list[1]:
                mask = GFS_mask
            else:
                mask = mask_array
            lat_lon_data.data[mask == 0] = np.nan
            lat_lon_data.data[lat_lon_data.data < 35] = np.nan
            lat_lon_data.data[lat_lon_data.data < Filter_min] = np.nan
            lat_lon_data.data[lat_lon_data.data > Filter_max] = np.nan
            metdig_single_plot(Infile_list, lat_lon_data, drw, lat_lon_data.data, Infile_list[6])
            drw.save()

    else:
        lat_lon_data = M4.open_m4(Infile_list[0])
        if "CMA_GFS" in Infile_list[1]:
            mask = GFS_mask
        else:
            mask = mask_array
        lat_lon_data.data[mask == 0] = np.nan
        lat_lon_data.data[lat_lon_data.data < Filter_min] = np.nan
        lat_lon_data.data[lat_lon_data.data > Filter_max] = np.nan
        metdig_single_plot(Infile_list, lat_lon_data, drw, lat_lon_data.data, Infile_list[6])
        drw.save()

#温度、相对湿度和降水（降水为累计）数据准备——CLDAS实况数据
def met_model_single_plot_CLDAS(Infile_list, region, hour, Filter_min=-9999.0, Filter_max=9999.0):
    File_Name = os.path.split(Infile_list[0])[1]
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])
    if os.path.exists(Infile_list[0]):
        region_name, map_extent = region, tuple(REGION[REGION_NAME.index(region)])
        if  os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png"):
            os.remove(Infile_list[1] + region_name + '_' + File_Name + ".png")
        file_time = os.path.basename(Infile_list[0]).split('.')[0]
        if '变' in Infile_list[2]:
            file_dir, file_name = os.path.split(Infile_list[0])
            father_file_dir = os.path.dirname(file_dir)
            father_file_dir_name = (datetime.strptime(str(int(os.path.split(file_dir)[1])), '%Y%m%d') - timedelta(
                    days=int(hour / 24))).strftime('%Y%m%d')
            father_file_name = father_file_dir_name + file_name[-6:]
            father_file = os.path.join(father_file_dir, father_file_dir_name, father_file_name)
            file_time_end = datetime.strptime(file_time, '%Y%m%d%H')
            file_time_start = file_time_end - timedelta(days=int(hour / 24))
            forcast_info = '实况时间：{}年{}月{}日{}时-{}年{}月{}日{}时'.format(file_time_start.year, file_time_start.month,
                                                                   file_time_start.day, file_time_start.hour,
                                                                   file_time_end.year, file_time_end.month,
                                                                   file_time_end.day, file_time_end.hour)
            fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info)
            drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info, fig=fig, ax=ax,
                                                  output_dir=Infile_list[1], add_city=False, add_tag=False,
                                                  is_clean_plt=True, map_extent=map_extent,
                                                  png_name=region_name + '_' + File_Name + ".png")
            drw.ax.tick_params(labelsize=16)
            if father_file_name[-6:-4] == '08' or father_file_name[-6:-4] == '20':
                if os.path.exists(father_file) and os.path.exists(Infile_list[0]):
                    lat_lon_data = M4.open_m4(Infile_list[0], encoding='GBK')
                    lat_lon_data_24 = M4.open_m4(father_file, encoding='GBK')
                    lat_lon_data_obs = lat_lon_data.data - lat_lon_data_24.data
                    lat_lon_data_obs[mask_array_cldas == 0] = np.nan
                    lat_lon_data_obs[lat_lon_data_obs < Filter_min] = np.nan
                    lat_lon_data_obs[lat_lon_data_obs > Filter_max] = np.nan
                    metdig_single_plot(Infile_list, lat_lon_data, drw, lat_lon_data_obs, Infile_list[6])
                    drw.save()

        elif '降水' in Infile_list[2]:
            file_time_end = datetime.strptime(file_time, '%y%m%d%H')
            file_time_start = file_time_end - timedelta(days=1)
            forcast_info = '实况时间：{}年{}月{}日{}时-{}年{}月{}日{}时'.format(file_time_start.year, file_time_start.month,
                                                                   file_time_start.day, file_time_start.hour,
                                                                   file_time_end.year, file_time_end.month,
                                                                   file_time_end.day, file_time_end.hour)
            fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info)
            drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info, fig=fig, ax=ax,
                                                  output_dir=Infile_list[1], add_city=False,
                                                  is_clean_plt=True, map_extent=map_extent,
                                                  png_name=region_name + '_20' + File_Name + ".png", add_tag=False)
            drw.ax.tick_params(labelsize=16)
            file_dir, file_name = os.path.split(Infile_list[0])
            if file_name[-6:-4] == '08' or file_name[-6:-4] == '20':
                if os.path.exists(Infile_list[0]):
                    lat_lon_data = M4.open_m4(Infile_list[0], encoding='GBK')
                    lat_lon_data.data[mask_array_cldas == 0] = np.nan
                    lat_lon_data.data[lat_lon_data.data < Filter_min] = np.nan
                    lat_lon_data.data[lat_lon_data.data > Filter_max] = np.nan
                    metdig_single_plot(Infile_list, lat_lon_data, drw, lat_lon_data.data, Infile_list[6])
                    drw.save()

        elif '高温' in Infile_list[2]:
            file_time_DATE = datetime.strptime(file_time, '%Y%m%d%H')
            forcast_info = '实况时间：{}年{}月{}日{}时'.format(file_time_DATE.year, file_time_DATE.month, file_time_DATE.day, file_time_DATE.hour)
            fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info)
            drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info, fig=fig, ax=ax,
                                                  output_dir=Infile_list[1], add_city=False, add_tag=False,
                                                  is_clean_plt=True, map_extent=map_extent,
                                                  png_name=region_name + '_' + File_Name + ".png")
            drw.ax.tick_params(labelsize=16)
            if os.path.exists(Infile_list[0]):
                lat_lon_data = M4.open_m4(Infile_list[0], encoding='GBK')
                lat_lon_data.data[mask_array_cldas == 0] = np.nan
                lat_lon_data.data[lat_lon_data.data < 35] = np.nan
                lat_lon_data.data[lat_lon_data.data < Filter_min] = np.nan
                lat_lon_data.data[lat_lon_data.data > Filter_max] = np.nan
                metdig_single_plot(Infile_list, lat_lon_data, drw, lat_lon_data.data, Infile_list[6])
                drw.save()

        else:
            file_time_DATE = datetime.strptime(file_time, '%Y%m%d%H')
            forcast_info = '实况时间：{}年{}月{}日{}时'.format(file_time_DATE.year, file_time_DATE.month, file_time_DATE.day, file_time_DATE.hour)
            fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info)
            drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info, fig=fig, ax=ax,
                                                  output_dir=Infile_list[1], add_city=False, add_tag=False,
                                                  is_clean_plt=True, map_extent=map_extent,
                                                  png_name=region_name + '_' + File_Name + ".png")
            drw.ax.tick_params(labelsize=16)
            if os.path.exists(Infile_list[0]):
                lat_lon_data = M4.open_m4(Infile_list[0], encoding='GBK')
                lat_lon_data.data[mask_array_cldas == 0] = np.nan
                metdig_single_plot(Infile_list, lat_lon_data, drw, lat_lon_data.data, Infile_list[6])
                drw.save()

def met_model_single_plot_tp(Infile_list, step, region, Filter_min=-9999.0, Filter_max=9999.0):
    File_Name = os.path.split(Infile_list[0])[1]
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])
    if os.path.exists(Infile_list[0]):
        for idx in range(len(REGION)):
            region_name, map_extent = region, tuple(REGION[REGION_NAME.index(region)])
            if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png"):
                os.remove(Infile_list[1] + region_name + '_' + File_Name + ".png")
            obs_time, step_time = os.path.basename(Infile_list[0]).split('.')
            if step_time != '000':
                OBS_time = datetime.strptime(obs_time, '%Y%m%d%H')
                FST_time = OBS_time + timedelta(hours=int(step_time))
                obs_time_dc = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(OBS_time)
                fst_time_dc = '预报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(FST_time)
                forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时'.format(int(step_time))
                fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info)
                png_name = region_name + '_' + File_Name + ".png"
                drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info, add_tag=False,
                                                      output_dir=Infile_list[1], add_city=False, fig=fig, ax=ax,
                                                      is_clean_plt=True, map_extent=map_extent,
                                                      png_name=png_name)
                drw.ax.tick_params(labelsize=16)
                file_dir, file_name = os.path.split(Infile_list[0])
                if int(file_name[-3:]) >= step and int(file_name[-3:]) % step == 0:
                    file_name_24 = '%.3f' % (float(file_name) - step / 1000)
                    file_dir_24 = os.path.join(file_dir, str(file_name_24))
                    if os.path.exists(file_dir_24):
                        lat_lon_data = M4.open_m4(Infile_list[0])
                        lat_lon_data_24 = M4.open_m4(file_dir_24)
                        lat_lon_data_obs = lat_lon_data.data - lat_lon_data_24.data
                        if '对流性' not in Infile_list[2]:
                            if "NCEP" in Infile_list[1]:
                                lat_lon_data_obs = lat_lon_data_obs / 1000
                        if "CMA_GFS" in Infile_list[1]:
                            mask = GFS_mask
                        else:
                            mask = mask_array
                        lat_lon_data_obs[mask == 0] = np.nan
                        lat_lon_data_obs[lat_lon_data_obs < Filter_min] = np.nan
                        lat_lon_data_obs[lat_lon_data_obs > Filter_max] = np.nan
                        metdig_single_plot(Infile_list, lat_lon_data, drw, lat_lon_data_obs, Infile_list[6])
                        drw.save()
                    else:
                        continue
                else:
                    continue
            else:
                continue

def met_model_single_plot_tp_CLDAS(Infile_list, step, region, Filter_min=-9999.0, Filter_max=9999.0):
    File_Name = os.path.split(Infile_list[0])[1]
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])
    if os.path.exists(Infile_list[0]):
        region_name, map_extent = region, tuple(REGION[REGION_NAME.index(region)])
        if os.path.exists(Infile_list[1] + region_name + '_' + File_Name + ".png"):
            os.remove(Infile_list[1] + region_name + '_' + File_Name + ".png")
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
            data_tmp = M4.open_m4(father_file).data
            data_tmp[data_tmp == 9999] = np.nan
            lat_lon_data += data_tmp
            freq += 1
        if freq == step - 1:
            lat_lon_data[mask_array_cldas == 0] = np.nan
            file_time_end = datetime.strptime(str(os.path.splitext(file_name)[0]), '%y%m%d%H')
            file_time_start = datetime.strptime(str(os.path.splitext(file_name)[0]), '%y%m%d%H') - timedelta(
                hours=step)
            forcast_info = '实况时间：{}年{}月{}日{}时-{}年{}月{}日{}时'.format(file_time_start.year,
                                                                   file_time_start.month,
                                                                   file_time_start.day,
                                                                   file_time_start.hour,
                                                                   file_time_end.year, file_time_end.month,
                                                                   file_time_end.day, file_time_end.hour)
            fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info)
            drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info, fig=fig,
                                                  ax=ax,
                                                  output_dir=Infile_list[1], add_city=False,
                                                  is_clean_plt=True, map_extent=map_extent,
                                                  png_name=region_name + '_20' + File_Name + ".png",
                                                  add_tag=False)
            drw.ax.tick_params(labelsize=16)
            lat_lon_data[lat_lon_data < Filter_min] = np.nan
            lat_lon_data[lat_lon_data > Filter_max] = np.nan
            metdig_single_plot(Infile_list, lat_lon, drw, lat_lon_data, Infile_list[6])
            drw.save()

# 温度、变温、相对湿度和降水——模式预报数据
def single_plot(argv):

    model_name = argv[0]
    report_time = datetime.strptime(argv[1], '%Y%m%d%H')
    cst = int(argv[2])
    var = argv[3]
    region = argv[4]
    Filter_min = float(argv[5])
    Filter_max = float(argv[6])

    file_t2m = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='t2m', lev=''),
                os.path.dirname(MODEL_SAVE_OUT).format(model=model_name, report_time=report_time, out_name='tem',
                                                       lev=''),
                t2m_title.format(model_name), t2m_var, t2m_units, t2m_colorbar, cmap_tem
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

    Dict = {'tem': file_t2m, 'tem_max': file_t2m_High, 'tem_change': file_temC, 'tem_change_48': file_temC_48, 'r': file_r2m,
            'pre24_hgt': file_tp, 'sf24': file_sd, 'pre24_cp': file_cp, 'pre24_lsp': file_lsp}
    Dict_Hour = {'tem': 3, 'tem_max': 3, 'tem_change': 24, 'tem_change_48': 48, 'r': 3, 'pre24_hgt': 24, 'sf24': 24,
                 'pre24_cp': 24, 'pre24_lsp': 24}

    Dict_tp = {'pre03': [file_tp_3, 3], 'pre06': [file_tp_6, 6], 'pre12': [file_tp_12, 12], 'pre12_cp': [file_cp_12, 12]}
    if var in Dict.keys() and var in Dict_Hour.keys():
        met_model_single_plot(Dict.get(var), region, Dict_Hour.get(var), Filter_min, Filter_max)
    elif var in Dict_tp.keys():
        met_model_single_plot_tp(Dict_tp.get(var)[0], Dict_tp.get(var)[1], region, Filter_min, Filter_max)

# 温度、变温、相对湿度和降水——CLDAS实况数据
def single_plot_CLDAS(argv):

    model_name = argv[0]
    report_time = datetime.strptime(argv[1], '%Y%m%d%H')
    cst = int(argv[2])
    var = argv[3]
    region = argv[4]
    Filter_min = float(argv[5])
    Filter_max = float(argv[6])

    CLDAS_t2m = [MODEL_ROOT_CLDAS.format(model=model_name, report_time=report_time, cst=cst, element='TMP', lev=''),
                 os.path.dirname(MODEL_SAVE_OUT_CLDAS).format(model=model_name, report_time=report_time,
                                                              out_name='tem', lev=''),
                 t2m_title.format(model_name), t2m_var, t2m_units, t2m_colorbar, cmap_tem
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

    Dict = {'tem': CLDAS_t2m, 'tem_max': CLDAS_t2m_High, 'tem_change': CLDAS_temC, 'tem_change_48': CLDAS_temC_48,
            'r': CLDAS_r2m, 'pre24_hgt': CLDAS_tp}
    Dict_Hour = {'tem': 3, 'tem_max': 3, 'tem_change': 24, 'tem_change_48': 48, 'r': 3, 'pre24_hgt': 24}
    Dict_tp = {'pre03': [CLDAS_tp_3, 3], 'pre06': [CLDAS_tp_6, 6], 'pre12': [CLDAS_tp_12, 12]}
    if var in Dict.keys() and var in Dict_Hour.keys():
        met_model_single_plot_CLDAS(Dict.get(var), region, Dict_Hour.get(var), Filter_min, Filter_max)
    elif var in Dict_tp.keys():
        met_model_single_plot_tp_CLDAS(Dict_tp.get(var)[0], Dict_tp.get(var)[1], region, Filter_min, Filter_max)


# 绘制模式预报风速图
def plot_wind_speed_single(argv):
    model_name = argv[0]
    report_time = datetime.strptime(argv[1], '%Y%m%d%H')
    cst = int(argv[2])
    region = argv[4]
    Filter_min = float(argv[5])
    Filter_max = float(argv[6])

    region_name, map_extent = region, tuple(REGION[REGION_NAME.index(region)])
    file_path = MODEL_SAVE_OUT.format(model=model_name, out_name=windspeend_name, report_time=report_time,
                                      cst=cst, lev='', region=region_name)
    if os.path.exists(file_path):
        os.remove(file_path)
    u_data = get_org_data(model_name, report_time, cst, element="u10", lev='')
    v_data = get_org_data(model_name, report_time, cst, element="v10", lev='')
    pwp = PlotHgtWindProd_sg(model_name, u_data, v_data, None, None)
    pwp.plot_hgt_wind_speed_sg(region_name, map_extent, file_path, Filter_min, Filter_max)

# 绘制CLDAS实况风速图
def plot_wind_speed_single_CLDAS(argv):
    model_name = argv[0]
    report_time = datetime.strptime(argv[1], '%Y%m%d%H')
    cst = int(argv[2])
    region = argv[4]
    Filter_min = float(argv[5])
    Filter_max = float(argv[6])

    region_name, map_extent = region, tuple(REGION[REGION_NAME.index(region)])
    file_path = MODEL_SAVE_OUT_CLDAS.format(model=model_name, out_name=windspeend_name, report_time=report_time,
                                            cst=cst, lev='', add='.000', region=region_name)
    if os.path.exists(file_path):
        os.remove(file_path)
    u_data, v_data, u, v = get_org_data(model_name, report_time, cst, element="WIND", lev='')
    pwp = PlotHgtWindProd_sg(model_name, u_data, v_data, u, v)
    pwp.plot_hgt_wind_speed_sg(region, map_extent, file_path, Filter_min, Filter_max)