# -- coding: utf-8 --
# @Time : 2023/8/25 10:31
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : single_AI.py
# @Software: PyCharm
import os
import sys
from operator import itemgetter
import pandas as pd
import meteva.base as meb
import math
from single_AI_config import *
from matplotlib.ticker import MultipleLocator
from metdig.graphics.draw_compose import *
from datetime import datetime,timedelta
from single_AI_month import horizontal_pallete_test
from metdig.graphics import draw_compose, contourf_method
import metdig.graphics.cmap.cm as cm_collected
import metdig.graphics.lib.utility as utl
from matplotlib import font_manager
font_manager.fontManager.addfont(os.path.join(os.path.dirname(__file__), 'SIMHEI.TTF'))
def scatter_2d(ax, stda, xdim='lon', ydim='lat',
               add_colorbar=True, cb_pos='bottom', cb_ticks=None, cb_label=None,
               levels=np.arange(-40, 40), cmap='ncl/BlueYellowRed', extend='both', isLinear=False,
               transform=ccrs.PlateCarree(), alpha=1,
               colorbar_kwargs={}, s=10, **kwargs):
    """[graphics层绘制scatter平面图通用方法]

    Args:
        ax ([type]): [description]
        stda ([type]): [u矢量 stda标准格式]
        xdim (type, optional): [stda维度名 member, level, time dtime, lat, lon或fcst_time]. Defaults to 'lon'.
        ydim (type, optional): [stda维度名 member, level, time dtime, lat, lon或fcst_time]. Defaults to 'lat'.
        add_colorbar (bool, optional): [是否绘制colorbar]. Defaults to True.
        cb_pos (str, optional): [colorbar的位置]. Defaults to 'bottom'.
        cb_ticks ([type], optional): [colorbar的刻度]. Defaults to None.
        cb_label ([type], optional): [colorbar的label，如果不传则自动进行var_cn_name和var_units拼接]. Defaults to None.
        levels ([list], optional): [description]. Defaults to None.
        cmap (str, optional): [description]. Defaults to 'jet'.
        extend (str, optional): [description]. Defaults to 'both'.
        isLinear ([bool], optional): [是否对colors线性化]. Defaults to False.
        transform ([type], optional): [stda的投影类型，仅在xdim='lon' ydim='lat'时候生效]. Defaults to ccrs.PlateCarree().
        alpha (float, optional): [description]. Defaults to 1.
        s=1 (float, optional): [散点大小]. Defaults to 1.
    Returns:
        [type]: [绘图对象]
    """
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)

    cmap, norm = cm_collected.get_cmap(cmap, extend=extend, levels=levels, isLinear=isLinear)
    if transform is None or (xdim != 'lon' and ydim != 'lat'):
        img = ax.scatter(x, y, marker='.', s=s, norm=norm, cmap=cmap, c=z, alpha=alpha, **kwargs)

    else:
        img = ax.scatter(x, y, marker='.', s=s, norm=norm, cmap=cmap, c=z, transform=transform, alpha=alpha, **kwargs)

    if add_colorbar:
        cb_label = '{}({})'.format(stda.attrs['var_cn_name'], stda.attrs['var_units']) if not cb_label else cb_label
        utl.add_colorbar(ax, img, ticks=cb_ticks, pos=cb_pos, extend=extend, label=cb_label, kwargs=colorbar_kwargs)

    return img

def metdig_plot_s(infile, outfile, ini_config, sta, Bool='F'):
    try:
        map_extent = [70, 140, 0, 60]
        file_time = os.path.split(infile)[1].split('.')[0]
        Fst_time = int(os.path.split(infile)[1].split('.')[1])
        obs_time_dc = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(datetime.strptime(file_time, '%Y%m%d%H'))
        fst_time_dc = '预报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(datetime.strptime(file_time, '%Y%m%d%H') + timedelta(hours=Fst_time))
        forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时'.format(Fst_time)
        png_name = file_time + '.' + os.path.split(infile)[1].split('.')[1] + '.PNG'

        if os.path.exists(outfile):
            if Bool == 'T':
                os.remove(outfile)
            elif Bool == 'F':
                print('文件存在，不覆盖')
                return
        drw = draw_compose.horizontal_compose(title=ini_config[0], description=forcast_info, output_dir=os.path.dirname(outfile),
                                              add_tag=False, add_city=False,
                                              map_extent=map_extent, png_name=png_name, is_return_figax=True, add_ticks=True)
        drw.ax.tick_params(labelsize=20)
        drw.ax.xaxis.set_major_locator(MultipleLocator(ticks_S))
        drw.ax.yaxis.set_major_locator(MultipleLocator(ticks_S))
        staGrd = sta.copy()
        extend = 'both'
        if ini_config[0].__contains__('MAE'):
            staGrd.data0 = np.abs(staGrd.data0)
            extend = 'max'
        elif ini_config[0].__contains__('RMSE'):
            staGrd.data0 = np.sqrt(np.square(staGrd.data0))
            extend = 'max'
        elif ini_config[0].__contains__('PC(%)'):
            sta_array = np.abs(staGrd.data0)
            if ini_config[0].__contains__('风速') or ini_config[0].__contains__('风向'):
                staGrd.data0 = np.where(sta_array == 1., 100,  np.nan)
            else:
                staGrd.data0 = np.where(sta_array<=2, 100,  np.nan)
            extend = 'neither'
        scatter_2d(drw.ax, staGrd, xdim='lon', ydim='lat',s=5,
                   add_colorbar=True, cb_pos='bottom', cb_ticks=None, cb_label=ini_config[2],
                   levels=ini_config[1], cmap=ini_config[3], extend=extend)

        drw.save()
        print('绘图成功：' + outfile)
    except Exception as e:
        print(e)
        print('绘图失败：' + infile)

def metdig_plot_c(infile, outfile, ini_config, sta, Bool='F'):
    try:
        lat_lon_data = meb.read_griddata_from_micaps4(infile)
        map_extent = (int(min(list(lat_lon_data.lon.data))), math.ceil(max(list(lat_lon_data.lon.data))),
                      int(min(list(lat_lon_data.lat.data))), math.ceil(max(list(lat_lon_data.lat.data))))

        if outfile.__contains__('wind'):
            file_time = os.path.split(infile)[1].split('.')[0].split('_')[-1]
        else:
            file_time = os.path.split(infile)[1].split('.')[0]
        Fst_time = int(os.path.split(infile)[1].split('.')[1])
        png_name = os.path.basename(outfile)
        obs_time_dc = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(datetime.strptime(file_time, '%Y%m%d%H'))
        fst_time_dc = '预报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(datetime.strptime(file_time, '%Y%m%d%H') + timedelta(hours=Fst_time))
        forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时'.format(Fst_time)

        if os.path.exists(outfile):
            if Bool == 'T':
                os.remove(outfile)
            elif Bool == 'F':
                print('文件存在，不覆盖')
                return
        fig, ax = horizontal_pallete_test()
        drw = draw_compose.horizontal_compose(title=ini_config[0], description=forcast_info, output_dir=os.path.dirname(outfile),
                                              add_tag=False, add_city=False, fig=fig, ax=ax,
                                              map_extent=map_extent, png_name=png_name, is_return_figax=True, add_ticks=True)
        drw.ax.tick_params(labelsize=20)
        drw.ax.xaxis.set_major_locator(MultipleLocator(ticks_S))
        drw.ax.yaxis.set_major_locator(MultipleLocator(ticks_S))
        arrayGrd = lat_lon_data.copy()
        extend = 'both'
        if ini_config[0].__contains__('MAE'):
            arrayGrd.data = [[[[np.abs(np.squeeze(lat_lon_data.data))]]]]
            extend = 'max'
        elif ini_config[0].__contains__('RMSE'):
            arrayGrd.data = [[[[np.sqrt(np.square(np.squeeze(lat_lon_data.data)))]]]]
            extend = 'max'
        elif ini_config[0].__contains__('PC(%)'):
            array = np.abs(np.squeeze(lat_lon_data.data))
            if ini_config[0].__contains__('风速') or ini_config[0].__contains__('风向'):
                arrayGrd.data = [[[[np.where(array == 1.0, 100, 0)]]]]
            else:
                arrayGrd.data = [[[[np.where(array<=2, 100,  0)]]]]
            extend = 'neither'

        contourf_method.contourf_2d(drw.ax, arrayGrd, levels=ini_config[1], cb_label=ini_config[2], cmap=ini_config[3], extend=extend)
        drw.save()
        print('绘图成功：' + outfile)
    except Exception as e:
        print(e)
        print('绘图失败：' + infile)

def creat_M3_grd(data):

    # 构建站点数据标准格式
    M3_grd = pd.DataFrame(data)
    sta = meb.sta_data(M3_grd, columns=["id", "lon", "lat", 'data0'])
    meb.set_stadata_coords(sta, level=0, time=datetime(2023, 1, 1, 8, 0), dtime=0)
    return sta

def gain_sta(stafile, model_file):
    with open(stafile, 'r', encoding='utf-8') as f1:
        content1 = f1.readlines()
    with open(model_file, 'r', encoding='utf-8') as f2:
        content2 = f2.readlines()
    new_content1 = []
    for word in content1:
        tmp = word.strip()
        tmp = tmp.split()[:5]
        new_content1.append(tmp)
    new_content2 = []

    if model_file.__contains__('wind'):
        for word in content2[2:]:
            tmp = word.strip()
            tmp = tmp.split()
            new_content2.append(itemgetter(*[0, 3, 4, 5, 7])(tmp))
        DF2_merge = pd.DataFrame(new_content2, columns=['id', 'acd', 'acs', 'fst', 'obs'])
        DF2_merge = DF2_merge[(DF2_merge['fst'].astype(np.float)<9999.0) & (DF2_merge['obs'].astype(np.float)<9999.0)
                  & (DF2_merge['acd'].astype(np.float)<9999.0) & (DF2_merge['acs'].astype(np.float)<9999.0)]
        DF2 = DF2_merge[['id', 'fst', 'obs']]
        if label == 'ACD':
            data_change = DF2_merge['acd'].astype(np.float)
        elif label == 'ACS':
            data_change = DF2_merge['acs'].astype(np.float)
        else:
            data_change = DF2_merge['fst'].astype(np.float) - DF2_merge['obs'].astype(np.float)
        DF2.insert(loc=1, column='data_change', value=data_change)
    else:
        for word in content2:
            tmp = word.strip()
            tmp = tmp.split()
            new_content2.append(tmp)
        DF2 = pd.DataFrame(new_content2, columns=['id', 'data_change', 'obs', 'fst'])

    DF1 = pd.DataFrame(new_content1, columns=['id', 'lon', 'lat', 'id1', 'local'])
    df_merge = pd.merge(DF1, DF2, on='id')
    df_merge_filter = df_merge[['id', 'lon', 'lat', 'data_change']]
    df_merge_filter = df_merge_filter[df_merge_filter['data_change'].astype(np.float)<9999.0]
    df_merge_filter['data_change'] = df_merge_filter['data_change'].astype(float)
    df_merge_filter['lon'] = df_merge_filter['lon'].astype(float)
    df_merge_filter['lat'] = df_merge_filter['lat'].astype(float)
    sta = creat_M3_grd(df_merge_filter)
    return sta

def main_draw():
    if var == 'wind':
        if lev.__contains__('station'):
            lev_filename = lev[:8] + model.lower()
            infile = infile_format.format(var=var, model=model, lev=lev_filename, RT=RT, cst=cst)
        else:
            lev_filename = lev
            if label == 'ACS':
                lab = 'sc_s'
            elif label == 'ACD':
                lab = 'sc_d'
            else:
                lab = 'ws_me'
            infile = windfile_format.format(lab=lab, var=var, model=model, lev=lev_filename, RT=RT, cst=cst)
    else:
        if lev.__contains__('station'):
            lev_filename = lev[:8] + model.lower()
        else:
            lev_filename = lev
        infile = infile_format.format(var=var, model=model, lev=lev_filename, RT=RT, cst=cst)
    outfile = outfile_format.format(var=var, model=model, lev=lev, label=label, inter=inter, RT=RT, cst=cst)

    if not os.path.exists(infile):
        return

    if lev.__contains__('station'):
        lev_name = lev.split('_')[1] + '站'
        function_draw = metdig_plot_s
        stafile = os.path.join(os.path.dirname(__file__), lev + '.dat')
        sta = gain_sta(stafile, infile)
    else:
        level = lev.split('_')[1]
        if int(level) < 200:
            lev_name = '地面' + level + '米'
        else:
            lev_name = lev.split('_')[1] + 'hPa'
        function_draw = metdig_plot_c
        sta = None

    if model == 'PANGU':
        model_name = '盘古'
    elif model == 'FENGWU':
        model_name = '风乌'
    elif model == 'FUXI':
        model_name = '伏羲'
    elif model == 'EC':
        model_name = 'ECMWF'
    elif model == 'CMA':
        model_name = 'CMA-GFS'
    else:
        return


    print('输入数据：' + infile)
    var_dict = {
        'tmp': {
            'ME': [t2m_title.format(model_name, lev_name, label), level_tmp, t2m_var.format(label), cmap],
            'MAE': [t2m_title.format(model_name, lev_name, label), level_tmp_sg, t2m_var.format(label), cmap],
            'RMSE': [t2m_title.format(model_name, lev_name, label), level_tmp_sg, t2m_var.format(label), cmap],
            'PC': [t2m_title_pc.format(model_name, lev_name), level_pc, t2m_var_pc, cmap_pc],
                },
        'sh': {
            'ME': [sh_title.format(model_name, lev_name, label), level_sh, sh_var.format(label), cmap],
            'MAE': [sh_title.format(model_name, lev_name, label), level_sh_sg, sh_var.format(label), cmap],
            'RMSE': [sh_title.format(model_name, lev_name, label), level_sh_sg, sh_var.format(label), cmap],
                },
        'gh': {
            'ME': [gh_title.format(model_name, lev_name, label), level_gh, gh_var.format(label), cmap],
            'MAE': [gh_title.format(model_name, lev_name, label), level_gh_sg, gh_var.format(label), cmap],
            'RMSE': [gh_title.format(model_name, lev_name, label), level_gh_sg, gh_var.format(label), cmap],
                },
        'wind': {
            'ME': [wind_title.format(model_name, lev_name, label), level_wind, wind_var.format(label), cmap],
            'MAE': [wind_title.format(model_name, lev_name, label), level_wind_sg, wind_var.format(label), cmap],
            'RMSE': [wind_title.format(model_name, lev_name, label), level_wind_sg, wind_var.format(label), cmap],
            'ACS': [wind_title_pc.format(model_name, lev_name), level_pc, wind_var_pc, cmap_pc],
            'ACD': [wind_title_pcd.format(model_name, lev_name), level_pc, wind_var_pcd, cmap_pc],
                }
    }
    function_draw(infile, outfile, var_dict.get(var).get(label), sta, reBool)

if __name__ == '__main__':
    var = sys.argv[1]
    model = sys.argv[2]
    lev = sys.argv[3]
    label = sys.argv[4]
    inter = sys.argv[5]
    RT = datetime.strptime(sys.argv[6], "%Y%m%d%H")
    cst = int(sys.argv[7])
    if len(sys.argv) > 8:
        reBool = sys.argv[8]
    else:
        reBool = 'F'
    main_draw()
    #gh FUXI gh_200 ME day 2023080120 12 T
    #tmp FENGWU t_200 ME day 2023080108 12 T
    #sh PANGU sh_500 ME day 2023081808 12 T
    #wind FUXI wind_200 ME day 2023081008 12 T
    #tmp FENGWU station_10290 ME day 2023080108 12 T
    #wind FENGWU station_2401 ME day 2023080108 12 T