import gc
import os.path
import locale
import metdig
from datetime import datetime
from matplotlib import font_manager
from cartopy.io.img_tiles import Stamen
import cartopy.feature as cfeature
import metdig.graphics.lib.utl_plotmap as utl_plotmap
from metdig.graphics.barbs_method import *
from metdig.graphics.pcolormesh_method import *
from metdig.graphics.draw_compose import *
from metdig.cal import other
from meteva.base.tool.plot_tools import add_china_map_2basemap
from .config_single import *

font_manager.fontManager.addfont(os.path.join(os.path.dirname(__file__), 'SIMHEI.TTF'))


def draw_uv_nafp(u, v, wsp, map_extent, regrid_shape, Filter_min, Filter_max, **kwargs):

    data_name = str(u['member'].values[0])
    title = '[{}]10m 风速'.format(
        data_name.upper())

    forcast_info = u.stda.description() + '平均值'

    if regrid_shape[0] == 'CHN' or regrid_shape[0] == 'JNHN':
        add_scs_value = True
    else:
        add_scs_value = False

    fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info, add_south_china_sea=add_scs_value)
    obj = horizontal_compose(title=title, description=forcast_info, add_tag=False,
                             map_extent=map_extent, fig=fig, ax=ax, kwargs=kwargs)
    obj.ax.tick_params(labelsize=16)
    lat_lon_value = wsp.data[0][0][0][0]
    lat_lon_value[lat_lon_value < Filter_min] = np.nan
    lat_lon_value[lat_lon_value > Filter_max] = np.nan
    wsp.data = [[[[lat_lon_value]]]]
    wsp_pcolormesh(obj.ax, wsp, levels=[2, 4, 6, 8, 10, 12, 14], colorbar_kwargs={'pad': 0.05, 'extend': 'both'}, cmap='ncl/wind_17lev', alpha=1)
    gc.collect()
    uv_barbs(obj.ax, u, v, regrid_shape=regrid_shape[1], sizes=dict(emptybarb=0), length=5)
    obj.save()

def draw_uv_cldas(u_c, v_c, wsp, map_extent, disc, regrid_shape, Filter_min, Filter_max, **kwargs):
    data_name = str(u_c['member'].values[0])
    title = '[{}]风速'.format(data_name.upper())
    rp_endT = datetime.strptime(disc[-18:-8], '%Y%m%d%H')
    rp_startT = datetime.strptime(kwargs.get('output_dir').split('/')[-2], '%Y%m%d%H')
    forcast_info = '实况时间：{}年{}月{}日-{}年{}月{}日 {}时平均值'.format(
        rp_startT.year, rp_startT.month, rp_startT.day,
        rp_endT.year, rp_endT.month, rp_endT.day, rp_endT.hour)

    if regrid_shape[0] == 'CHN' or regrid_shape[0] == 'JNHN':
        add_scs_value = True
    else:
        add_scs_value = False

    fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info, add_south_china_sea=add_scs_value)
    obj = horizontal_compose(title=title, description=forcast_info, add_tag=False, map_extent=map_extent, fig=fig,
                             ax=ax, kwargs=kwargs)
    obj.ax.tick_params(labelsize=16)
    lat_lon_value = wsp.data[0][0][0][0]
    lat_lon_value[lat_lon_value < Filter_min] = np.nan
    lat_lon_value[lat_lon_value > Filter_max] = np.nan
    wsp.data = [[[[lat_lon_value]]]]
    wsp_pcolormesh(obj.ax, wsp, levels=[2, 4, 6, 8, 10, 12, 14], colorbar_kwargs={'pad': 0.05, 'extend': 'both'}, cmap='ncl/wind_17lev', alpha=1)
    gc.collect()
    uv_barbs(obj.ax, u_c, v_c, regrid_shape=regrid_shape[1], sizes=dict(emptybarb=0), length=5)
    obj.save()

def plt_base_env():
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

    if (sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN.utf8')
    if (sys.platform[0:3] == 'win'):
        locale.setlocale(locale.LC_CTYPE, 'chinese')


def horizontal_pallete_test(ax=None, figsize=(16, 9), crs=ccrs.PlateCarree(), map_extent=(60, 145, 15, 55), step=10,
                            title='', title_fontsize=18, forcast_info='', nmc_logo=False,
                            add_coastline=True, add_china=True, add_province=True, add_river=True, add_city=False,
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
        utl_plotmap.add_china_map_2cartopy_public(ax, name='coastline', edgecolor='gray', lw=0.5, zorder=19, alpha=1,
                                                  crs=ccrs.PlateCarree())
    if add_china:
        utl_plotmap.add_china_map_2cartopy_public(ax, name='nation', edgecolor='black', lw=1.5, zorder=19,
                                                  crs=ccrs.PlateCarree())
    if add_province:
        utl_plotmap.add_china_map_2cartopy_public(ax, name='province', edgecolor='gray', lw=1, zorder=19,
                                                  crs=ccrs.PlateCarree())

    if add_river:
        utl_plotmap.add_china_map_2cartopy_public(ax, name='river', edgecolor='#B94FFF', lw=1, zorder=10, alpha=1,
                                                  crs=ccrs.PlateCarree())
        # add_china_map_2basemap(ax, name="province", edgecolor='gray', lw=0.5, encoding='gbk', zorder=0)
        # add_china_map_2basemap(ax, name="nation", edgecolor='black', lw=0.8, encoding='gbk', zorder=0)
    if add_county:
        add_china_map_2basemap(ax, name="county", edgecolor='#D9D9D9', lw=0.1, encoding='gbk', zorder=0)
        # add_china_map_2basemap(ax, name="river", edgecolor='#74b9ff', lw=0.8, encoding='gbk', zorder=1)
        pass

    # 城市名称
    if add_city:
        # small_city = False
        # if(map_extent[1] - map_extent[0] < 25):
        #     small_city = True
        utl_plotmap.add_city_on_map(ax, map_extent=map_extent, transform=ccrs.PlateCarree(),
                                    zorder=101, size=13)
    if add_county_city:
        # small_city = False
        # if(map_extent[1] - map_extent[0] < 25):
        #     small_city = True
        utl_plotmap.add_city_on_map(ax, map_extent=map_extent, transform=ccrs.PlateCarree(),
                                    zorder=101, size=13, city_type='county')

    # 背景图
    if add_background_style is None:
        # ax.add_feature(cfeature.OCEAN, facecolor='#EDFBFE')
        # ax.add_feature(cfeature.LAND, facecolor='#FCF6EA')
        # add_china_map_2basemap(ax, name="world", edgecolor='gray', lw=0.1, encoding='gbk',zorder=19)
        utl_plotmap.add_china_map_2cartopy_public(ax, name='world', edgecolor='gray', lw=1, zorder=19,
                                                  crs=ccrs.PlateCarree())
    elif add_background_style == 'RD':
        utl_plotmap.add_china_map_2cartopy_public(ax, name='world', edgecolor='gray', lw=1, zorder=19,
                                                  crs=ccrs.PlateCarree())
        # add_china_map_2basemap(ax, name="world", edgecolor='gray', lw=0.5, encoding='gbk',zorder=19)
        # ax.add_feature(cfeature.OCEAN)
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

        # plt.tick_params(labelsize=32)
        # ax.set_yticks(np.arange(map_extent[2], map_extent[3]+1, 10), crs=ccrs.PlateCarree())
        # ax.set_xticks(np.arange(map_extent[0], map_extent[1]+1, 10), crs=ccrs.PlateCarree())
        # lon_formatter = LongitudeFormatter(dateline_direction_label=True)
        # lat_formatter = LatitudeFormatter()
        # ax.xaxis.set_major_formatter(lon_formatter)
        # ax.yaxis.set_major_formatter(lat_formatter)

    # 南海
    if add_south_china_sea:
        l, b, w, h = ax.get_position().bounds
        utl_plotmap.add_south_china_sea_png(pos=[l + w - 0.1, b + 0.005, 0.11, 0.211], name='white')  # 直接贴图

    # 预报/分析描述信息
    if forcast_info:
        ax.text(0.01, 0.99, forcast_info, transform=ax.transAxes, size=12, va='top',
                ha='left', bbox=dict(facecolor='#FFFFFFCC', edgecolor='black', pad=3.0), zorder=20)

    # logo

    if nmc_logo:
        l, b, w, h = ax.get_position().bounds
        # utl.add_logo_extra_in_axes(pos=[l - 0.02, b + h - 0.1, .1, .1], which='nmc', size='Xlarge') # 左上角
        utl.add_logo_extra_in_axes(pos=[l + w - 0.08, b + h - 0.1, .1, .1], which='nmc', size='Xlarge')  # 右上角

    # 添加 powered by metdig
    if (add_tag):
        t = ax.text(0.01, 0.028, 'Powered by MetDig', transform=ax.transAxes, size=15,
                    color='black', alpha=1.0, va='bottom', ha='left', zorder=100)  # 左下角图的里面
        t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='#D9D9D9'),
                            mpatheffects.Normal()])
        t = ax.text(0.01, 0.003, 'https://github.com/nmcdev/metdig', transform=ax.transAxes, size=10,
                    color='black', alpha=1.0, va='bottom', ha='left', zorder=100)  # 左下角图的里面
        t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='#D9D9D9'),
                            mpatheffects.Normal()])
    # ax.text(1.00, -0.12, 'Powered by MetDig', transform=ax.transAxes, size=14, color='gray', alpha=1.0, va='bottom',  ha='right')  # 右下角图的外面，colorbar的下边
    # ax.text(1.00, -0.005, 'Powered by MetDig', transform=ax.transAxes, size=14, color='gray', alpha=1.0, va='top',  ha='right' )  # 右下角图的外面刻度线的位置
    return fig, ax


class PlotHgtWindProd_sg:
    def __init__(self, model_name, u, v, u_c, v_c):
        """

        :param hgt:
        :param u:
        :param v:
        """
        self.model_name = model_name
        self.u = metdig.utl.xrda_to_gridstda(u, level_dim='level', time_dim='time', lat_dim='lat',
                                             lon_dim='lon', dtime_dim='dtime',
                                             var_name='u', np_input_units='m/s')
        self.v = metdig.utl.xrda_to_gridstda(v, level_dim='level', time_dim='time', lat_dim='lat',
                                             lon_dim='lon', dtime_dim='dtime',
                                             var_name='v', np_input_units='m/s')
        self.wind_speed = other.wind_speed(self.u, self.v)
        u.close()
        v.close()

        if u_c is not None and v_c is not None:
            self.u_c = metdig.utl.xrda_to_gridstda(u_c, level_dim='level', time_dim='time', lat_dim='lat',
                                                   lon_dim='lon', dtime_dim='dtime',
                                                   var_name='u', np_input_units='m/s')
            self.v_c = metdig.utl.xrda_to_gridstda(v_c, level_dim='level', time_dim='time', lat_dim='lat',
                                                   lon_dim='lon', dtime_dim='dtime',
                                                   var_name='v', np_input_units='m/s')
            v_c.close()
            u_c.close()

    def plot_hgt_wind_speed_sg(self, region_name, region, file_path, Filter_min=-9999.0, Filter_max=9999.0):
        """
        高度场和风场
        :param lev:
        :param report_time:
        :param cst:
        :param out_name:
        :param region_name:
        :param region:
        :return:
        """
        region_num = {
            "EA": 40, "CHN": 40,
            "NE": 30, "HB": 30,
            "HHJH": 30, "JNHN": 30,
            "XN": 30, "NW": 20
        }
        if self.model_name == 'CLDAS':

            draw_uv_cldas(self.u, self.v, self.wind_speed, map_extent=region,
                                     regrid_shape = [region_name, region_num.get(region_name)],
                                     output_dir=os.path.dirname(file_path), disc=os.path.basename(file_path),
                                     png_name=os.path.basename(file_path), is_clean_plt=True, add_city=False,
                                     Filter_min=Filter_min, Filter_max=Filter_max)
        else:
            draw_uv_nafp(self.u, self.v, self.wind_speed, map_extent=region, output_dir=os.path.dirname(file_path),
                               png_name=os.path.basename(file_path), is_clean_plt=True, add_city=False,
                               regrid_shape = [region_name, region_num.get(region_name)], Filter_min=Filter_min, Filter_max=Filter_max)