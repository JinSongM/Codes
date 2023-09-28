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

cmap_tp = ['#{:02x}{:02x}{:02x}'.format(*tuple(i)) for i in tp_color]
cmap_tp_hour = ['#{:02x}{:02x}{:02x}'.format(*tuple(i)) for i in tp_hour_color]
cmap_r = ['#{:02x}{:02x}{:02x}'.format(*tuple(i)) for i in r_color]
cmap_tem_change = ['#{:02x}{:02x}{:02x}'.format(*tuple(i)) for i in tem_change_color]
cmap_tem = 'guide/cs1'

def creat_m4(start_lon, end_lon, start_lat, end_lat, res, lat_lon_data):
    # 构建m4标准格式
    grid0 = meb.grid([start_lon, end_lon, res], [start_lat, end_lat, res])
    data = lat_lon_data
    grd = meb.grid_data(grid0, data=data)
    meb.set_griddata_coords(grd)
    return grd

def calc_relative_humidity(t_data, d_data):
    """

    :param t_data: 单位：℃
    :param d_data:单位：℃
    :return:
    """
    return np.array(mp_calc.relative_humidity_from_dewpoint(t_data * units.degC, d_data * units.degC),
                    dtype=float) * 100

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

#重采样
def Interp_gg_linear(cldas_grd, lat_lon_data, mask):
    grid_w = meb.grid([lat_lon_data.start_lon, lat_lon_data.end_lon, 0.25],
                      [lat_lon_data.start_lat, lat_lon_data.end_lat, 0.25])
    lat_lon_data_cldas = cldas_grd
    grd = meb.interp_gg_linear(lat_lon_data_cldas, grid_w, outer_value=0).data[0][0][0][0]
    grd[mask == 0] = np.nan
    return grd

#计算模式与实况差
def cal_df(CLDAS_grd, file_time_DATE, file_df, map_extent, region_name, num=-99):
    if file_df[-2] == 'CMA_GFS':
        mask = GFS_mask
    else:
        mask = mask_array
    model_time = file_time_DATE - timedelta(hours=file_df[-1])
    model_path = file_df[0].format(model=file_df[-2], element= file_df[-4], lev='', report_time=model_time, cst=file_df[-1])
    df_title = file_df[2].format(file_df[-2])
    obs_time_dc = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(model_time)
    fst_time_dc = '预报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(file_time_DATE)
    forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时'.format(int(file_df[-1]))
    model_out_path = file_df[1].format(model=file_df[-2], report_time=model_time, out_name=file_df[-3], lev='')
    if not os.path.exists(model_out_path):
        os.makedirs(model_out_path)
    if '变' in file_df[2] or '降水' in file_df[2]:
        if file_df[-1] >= 24 and file_df[-1] % 12 == 0:
            model_path_sub = file_df[0].format(model=file_df[-2], element=file_df[-4], lev='', report_time=model_time, cst=file_df[-1]-24)
            if os.path.exists(model_path_sub) and os.path.exists(model_path):
                model_data_far = M4.open_m4(model_path)
                model_data_sub = M4.open_m4(model_path_sub)
                model_data = model_data_far.data - model_data_sub.data
                if '降水' in file_df[2]:
                    if file_df[-2] == 'NCEP':
                        model_data = model_data / 1000
                model_data[mask == 0] = np.nan
                cldas_data = Interp_gg_linear(CLDAS_grd, model_data_far, mask)
                df_data = model_data - cldas_data
                df_data[(df_data > -0.1) & (df_data < 0.1)] = np.nan
                fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info)
                drw = draw_compose.horizontal_compose(title=df_title, description=forcast_info,
                                                      add_tag=False, output_dir=model_out_path,
                                                      add_city=False, fig=fig, ax=ax,
                                                      is_clean_plt=True, map_extent=map_extent,
                                                      png_name=region_name + '_' +
                                                               os.path.split(model_path)[1] + ".png")
                metdig_single_plot(file_df, model_data_far, drw, df_data, file_df[-5])
                drw.save()
    else:
        if os.path.exists(model_path):
            model_data = M4.open_m4(model_path)
            model_data.data[mask == 0] = np.nan
            model_data.data[model_data.data < num] = np.nan
            cldas_data = Interp_gg_linear(CLDAS_grd, model_data, mask)
            df_data = model_data.data - cldas_data
            df_data[df_data == 0] = np.nan
            fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info)
            drw = draw_compose.horizontal_compose(title=df_title, description=forcast_info,
                                                  add_tag=False, output_dir=model_out_path,
                                                  add_city=False, fig=fig, ax=ax,
                                                  is_clean_plt=True, map_extent=map_extent,
                                                  png_name=region_name + '_' +
                                                           os.path.split(model_path)[1] + ".png")
            metdig_single_plot(file_df, model_data, drw, df_data, file_df[-5])
            drw.save()

def cal_df_tp(CLDAS_grd, file_time_end, file_df, map_extent, region_name):
    try:
        model_time = file_time_end - timedelta(hours=file_df[-1])
        model_path = file_df[0].format(model=file_df[-2], element='tp', lev='', report_time=model_time, cst=file_df[-1])
        model_path_sub = file_df[0].format(model=file_df[-2], element='tp', lev='', report_time=model_time, cst=file_df[-1] - 3)
        if os.path.exists(model_path) and os.path.exists(model_path_sub):
            df_title = file_df[2].format(file_df[-2])
            obs_time_dc = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(model_time)
            fst_time_dc = '预报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(file_time_end)
            forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时'.format(int(file_df[-1]))
            model_out_path = file_df[1].format(model=file_df[-2], report_time=model_time, out_name=file_df[-3],
                                               lev='')
            if not os.path.exists(model_out_path):
                os.makedirs(model_out_path)
            model_data_far = M4.open_m4(model_path)
            model_data_sub = M4.open_m4(model_path_sub)
            model_data = model_data_far.data - model_data_sub.data
            # if file_df[-2] == 'CMA_TYM' or file_df[-2] == 'NCEP':
            #     model_data = model_data / 1000
            if file_df[-2] == 'CMA_GFS':
                mask = GFS_mask
            else:
                mask = mask_array
            model_data[mask == 0] = np.nan
            cldas_data = Interp_gg_linear(CLDAS_grd, model_data_far, mask)
            df_data = model_data - cldas_data
            df_data[df_data == 0] = np.nan
            fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info)
            drw = draw_compose.horizontal_compose(title=df_title, description=forcast_info,
                                                  add_tag=False, output_dir=model_out_path,
                                                  add_city=False, fig=fig, ax=ax,
                                                  is_clean_plt=True, map_extent=map_extent,
                                                  png_name=region_name + '_' +
                                                           os.path.split(model_path)[1] + ".png")
            metdig_single_plot(file_df, model_data_far, drw, df_data, file_df[-4])
            drw.save()
    except:
        print('差值图绘制失败')

def loss_data(file_path):
    name = os.path.split(file_path)[1][0:-4]
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'loss_data', name), 'a') as f:
        f.write(file_path)
        f.write('\r\n')
        f.close()

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

#温度、相对湿度和降水（降水为累计）数据准备——CLDAS实况数据
def met_model_single_plot_CLDAS(Infile_list, region, hour, Infile_list_df):
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])
    if os.path.exists(Infile_list[0]):
        region_name, map_extent = region, tuple(REGION[REGION_NAME.index(region)])
        file_time = os.path.basename(Infile_list[0]).split('.')[0]
        if '变' in Infile_list[2]:
            file_dir, file_name = os.path.split(Infile_list[0])
            father_file_dir = os.path.dirname(file_dir)
            father_file_dir_name = (datetime.strptime(str(int(os.path.split(file_dir)[1])), '%Y%m%d') - timedelta(
                    days=int(hour / 24))).strftime('%Y%m%d')
            father_file_name = father_file_dir_name + file_name[-6:]
            father_file = os.path.join(father_file_dir, father_file_dir_name, father_file_name)
            if father_file_name[-6:-4] == '08' or father_file_name[-6:-4] == '20':
                if os.path.exists(father_file) and os.path.exists(Infile_list[0]):
                    file_time_end = datetime.strptime(file_time, '%Y%m%d%H')
                    lat_lon_data = M4.open_m4(Infile_list[0], encoding='GBK')
                    lat_lon_data_24 = M4.open_m4(father_file, encoding='GBK')
                    lat_lon_data_obs = lat_lon_data.data - lat_lon_data_24.data
                    lat_lon_data_obs[mask_array_cldas == 0] = np.nan
                    grd = creat_m4(lat_lon_data.start_lon, lat_lon_data.end_lon, lat_lon_data.start_lat,
                                   lat_lon_data.end_lat, 0.05, lat_lon_data_obs)
                    cal_df(grd, file_time_end, Infile_list_df, map_extent, region_name)

        elif '降水' in Infile_list[2]:
            file_time_end = datetime.strptime(file_time, '%y%m%d%H')
            file_dir, file_name = os.path.split(Infile_list[0])
            if file_name[-6:-4] == '08' or file_name[-6:-4] == '20':
                if os.path.exists(Infile_list[0]):
                    lat_lon_data = M4.open_m4(Infile_list[0], encoding='GBK')
                    lat_lon_data.data[mask_array_cldas == 0] = np.nan
                    grd = creat_m4(lat_lon_data.start_lon, lat_lon_data.end_lon, lat_lon_data.start_lat,
                                   lat_lon_data.end_lat, 0.05,
                                   lat_lon_data.data)
                    cal_df(grd, file_time_end, Infile_list_df, map_extent, region_name)
        elif '高温' in Infile_list[2]:
            file_time_DATE = datetime.strptime(file_time, '%Y%m%d%H')
            if os.path.exists(Infile_list[0]):
                lat_lon_data = M4.open_m4(Infile_list[0], encoding='GBK')
                lat_lon_data.data[mask_array_cldas == 0] = np.nan
                lat_lon_data.data[lat_lon_data.data < 35] = np.nan
                grd = creat_m4(lat_lon_data.start_lon, lat_lon_data.end_lon, lat_lon_data.start_lat, lat_lon_data.end_lat, 0.05,
                               lat_lon_data.data)
                cal_df(grd, file_time_DATE, Infile_list_df, map_extent, region_name, num=35)
        else:
            file_time_DATE = datetime.strptime(file_time, '%Y%m%d%H')
            if os.path.exists(Infile_list[0]):
                lat_lon_data = M4.open_m4(Infile_list[0], encoding='GBK')
                lat_lon_data.data[mask_array_cldas == 0] = np.nan
                grd = creat_m4(lat_lon_data.start_lon, lat_lon_data.end_lon, lat_lon_data.start_lat, lat_lon_data.end_lat, 0.05,
                               lat_lon_data.data)
                cal_df(grd, file_time_DATE, Infile_list_df, map_extent, region_name)

def met_model_single_plot_tp_CLDAS(Infile_list, step, region, Infile_list_df):
    try:
        if not os.path.exists(Infile_list[1]):
            os.makedirs(Infile_list[1])
        if os.path.exists(Infile_list[0]):
            region_name, map_extent = region, tuple(REGION[REGION_NAME.index(region)])
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
                file_time_end = datetime.strptime(str(os.path.splitext(os.path.basename(Infile_list[0]))[0]), '%y%m%d%H')
                lat_lon_data[mask_array_cldas == 0] = np.nan
                grd = creat_m4(lat_lon.start_lon, lat_lon.end_lon, lat_lon.start_lat, lat_lon.end_lat, 0.05, lat_lon_data)
                cal_df_tp(grd, file_time_end, Infile_list_df, map_extent, region_name)
    except:
        print('数据缺失')

# 温度、变温、相对湿度和降水——CLDAS实况数据
def single_plot_CLDAS(argv):

    model_name = 'CLDAS'
    model_DF = argv[0]
    report_time = datetime.strptime(argv[1], '%Y%m%d%H')
    cst = report_time.hour
    cst_DF = int(argv[2])
    var = argv[3]
    region = argv[4]

    CLDAS_t2m = [MODEL_ROOT_CLDAS.format(model=model_name, report_time=report_time, cst=cst, element='TMP', lev=''),
                 os.path.dirname(MODEL_SAVE_OUT_CLDAS).format(model=model_name, report_time=report_time,
                                                              out_name='tem', lev=''),
                 t2m_title.format(model_name), t2m_var, t2m_units, t2m_colorbar, cmap_tem
                 ]
    file_t2m_df = [MODEL_ROOT, os.path.dirname(MODEL_SAVE_OUT), tem_df_title, tem_var_df, t2m_units,
                   tem_colorbar_df, cmap_tem_df, 't2m', 'tem_df', model_DF, cst_DF]


    CLDAS_t2m_High = [MODEL_ROOT_CLDAS.format(model=model_name, report_time=report_time, cst=cst, element='TMP', lev=''),
                 os.path.dirname(MODEL_SAVE_OUT_CLDAS).format(model=model_name, report_time=report_time,
                                                              out_name='tem_max', lev=''),
                t2m_high_title.format(model_name), t2m_high_var, t2m_high_units, t2m_high_colorbar, cmap_tem_high
                ]
    file_t2m_High_df = [MODEL_ROOT, os.path.dirname(MODEL_SAVE_OUT), tem_max_df_title, tem_max_var_df, t2m_units,
                   tem_max_colorbar_df, cmap_tem_max_df, 't2m', 'tem_max_df', model_DF, cst_DF]

    CLDAS_temC = [
        MODEL_ROOT_CLDAS.format(model=model_name, report_time=report_time, cst=cst, element='TMP', lev=''),
        os.path.dirname(MODEL_SAVE_OUT_CLDAS).format(model=model_name, report_time=report_time,
                                                     out_name='tem_change', lev=''),
        tem_change_title.format(model_name), tem_change_var, tem_change_units, tem_change_colorbar, cmap_tem_change
        ]
    file_temC_df = [MODEL_ROOT, os.path.dirname(MODEL_SAVE_OUT), temC_df_title, temC_var_df, t2m_units,
                       temC_colorbar_df, cmap_temC_df, 't2m', 'tem_change_df', model_DF, cst_DF]


    CLDAS_temC_48 = [
        MODEL_ROOT_CLDAS.format(model=model_name, report_time=report_time, cst=cst, element='TMP', lev=''),
        os.path.dirname(MODEL_SAVE_OUT_CLDAS).format(model=model_name, report_time=report_time,
                                                     out_name='tem_change_48', lev=''),
        tem_change_title.format(model_name), tem_change_var, tem_change_units, tem_change_colorbar, cmap_tem_change
        ]
    file_temC_48_df = [MODEL_ROOT, os.path.dirname(MODEL_SAVE_OUT), temC_df_title, temC_var_df, t2m_units,
                       temC_colorbar_df, cmap_temC_df, 't2m', 'tem_change_48_df', model_DF, cst_DF]

    CLDAS_r2m = [MODEL_ROOT_CLDAS.format(model=model_name, report_time=report_time, cst=cst, element='RH', lev=''),
                 os.path.dirname(MODEL_SAVE_OUT_CLDAS).format(model=model_name, report_time=report_time,
                                                              out_name='r', lev=''),
                 rh_title.format(model_name), rh_var, rh_units, rh_colorbar, cmap_r
                 ]
    file_r2m_df = [MODEL_ROOT, os.path.dirname(MODEL_SAVE_OUT), rh_df_title, rh_var_df, rh_units,
                   rh_colorbar_df, cmap_rh_df, 'r2m', 'r_df', model_DF, cst_DF]

    CLDAS_tp = [
        MODEL_ROOT_CLDAS_TP.format(model=model_name, report_time=report_time, cst=cst, element='tp', lev=''),
        os.path.dirname(MODEL_SAVE_OUT_CLDAS).format(model=model_name, report_time=report_time,
                                                     out_name='pre24_hgt', lev=''),
        tp_title.format(model_name), tp_var, tp_units, tp_colorbar, cmap_tp
        ]
    file_tp_df = [MODEL_ROOT, os.path.dirname(MODEL_SAVE_OUT), tp_df_title,
                   tp_var_df, tp_units, tp_colorbar_df, cmap_tp_hour_df, 'tp', 'pre24_hgt_df', model_DF, cst_DF]

    CLDAS_tp_3 = [
        MODEL_ROOT_CLDAS_TP_1h.format(model=model_name, report_time=report_time, cst=cst, element='tp', lev=''),
        os.path.dirname(MODEL_SAVE_OUT_CLDAS).format(model=model_name, report_time=report_time, out_name='pre03',
                                                     lev=''),
        tp_title.format(model_name), tp_var, tp_units, tp_colorbar2, cmap_tp_hour
        ]
    file_tp_3_df = [MODEL_ROOT, os.path.dirname(MODEL_SAVE_OUT), tp_hour_df_title,
                   tp_var_df, tp_units, tp_colorbar_df, cmap_tp_hour_df, 'pre03_df', model_DF, cst_DF]

    CLDAS_tp_6 = [
        MODEL_ROOT_CLDAS_TP_1h.format(model=model_name, report_time=report_time, cst=cst, element='tp', lev=''),
        os.path.dirname(MODEL_SAVE_OUT_CLDAS).format(model=model_name, report_time=report_time, out_name='pre06',
                                                     lev=''),
        tp_title.format(model_name), tp_var, tp_units, tp_colorbar2, cmap_tp_hour
        ]
    file_tp_6_df = [MODEL_ROOT, os.path.dirname(MODEL_SAVE_OUT), tp_hour_df_title,
                   tp_var_df, tp_units, tp_colorbar_df, cmap_tp_hour_df, 'pre06_df', model_DF, cst_DF]

    CLDAS_tp_12 = [
        MODEL_ROOT_CLDAS_TP_1h.format(model=model_name, report_time=report_time, cst=cst, element='tp', lev=''),
        os.path.dirname(MODEL_SAVE_OUT_CLDAS).format(model=model_name, report_time=report_time, out_name='pre12',
                                                     lev=''),
        tp_title.format(model_name), tp_var, tp_units, tp_colorbar2, cmap_tp_hour
        ]
    file_tp_12_df = [MODEL_ROOT, os.path.dirname(MODEL_SAVE_OUT), tp_hour_df_title,
                   tp_var_df, tp_units, tp_colorbar_df, cmap_tp_hour_df, 'pre12_df', model_DF, cst_DF]

    Dict = {'tem': [CLDAS_t2m, 3, file_t2m_df], 'tem_max': [CLDAS_t2m_High, 3, file_t2m_High_df],
            'tem_change': [CLDAS_temC, 24, file_temC_df], 'tem_change_48': [CLDAS_temC_48, 48, file_temC_48_df],
            'r': [CLDAS_r2m, 3, file_r2m_df], 'pre24_hgt': [CLDAS_tp, 24, file_tp_df]}
    Dict_tp = {'pre03': [CLDAS_tp_3, 3, file_tp_3_df], 'pre06': [CLDAS_tp_6, 6, file_tp_6_df], 'pre12': [CLDAS_tp_12, 12, file_tp_12_df]}
    if var in Dict.keys():
        met_model_single_plot_CLDAS(Dict.get(var)[0], region, Dict.get(var)[1], Dict.get(var)[2])
    elif var in Dict_tp.keys():
        met_model_single_plot_tp_CLDAS(Dict_tp.get(var)[0], Dict_tp.get(var)[1], region, Dict_tp.get(var)[2])