import sys
# import meteva
import numpy as np
import os
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
from gma.extend import mapplottools as mpt

PAR = {'font.sans-serif': 'Times New Roman',
       'font.size': 18,
       'axes.unicode_minus': False}
plt.rcParams.update(PAR)
plt.rcParams['axes.linewidth'] = 0
china_shp = r'D:\data\datasource\Geoserver\2023最新行政边界\2023年省级\2023年初省级矢量.shp'
nine_shp = r'D:\data\datasource\Geoserver\2023最新行政边界\九段线\九段线.shp'

def draw_lbt(infile, outfile):
    fig = plt.figure(figsize=(16, 9), dpi=180)
    proj_info = ccrs.LambertConformal(central_longitude=105,
                                  central_latitude=36,
                                  standard_parallels=(25.0, 47.0))
    ax = fig.add_subplot(projection=proj_info)
    plt.title('[盘古200hPa]温度平均误差(℃)\n', loc='left', fontsize=18, fontdict={'family': 'simhei'})
    file_time = os.path.split(infile)[1].split('.')[0]
    Fst_time = int(os.path.split(infile)[1].split('.')[1])
    obs_time_dc = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(datetime.strptime(file_time, '%Y%m%d%H'))
    fst_time_dc = '预报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(
        datetime.strptime(file_time, '%Y%m%d%H') + timedelta(hours=Fst_time))
    forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时'.format(Fst_time)
    plt.title(forcast_info, loc='right', fontsize=11, fontdict={'family': 'simhei'})
    # ax.text(50,45, forcast_info, fontsize=14, fontdict={'family': 'simsun'}, transform=ccrs.PlateCarree())
    #设置xy轴坐标
    box, xstep, ystep = [70, 140, 10, 60], 1, 1
    ax.set_extent(box, crs=ccrs.PlateCarree())
    gridliner = ax.gridlines(draw_labels=True, crs=ccrs.PlateCarree(),
                       color='k', linestyle='dashed', linewidth=0.3,
                       y_inline=False, x_inline=False,
                       rotate_labels=0, xpadding=5,
                       xlocs=range(-180, 180, 10), ylocs=range(-90, 90, 10),
                       xlabel_style={"size": 12, "weight": "bold"},
                       ylabel_style={"size": 12, "weight": "bold"}
                       )
    gridliner.xlabels_top = False
    gridliner.xlabels_bottom = True
    gridliner.ylabels_left = True
    gridliner.ylabels_right = False
    # 标注矢量边界
    china_reader, nine_reader = Reader(china_shp), Reader(nine_shp)
    enshicity = cfeature.ShapelyFeature(china_reader.geometries(), ccrs.PlateCarree(), edgecolor='gray', facecolor='none')#'oldlace'
    ax.add_feature(enshicity, linewidth=0.7, zorder=2)  # 添加市界细节
    enshicity = cfeature.ShapelyFeature(nine_reader.geometries(), ccrs.PlateCarree(), edgecolor='gray', facecolor='none')#'oldlace'
    ax.add_feature(enshicity, linewidth=0.7, zorder=2)  # 添加市界细节

    grd = meteva.base.read_griddata_from_micaps4(infile)
    lon, lat = grd.lon.to_numpy(), grd.lat.to_numpy()
    LON, LAT = np.meshgrid(lon, lat)
    data_array = np.squeeze(grd.data)
    cmap_tem, ticks = 'RdYlGn_r', [i/10 for i in range(-20, 24, 5)]
    # 绘制等值线填充图
    cs = ax.contourf(LON, LAT, data_array, cmap=cmap_tem, levels=ticks, transform=ccrs.PlateCarree(), zorder=1, extend='both')
    #aspect：色标宽度, shrink：色标缩放
    plt.colorbar(cs, ax=ax, aspect=50, shrink=0.6, pad=0.08, location='bottom')

    # ax.scatter(LON, LAT, marker='D', s=8, c=value, cmap=cmp, norm=norm, transform=ccrs.PlateCarree(), zorder=2)
    # ax2 = fig.add_axes([0.83, 0.09, 0.13, 0.25], projection=proj_info)
    # ax2.set_extent([104.5, 125, 0, 26])
    # ax2.set_facecolor('#BEE8FF')
    # ax2.spines['geo'].set_linewidth(.2)
    # # 设置网格点
    # lb = ax2.gridlines(draw_labels=False, x_inline=False, y_inline=False,
    #                    linewidth=0.1, color='gray', alpha=0.8,
    #                    linestyle='--')
    # ax2.add_feature(enshicity, linewidth=0.7)  # 添加市界细节

    # 添加指北针\添加比例尺
    mpt.AddCompass(ax, LOC=(0.12, 0.14), SCA=0.04, FontSize=8)
    mpt.AddScaleBar(ax, LOC=(0.15, 0.05), SCA=0.08, FontSize=12, UnitPad=0.3, BarWidth=0.8)
    # plt.legend(bbox_to_anchor=(0.5, 1.08), loc=9, ncol=4, frameon=False, markerscale=2, handletextpad=0.1)
    fig.savefig(outfile, bbox_inches='tight')


if __name__ == '__main__':
    date_t = datetime.strptime(sys.argv[1], '%Y%m%d%H')
    cst = int(sys.argv[2])
    infile_format = r'/data/data/tmp/{TT:%Y}/{TT:%Y%m%d}/{TT:%Y%m%d%H}.{cst:03d}'
    outfile_format = r'/data/data/result/tmp/{TT:%Y}/{TT:%Y%m%d}/{TT:%Y%m%d%H}.{cst:03d}.png'

    draw_lbt(infile_format.format(TT=date_t, cst=cst), outfile_format.format(TT=date_t, cst=cst))