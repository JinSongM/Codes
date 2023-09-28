# -- coding: utf-8 --
# @Time : 2023/9/6 9:52
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : single_AI_month_merge.py
# @Software: PyCharm
import os
import sys
from operator import itemgetter
import pandas as pd
import meteva.base as meb
import math
import matplotlib as mpl
from single_AI_config import *
import cartopy.feature as cfeature
from cartopy.io.img_tiles import Stamen
from matplotlib.ticker import MultipleLocator
from metdig.graphics.draw_compose import *
from dateutil import relativedelta
from datetime import datetime,timedelta
import metdig.graphics.lib.utl_plotmap as utl_plotmap
from meteva.base.tool.plot_tools import add_china_map_2basemap
from metdig.graphics import draw_compose, contourf_method, scatter_method
import metdig.graphics.cmap.cm as cm_collected
import metdig.graphics.lib.utility as utl
from matplotlib import font_manager
font_manager.fontManager.addfont(os.path.join(os.path.dirname(__file__), 'SIMHEI.TTF'))
mpl.use('Agg')

def horizontal_pallete_test(ax=None, figsize=(16, 9), crs=ccrs.PlateCarree(), map_extent=(60, 145, 15, 55), step=10,
                            title='', title_fontsize=18, forcast_info='', nmc_logo=False,
                            add_coastline=True, add_china=True, add_province=True, add_river=False, add_city=False,
                            add_county=False, add_county_city=False,
                            add_background_style=None, add_south_china_sea=False, add_grid=False, add_ticks=True,
                            background_zoom_level=5, add_tag=False, **kwargs):
    """[水平分布图画板设置]]

    Args:
        ax ():[绘图对象].用于用户传入自己的ax绘图拓展
        figsize (tuple, optional): [画板大小]. Defaults to (16, 9).
        crs ([type], optional): [画板投影类型投影]. Defaults to ccrs.PlateCarree().
        map_extent (tuple, optional): [绘图区域]. Defaults to (60, 145, 15, 55).
        title (str, optional): [标题]. Defaults to ''.
        title_fontsize (int, optional): [标题字体大小]. Defaults to 23.
        forcast_info (str, optional): [预报或其它描述信息]. Defaults to ''.
        nmc_logo (bool, optional): [是否增加logo]. Defaults to False.
        add_china (bool, optional): [是否增加中国边界线]. Defaults to True.
        add_city (bool, optional): [是否增加城市名称]. Defaults to True.
        add_background_style (str, [None, False, 'RD', 'YB', 'satellite', 'terrain', 'road']): [是否增加背景底图，None/False(无填充),RD(陆地海洋),YB(陆地海洋),satellite/terrain/road(卫星图像)，]. Defaults to 'RD'.
        add_south_china_sea (bool, optional): [是否增加南海]. Defaults to True.
        add_grid (bool, optional): [是否绘制网格线]]. Defaults to True.
        add_ticks (bool, optional): [是否绘制刻度]. Defaults to False.
        background_zoom_level (int, optional): [背景地图是卫星地图时需要手动设置zoomlevel]. Defaults to 10.
        add_tag(bool, optional): [是否标注metdig信息]. Defaults to True.

    Returns:
        [type]: [description]
    """
    # plt_base_env()  # 初始化字体中文等
    if (ax is None):  #
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(projection=crs)
    else:
        fig = None
    # 标题
    ax.set_title(title, loc='left', fontsize=title_fontsize)
    # set_map_extent
    if ((map_extent[1] - map_extent[0] > 350) and (map_extent[3] - map_extent[2] > 170)):
        ax.set_global()
    else:
        # map_extent2 = utl_plotmap.adjust_map_ratio(ax, map_extent=map_extent, datacrs=ccrs.PlateCarree())
        ax.set_extent(map_extent, crs=ccrs.PlateCarree())

    # add grid lines
    if add_grid:
        gl = ax.gridlines(crs=ccrs.PlateCarree(), linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=100)
        gl.xlocator = mpl.ticker.FixedLocator(np.arange(0, 361, 10))
        gl.ylocator = mpl.ticker.FixedLocator(np.arange(-90, 90, 10))

    # 海岸线，省界，河流等中国边界信息
    if add_coastline:
        utl_plotmap.add_china_map_2cartopy_public(ax, name='coastline', edgecolor='dimgrey', lw=1, zorder=19, alpha=1,
                                                  crs=ccrs.PlateCarree())
    if add_china:
        utl_plotmap.add_china_map_2cartopy_public(ax, name='nation', edgecolor='black', lw=2.5, zorder=20,
                                                  crs=ccrs.PlateCarree())
    if add_province:
        utl_plotmap.add_china_map_2cartopy_public(ax, name='province', edgecolor='dimgray', lw=1, zorder=19,
                                                  crs=ccrs.PlateCarree())

    if add_river:
        utl_plotmap.add_china_map_2cartopy_public(ax, name='river', edgecolor='#B94FFF', lw=1, zorder=10, alpha=1,
                                                  crs=ccrs.PlateCarree())
    if add_county:
        add_china_map_2basemap(ax, name="county", edgecolor='#D9D9D9', lw=0.1, encoding='gbk', zorder=0)
        pass

    # 城市名称
    if add_city:
        utl_plotmap.add_city_on_map(ax, map_extent=map_extent, transform=ccrs.PlateCarree(),
                                    zorder=101, size=13)
    if add_county_city:
        utl_plotmap.add_city_on_map(ax, map_extent=map_extent, transform=ccrs.PlateCarree(),
                                    zorder=101, size=13, city_type='county')

    # 背景图
    if add_background_style is None:
        utl_plotmap.add_china_map_2cartopy_public(ax, name='world', edgecolor='gray', lw=1, zorder=19,
                                                  crs=ccrs.PlateCarree())
    elif add_background_style == 'RD':
        utl_plotmap.add_china_map_2cartopy_public(ax, name='world', edgecolor='gray', lw=1, zorder=19,
                                                  crs=ccrs.PlateCarree())
        utl_plotmap.add_cartopy_background(ax, name='RD')
    elif add_background_style == 'YB':
        ax.add_feature(cfeature.LAND, facecolor='#EBDBB2')
        ax.add_feature(cfeature.OCEAN, facecolor='#C8EBFA')
    elif add_background_style == 'satellite':
        request = utl.TDT_img()  # 卫星图像
        ax.add_image(request, background_zoom_level)  # level=10 缩放等级
    elif add_background_style == 'terrain':
        request = utl.TDT_Hillshade()  # 地形阴影
        ax.add_image(request, background_zoom_level)  # level=10 缩放等
        request = utl.TDT_ter()  # 地形
        ax.add_image(request, background_zoom_level, alpha=0.5)  # level=10 缩放等

    elif add_background_style == 'terrain2':
        tiler = Stamen('terrain-background')
        ax.add_image(tiler, background_zoom_level, interpolation='bilinear')

    elif add_background_style == 'road':
        request = utl.TDT()  # 卫星图像
        ax.add_image(request, background_zoom_level)  # level=10 缩放等级

    # 增加坐标
    if add_ticks:
        if (isinstance(add_ticks, bool)):
            utl_plotmap.add_ticks(ax, xticks=np.arange(map_extent[0], map_extent[1] + 1, step),
                                  yticks=np.arange(map_extent[2], map_extent[3] + 1, step))

        else:
            utl_plotmap.add_ticks(ax, xticks=np.arange(map_extent[0], map_extent[1] + 1, step),
                                  yticks=np.arange(map_extent[2], map_extent[3] + 1, step))

    # 南海
    if add_south_china_sea:
        l, b, w, h = ax.get_position().bounds
        utl_plotmap.add_south_china_sea_png(pos=[l + w - 0.1, b + 0.005, 0.11, 0.211], name='white')  # 直接贴图

    # 预报/分析描述信息
    if forcast_info:
        ax.text(0.01, 0.99, forcast_info, transform=ax.transAxes, size=12, va='top',
                ha='left', bbox=dict(facecolor='#FFFFFFCC', edgecolor='black', pad=3.0), zorder=20)

    return fig, ax



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

def metdig_plot_s(infile_list, outfile, ini_config, stafile, Bool='F'):
    # 绘制散点图
    try:
        infile, map_extent = infile_list[0], [70, 140, 0, 60]
        file_time = os.path.split(outfile)[1][:-4]
        Fst_time = int(file_time.split('.')[-1])
        obs_time_dc = '{0:%Y}年{0:%m}月{0:%H}时平均值'.format(datetime.strptime(file_time[:-4], '%Y%m.%H'))
        forcast_info = obs_time_dc + '\n' + '预报时效：{}小时'.format(Fst_time)
        png_name = os.path.basename(outfile)

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

        try:
            staGrd, extend = None, 'both'
            if ini_config[0].__contains__('MAE'):
                staGrd, extend = statistical_Inspect_sta(infile_list, stafile, 'MAE')
            if ini_config[0].__contains__('RMSE'):
                staGrd, extend = statistical_Inspect_sta(infile_list, stafile,  'RMSE')
            if ini_config[0].__contains__('PC'):
                staGrd, extend = statistical_Inspect_sta(infile_list, stafile,  'PC')
            if ini_config[0].__contains__('ME'):
                staGrd, extend = statistical_Inspect_sta(infile_list, stafile,  'ME')
            scatter_2d(drw.ax, staGrd, xdim='lon', ydim='lat',s=5,
                       add_colorbar=True, cb_pos='bottom', cb_ticks=None, cb_label=ini_config[2],
                       levels=ini_config[1], cmap=ini_config[3], extend=extend)
        except Exception as e:
            print(e)
        drw.save()
        print('绘图成功：' + outfile)
    except Exception as e:
        print(e)
        print('绘图失败')

def metdig_plot_c(infile_list, outfile, ini_config, stafile, Bool='F'):
    # 绘制填色图
    try:
        fst_file = infile_list[0]
        lat_lon_data = meb.read_griddata_from_micaps4(fst_file)
        map_extent = (int(min(list(lat_lon_data.lon.data))), math.ceil(max(list(lat_lon_data.lon.data))),
                      int(min(list(lat_lon_data.lat.data))), math.ceil(max(list(lat_lon_data.lat.data))))

        file_time = os.path.split(outfile)[1][:-4]
        Fst_time = int(file_time.split('.')[-1])
        png_name = os.path.basename(outfile)
        obs_time_dc = '{0:%Y}年{0:%m}月{0:%H}时平均值'.format(datetime.strptime(file_time[:-4], '%Y%m.%H'))
        forcast_info = obs_time_dc + '\n' + '预报时效：{}小时'.format(Fst_time)

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

        arrayGrd, extend = None, 'both'
        try:
            if ini_config[0].__contains__('MAE'):
                arrayGrd, extend = statistical_Inspect_grd(infile_list, 'MAE')
                extend = 'max'
            if ini_config[0].__contains__('RMSE'):
                arrayGrd, extend = statistical_Inspect_grd(infile_list, 'RMSE')
                extend = 'max'
            if ini_config[0].__contains__('PC'):
                arrayGrd, extend = statistical_Inspect_grd(infile_list, 'PC')
                extend = 'neither'
            if ini_config[0].__contains__('ME'):
                arrayGrd, extend = statistical_Inspect_grd(infile_list, 'ME')
        except Exception as e:
            print(e)

        contourf_method.contourf_2d(drw.ax, arrayGrd, levels=ini_config[1], cb_label=ini_config[2], cmap=ini_config[3], extend=extend)
        drw.save()
        print('绘图成功：' + outfile)
    except Exception as e:
        print(e)
        print('绘图失败')

def statistical_Inspect_sta(infile_list, stafile, index):
    # 统计月均站点数据检验指标
    sta_list, sta, extend = [], None, 'both'
    for file in infile_list:
        sta = gain_sta(stafile, file)
        sta_list.append(sta.data0)
    if index == 'ME':
        sta.data0 = np.nanmean(sta_list, axis=0)
        extend = 'both'
    if index == 'MAE':
        sta.data0 = np.nanmean(np.abs(sta_list), axis=0)
        extend = 'max'
    if index == 'RMSE':
        sta.data0 = np.sqrt(np.nanmean(np.square(sta_list), axis=0))
        extend = 'max'
    if index == 'PC':
        array_PC = np.nanmean(np.array([np.where(np.abs(i)<=2, 100,  0) for i in sta_list]), axis=0)
        array_PC[array_PC < 50.] = np.nan
        sta.data0 = array_PC
        extend = 'neither'
    return sta, extend

def statistical_Inspect_grd(infile_list, index):
    # 统计月均格点数据检验指标
    array_list, grd, extend = [], None, 'both'
    for file in infile_list:
        grd = meb.read_griddata_from_micaps4(file)
        array_list.append(np.squeeze(grd.data))

    if index == 'ME':
        array = np.nanmean(np.array(array_list), axis=0)
        grd.data = [[[[array]]]]
        extend = 'both'
    if index == 'MAE':
        array = np.nanmean(np.abs(np.array(array_list)), axis=0)
        grd.data = [[[[array]]]]
        extend = 'max'
    if index == 'RMSE':
        array = np.sqrt(np.nanmean(np.square(np.array(array_list)), axis=0))
        grd.data = [[[[array]]]]
        extend = 'max'
    if index == 'PC':
        array = np.nanmean(np.array([np.where(np.abs(i)<=2, 100,  0) for i in array_list]), axis=0)
        grd.data = [[[[array]]]]
        extend = 'neither'
    return grd, extend

def creat_M3_grd(data):
    # 构建站点数据标准格式
    M3_grd = pd.DataFrame(data)
    sta = meb.sta_data(M3_grd, columns=["id", "lon", "lat", 'data0'])
    meb.set_stadata_coords(sta, level=0, time=datetime(2023, 1, 1, 8, 0), dtime=0)
    return sta

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

def gain_sta(stafile, model_file):
    # 站点匹配，输出m3标准格式
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
            new_content2.append(itemgetter(*[0, 5, 7])(tmp))
        DF2 = pd.DataFrame(new_content2, columns=['id', 'fst', 'obs'])
        data_change = np.where((DF2['fst'].astype(np.float) == 9999.) | (DF2['obs'].astype(np.float) == 9999.), np.nan,
                       DF2['fst'].astype(np.float) - DF2['obs'].astype(np.float))
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
    df_merge_filter['data_change'] = df_merge_filter['data_change'].astype(float)
    data_change = df_merge_filter['data_change']
    data_change[data_change == 9999.] = np.nan
    df_merge_filter['data_change'] = data_change
    df_merge_filter['lon'] = df_merge_filter['lon'].astype(float)
    df_merge_filter['lat'] = df_merge_filter['lat'].astype(float)
    sta = creat_M3_grd(df_merge_filter)
    return sta

def main_draw(RT_list):
    infile_list = []
    if var == 'wind':
        if lev.__contains__('station'):
            lev_filename = lev[:8] + model.lower()
            for report_time in RT_list:
                infile = infile_format.format(var=var, model=model, lev=lev_filename, RT=report_time, cst=cst)
                if os.path.exists(infile):
                    infile_list.append(infile)
        else:
            lev_filename = lev
            for report_time in RT_list:
                infile = windfile_format.format(var=var, model=model, lev=lev_filename, RT=report_time, cst=cst)
                if os.path.exists(infile):
                    infile_list.append(infile)
    else:
        if lev.__contains__('station'):
            lev_filename = lev[:8] + model.lower()
        else:
            lev_filename = lev
        for report_time in RT_list:
            infile = infile_format.format(var=var, model=model, lev=lev_filename, RT=report_time, cst=cst)
            if os.path.exists(infile):
                infile_list.append(infile)

    outfile_format = outfile_month_format.format(var=var, model=model, lev=lev, label=label, inter=inter, RT=RT, cst=cst)
    if lev.__contains__('station'):
        lev_name = lev.split('_')[1] + '站'
        function_draw = metdig_plot_s
        stafile = os.path.join(os.path.dirname(__file__), lev + '.dat')
    else:
        level = lev.split('_')[1]
        if int(level) < 200:
            lev_name = '地面' + level + '米'
        else:
            lev_name = lev.split('_')[1] + 'hPa'
        function_draw = metdig_plot_c
        stafile = None

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


    print('输入数据长度：' + str(len(infile_list)))
    var_dict = {
        'tmp': {
            'ME': [t2m_title.format(model_name, lev_name, label), level_tmp, t2m_var.format(label), cmap],
            'MAE': [t2m_title.format(model_name, lev_name, label), level_tmp_sg, t2m_var.format(label), cmap],
            'RMSE': [t2m_title.format(model_name, lev_name, label), level_tmp_sg, t2m_var.format(label), cmap],
            'PC': [t2m_title_pc.format(model_name, lev_name, label), level_pc, t2m_var_pc.format(label), cmap_pc],
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
            'PC': [wind_title_pc.format(model_name, lev_name, label), level_pc, wind_var_pc.format(label), cmap_pc],
                }
    }
    function_draw(infile_list, outfile_format, var_dict.get(var).get(label), stafile, reBool)

if __name__ == '__main__':
    var = sys.argv[1]
    model = sys.argv[2]
    lev = sys.argv[3]
    label = sys.argv[4]
    inter = sys.argv[5]
    RT = datetime.strptime(sys.argv[6], "%Y%m")
    rt_Hour = sys.argv[7].split(',')
    cst = int(sys.argv[8])
    if len(sys.argv) > 9:
        reBool = sys.argv[9]
    else:
        reBool = 'F'

    RT_list = []
    for rtH in rt_Hour:
        RT_start = RT.replace(day=1, hour=int(rtH))
        RT_end = RT_start + relativedelta.relativedelta(months=1, day=1)
        while RT_start < RT_end:
            RT_list.append(RT_start)
            RT_start += timedelta(days=1)

    main_draw(RT_list)
    #wind FENGWU station_10290 MAE month 2023080108 12 T