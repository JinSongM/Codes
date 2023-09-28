# -- coding: utf-8 --
# @Time : 2023/9/4 15:33
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : yl.py
# @Software: PyCharm
import os
import metdig
import os.path
import pandas as pd
import meteva.base as meb
from metdig.cal import other
import cartopy.feature as cfeature
from datetime import datetime, timedelta
from cartopy.io.img_tiles import Stamen
from metdig.graphics.barbs_method import *
from metdig.graphics.contour_method import *
from metdig.graphics.pcolormesh_method import *
from metdig.graphics.draw_compose import *
import metdig.graphics.lib.utl_plotmap as utl_plotmap
from meteva.base.tool.plot_tools import add_china_map_2basemap

class PlotHgtWindProd:
    def __init__(self, model_name, hgt, u, v):
        """

        :param hgt:
        :param u:
        :param v:
        """
        self.gh = metdig.utl.xrda_to_gridstda(hgt, level_dim='level', time_dim='time', lat_dim='lat',
                                              lon_dim='lon', dtime_dim='dtime',
                                              var_name='gh', np_input_units='hPa')
        self.u = metdig.utl.xrda_to_gridstda(u, level_dim='level', time_dim='time', lat_dim='lat',
                                             lon_dim='lon', dtime_dim='dtime',
                                             var_name='u', np_input_units='m/s')
        self.v = metdig.utl.xrda_to_gridstda(v, level_dim='level', time_dim='time', lat_dim='lat',
                                             lon_dim='lon', dtime_dim='dtime',
                                             var_name='v', np_input_units='m/s')

        self.wind_speed = other.wind_speed(self.u, self.v)
        hgt.close()
        u.close()
        v.close()
        self.model_name = model_name
        self.path = MODEL_SAVE_OUT

    def plot_hgt_wind_rh(self, rh, report_time, cst, out_name, region_name, region, lev):
        """
        高度场、风场、相对湿度
        :param lev:
        :param rh:
        :param report_time:
        :param cst:
        :param out_name:
        :param region_name:
        :param region:
        :return:
        """

        file_path = self.path.format(model=self.model_name, report_time=report_time, cst=cst, lev=lev,
                                     out_name=out_name, region=region_name)
        if os.path.exists(file_path):
            return
        std_data = metdig.utl.xrda_to_gridstda(rh, level_dim='level', time_dim='time', lat_dim='lat',
                                               lon_dim='lon', dtime_dim='dtime',
                                               var_name='rh', np_input_units='%')
        rh.close()
        draw_hgt_uv_rh_588(self.gh, self.u, self.v, std_data, map_extent=region, region=region_name,
                           output_dir=os.path.dirname(file_path),
                           png_name=os.path.basename(file_path), is_clean_plt=True, add_city=False)
        std_data.close()


def draw_hgt_uv_rh_588(hgt, u, v, rh, map_extent=(60, 145, 15, 55), region=None,
                       rh_pcolormesh_kwargs={}, uv_barbs_kwargs={}, hgt_contour_kwargs={},
                       **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    data_name = str(hgt['member'].values[0])
    title = '[{}] {}hPa 位势高度场, {}hPa 风场, {}hPa 相对湿度'.format(data_name.upper(), int(hgt['level'].values[0]),
                                                            int(u['level'].values[0]), int(rh['level'].values[0]))

    forcast_info = hgt.stda.description()
    png_name = '{2}_位势高度场_风场_相对湿度_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour,
                                                                                              data_name.upper())
    fig, ax = horizontal_pallete_test(map_extent=map_extent, crs=ccrs.PlateCarree(central_longitude=0),
                                      step=10, forcast_info=forcast_info)
    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent,
                             add_tag=False, fig=fig, ax=ax, kwargs=pallete_kwargs)
    obj.ax.tick_params(labelsize=16)
    cmap_r = r_color
    rh_pcolormesh(obj.ax, rh, colorbar_kwargs={'pad': 0.05}, kwargs=rh_pcolormesh_kwargs, cmap=cmap_r, alpha=0.9)
    uv_barbs(obj.ax, u, v, regrid_shape=20, sizes=dict(emptybarb=0), kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, levels=contour_levels, kwargs=hgt_contour_kwargs)
    hgt_contour_588(obj.ax, hgt)
    obj.save()

def plot_wind(model_name, report_time, cst):

    gh_data_path = MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element="gh", lev="500")
    u_data_path = MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element="u", lev="850")
    v_data_path = MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element="v", lev="850")
    gh_data = meb.read_griddata_from_micaps4(gh_data_path)
    u_data = meb.read_griddata_from_micaps4(u_data_path)
    v_data = meb.read_griddata_from_micaps4(v_data_path)

    try:
        pwp = PlotHgtWindProd(model_name, gh_data, u_data, v_data)

        for lev in LEV:
            rh_data_path = MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element="r", lev=lev)
            rh_data = meb.read_griddata_from_micaps4(rh_data_path)
            if rh_data is not None:
                pwp.plot_hgt_wind_rh(rh_data, report_time, cst, "gh500_wind850_r", "CHN", [70, 150, 10, 60], lev)
    except:
        print('Error')

def hgt_contour_588(ax, stda, xdim='lon', ydim='lat',
                    add_clabel=True,
                    levels=np.arange(588, 592, 4), colors='red',
                    transform=ccrs.PlateCarree(), linewidths=3,
                    **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # dagpm

    img = ax.contour(x, y, z, levels=levels, transform=transform, colors=colors, linewidths=linewidths, **kwargs)
    if add_clabel:
        plt.clabel(img, inline=1, fontsize=20, fmt='%.0f', colors='red')
    return img

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
    return fig, ax

if __name__ == '__main__':
    MODEL_ROOT = "/data/cpvs/test/{model}/{element}/{lev}/{report_time:%Y}/{report_time:%Y%m%d%H}/" \
                 "{report_time:%Y%m%d%H}.{cst:03d}"
    MODEL_SAVE_OUT = "/data/cpvs/Product/synoptic/{model}/{report_time:%Y%m%d%H}/{out_name}/{lev}/" \
                     "{region}_{report_time:%Y%m%d%H}.{cst:03d}.png"
    r_color = 'PRGn'
    contour_levels = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95]
    LEV = [500, 700, 850, 925]

    model_name, report_time, cst = sys.argv[1], datetime.strptime(sys.argv[2], '%Y%m%d%H'), int(sys.argv[3])
    plot_wind(model_name, report_time, cst)
