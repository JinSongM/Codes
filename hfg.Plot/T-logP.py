import os, sys
import metdig
import pandas as pd

import meteva.base as meb
from verify.config import *
import metpy.calc as mpcalc
from metdig.cal import other
from metpy.units import units
import matplotlib.pyplot as plt
from matplotlib import font_manager
from datetime import datetime, timedelta
from metpy.plots import Hodograph, SkewT
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
font_manager.fontManager.addfont(os.path.join(os.path.dirname(__file__), 'verify', 'SIMHEI.TTF'))

col_names = ['pressure', 'height', 'temperature', 'dewpoint', 'direction', 'speed']
height_col = [1000, 975, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200, 100]

def createdir(arg_dir):
    if os.path.exists(arg_dir):
        print('file path exists: ' + arg_dir)
    else:
        os.makedirs(arg_dir)
        print('Create file path: ' + arg_dir)

def get_df_data(arg_list):
    # 模式、起报时间、预报时效、经纬度
    model = arg_list[1]
    date_start = datetime.strptime(arg_list[2], "%Y%m%d%H")
    cst = arg_list[3]
    find_lonindex = float(arg_list[4])
    find_latindex = float(arg_list[5])
    dict_merge = pd.DataFrame()
    for i in height_col:
        h_path = MODEL_ROOT.format(model=model, element='gh', lev=i, report_time=date_start, cst=int(cst))
        t_path = MODEL_ROOT.format(model=model, element='t', lev=i, report_time=date_start, cst=int(cst))
        d_path = MODEL_ROOT.format(model=model, element='dpt', lev=i, report_time=date_start, cst=int(cst))
        u_path = MODEL_ROOT.format(model=model, element='u', lev=i, report_time=date_start, cst=int(cst))
        v_path = MODEL_ROOT.format(model=model, element='v', lev=i, report_time=date_start, cst=int(cst))
        if os.path.exists(h_path) and os.path.exists(t_path) and os.path.exists(d_path) \
                and os.path.exists(u_path) and os.path.exists(v_path):
            h_data = meb.read_griddata_from_micaps4(h_path)
            t_data = meb.read_griddata_from_micaps4(t_path)
            d_data = meb.read_griddata_from_micaps4(d_path)
            u_data = meb.read_griddata_from_micaps4(u_path)
            v_data = meb.read_griddata_from_micaps4(v_path)
            u = metdig.utl.xrda_to_gridstda(u_data, level_dim='level', time_dim='time', lat_dim='lat',
                                                 lon_dim='lon', dtime_dim='dtime', var_name='u', np_input_units='m/s')
            v = metdig.utl.xrda_to_gridstda(v_data, level_dim='level', time_dim='time', lat_dim='lat',
                                                 lon_dim='lon', dtime_dim='dtime', var_name='v', np_input_units='m/s')
            wind_speed = other.wind_speed(u, v)

            lon, lat = h_data.lon.data.tolist(), h_data.lat.data.tolist()  # 读取经度，并且一定要转化为列表格式，因为后面所使用的函数不支持numpy或者其他格式
            # 查询距离指定纬度最近的格点
            lat_index = lat.index(min(lat, key=lambda x: abs(x - find_latindex)))
            lon_index = lon.index(min(lon, key=lambda x: abs(x - find_lonindex)))
            # 读取数据
            reshape_l, reshape_v = h_data.data.shape[-2], h_data.data.shape[-1]
            h_value = h_data.data.reshape(reshape_l, reshape_v)[lat_index, lon_index]
            t_value = t_data.data.reshape(reshape_l, reshape_v)[lat_index, lon_index]
            d_value = d_data.data.reshape(reshape_l, reshape_v)[lat_index, lon_index]
            u_value = u_data.data.reshape(reshape_l, reshape_v)[lat_index, lon_index]
            wind_speed_value = wind_speed.data.reshape(reshape_l, reshape_v)[lat_index, lon_index]
            dict_data = pd.DataFrame([i, h_value, t_value, d_value, u_value, wind_speed_value]).T
            dict_merge = pd.concat([dict_merge, dict_data], axis=0)
    dict_merge.columns = col_names
    return  dict_merge

def plot_T_logP(arg_list, df):
    # from metpy.cbook import get_test_data
    # df = pd.read_fwf(get_test_data('nov11_sounding.txt', as_file_obj=False),
    #                  skiprows=5, usecols=[0, 1, 2, 3, 6, 7], names=col_names)
    model = arg_list[1]
    date_start = datetime.strptime(arg_list[2], "%Y%m%d%H")
    cst = arg_list[3]
    date_end = date_start + timedelta(hours=int(cst))

    obs_time_info = '{model}: {Time:%Y}年{Time:%m}月{Time:%d}日{Time:%H}时'.format(model=model, Time=date_start)
    fst_time_info = 'CST: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(date_end)
    title = 'T-logP'

    # Drop any rows with all NaN values for T, Td, winds
    df_tmp = df.dropna(subset=('temperature', 'dewpoint', 'direction', 'speed'
                           ), how='all').reset_index(drop=True)

    df = df_tmp.sort_values(by=['pressure'], ascending=False)
    # We will pull the data out of the example dataset into individual variables and
    # assign units
    p = df['pressure'].values * units.hPa
    T = df['temperature'].values * units.degC
    Td = df['dewpoint'].values * units.degC

    wind_speed = df['speed'].values * units.knots
    wind_dir = df['direction'].values * units.degrees
    u, v = mpcalc.wind_components(wind_speed, wind_dir)
    # Calculate the LCL
    lcl_pressure, lcl_temperature = mpcalc.lcl(p[0], T[0], Td[0])
    # Calculate the parcel profile.
    parcel_prof = mpcalc.parcel_profile(p, T[0], Td[0]).to('degC')

    # Create a new figure. The dimensions here give a good aspect ratio
    fig = plt.figure(figsize=(9, 9))
    skew = SkewT(fig, rotation=30)

    # Plot the data using normal plotting functions, in this case using
    # log scaling in Y, as dictated by the typical meteorological plot
    skew.plot(p, T, 'r')
    skew.plot(p, Td, 'g')
    skew.plot_barbs(p, u, v, sizes=dict(emptybarb=0))
    skew.ax.set_ylim(1000, 100)
    skew.ax.set_xlim(-60, 60)
    skew.ax.set_title(title, family='serif', fontsize=25, pad=30)
    plt.text(x=-108, y=95, fontsize=15, s=obs_time_info)
    plt.text(x=-29, y=95, fontsize=15, s=fst_time_info)
    plt.rc('font', family='serif')
    plt.xticks(fontsize=15, fontproperties='serif')
    plt.yticks(fontsize=15, fontproperties='serif')
    plt.xlabel('degree_Celsius', font={'family':'serif', 'size':20})
    plt.ylabel('hectopascal', font={'family':'serif', 'size':20})

    # Plot LCL as black dot
    skew.plot(lcl_pressure, lcl_temperature, 'ko', markerfacecolor='black')

    # Plot the parcel profile as a black line
    skew.plot(p, parcel_prof, 'k', linewidth=2)

    # Shade areas of CAPE and CIN
    skew.shade_cin(p, T, parcel_prof, Td)
    skew.shade_cape(p, T, parcel_prof)

    # Plot a zero degree isotherm
    skew.ax.axvline(0, color='c', linestyle='--', linewidth=2)

    # Add the relevant special lines
    skew.plot_dry_adiabats()
    skew.plot_moist_adiabats()
    skew.plot_mixing_lines()

    # Create a hodograph
    # Create an inset axes object that is 40% width and height of the
    # figure and put it in the upper right hand corner.
    ax_hod = inset_axes(skew.ax, '30%', '45%', loc=1)
    h = Hodograph(ax_hod, component_range=80.)
    h.add_grid(increment=20)
    h.plot_colormapped(u, v, wind_speed)  # Plot a line colored by wind speed
    # save the plot
    outpath = MODEL_SAVE_OUT.format(model=model, report_time=date_start,
                                    out_name='tlp', lev='', cst=int(cst), region=arg_list[4] +'_'+ arg_list[5])
    createdir(os.path.dirname(outpath))
    plt.savefig(outpath, bbox_inches='tight')


if __name__ == '__main__':
    if len(sys.argv) == 6:
        arg_list = sys.argv
        dataFrame = get_df_data(arg_list)
        plot_T_logP(arg_list, dataFrame)
    else:
        print('参数输入错误')