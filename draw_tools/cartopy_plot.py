import glob
import os.path
import sys
import meteva.base as meb
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from datetime import datetime, timedelta
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import numpy as np
from cartopy.io.shapereader import Reader
import matplotlib.colors as colors
from matplotlib.colors import ListedColormap
from pathlib import Path
plt.rcParams.update({
    'font.sans-serif': 'Times New Roman',
    'font.size': 14
    })
plt.rcParams['axes.unicode_minus']=False

china_shp = r'D:\data\datasource\Geoserver\Geoserver\全国边界线\chinaGJSJ\china_20220325.shp'
worldmap_shp = r'D:\data\datasource\Geoserver\Geoserver\全国边界线\coastLine\worldmap.shp'
coastline_shp = r'D:\data\datasource\Geoserver\Geoserver\全国边界线\coastLine\ne_10m_coastline.shp'
southsea_png = r'D:\data\datasource\Geoserver\Geoserver\全国边界线\coastLine\white.png'
ticks = [i for i in range(245, 321, 4)]
cmap_tem = 'ncl/ncl_default'
# cmap_col = ['#FFFFFF', '#43CE17', '#EFDC31', '#FFAA00', '#FF401A', '#D20040', '#9C0A4E', '#9C0A4E']
# cmp = colors.ListedColormap(cmap_col)
# norm = colors.BoundaryNorm(ticks, cmp.N)


def contourf_plot(infile, box, outfile, obs_time):
    #获取数据经纬度及二维矩阵
    xr_data = meb.read_griddata_from_nc(infile)
    fig = plt.figure(figsize=(16, 9), dpi=120)
    ax = plt.axes(projection=ccrs.PlateCarree())
    plt.title('沙尘', loc='left', fontsize=20, fontdict={'family': 'simhei'})
    LAT = xr_data.lat.to_numpy()
    LON = xr_data.lon.to_numpy()
    xr_data_array = xr_data.data[0][0][0][0]
    data_array_new = np.where(xr_data_array > 0, xr_data_array + 10, xr_data_array)

    #设置xy轴坐标
    box, xstep, ystep = box, 0.02, 0.02
    ax.set_xticks(np.arange(int(box[0]), box[1] + xstep, 10)) #xstep * 100
    ax.set_yticks(np.arange(int(box[2]), box[3] + ystep, 10))
    ax.set_extent(box, crs=ccrs.PlateCarree())
    plt.tick_params(axis="both", which="major", width=1, length=5)

    #设置预报描述信息
    OBS_time = obs_time
    # 添加描述信息
    obs_time_dc = '实况时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(OBS_time)
    forcast_info = obs_time_dc
    ax.text(0.01, 0.985, forcast_info, transform=ax.transAxes, size=12, va='top', font=Path('./simsun.ttc'),
            ha='left', bbox=dict(facecolor='#FFFFFFCC', edgecolor='black', pad=3.0), zorder=20)

    #设置经纬度显示格式
    # zero_direction_label用来设置经度的0度加不加E和W
    lon_formatter = LongitudeFormatter(zero_direction_label=False)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)

    # 绘制等值线填充图
    # cs = plt.contourf(LON, LAT, data_array_new, cmap=ListedColormap(cmap_col), levels=ticks)
    cs = plt.contourf(LON, LAT, data_array_new, cmap=cmap_tem, levels=ticks)
    #aspect：色标宽度, shrink：色标缩放
    fig.colorbar(cs, ax=ax, aspect=50, shrink=0.6, pad=0.08, location='bottom', ticks=ticks, label=ticks)

    # colorlevel = np.arrange()
    # cmap = mpl.cm.Blues
    # norm = mcolors.BoundaryNorrm(colorlevel, not cmap)
    # ax.pcolormesh(lon, lat, RH, transform=ccrs.PlateCarree(), cmap=cmap, norm = norm)


    # 绘制风羽图
    # plt.barbs(LON, LAT, U10, V10, regrid_shape=regrid_shape, transform=transform, sizes=dict(emptybarb=0),
    # barbcolor='b', barb_increments={'half':5,'full':10,'flag':20}, length=6)

    # 绘制散点图
    # cs = plt.scatter(LON, LAT, marker='.', s=5, c=value, cmap=cmp, norm=norm)
    # fig.colorbar(cs, aspect=50, shrink=0.5, pad=0.08, orientation='horizontal', extend='both', ticks=ticks)

    # 标注矢量边界
    china_reader, worldmap_reader, coastline_reader = Reader(china_shp), Reader(worldmap_shp), Reader(coastline_shp)
    enshicity = cfeature.ShapelyFeature(china_reader.geometries(), ccrs.PlateCarree(), edgecolor='k', facecolor='none')
    ax.add_feature(enshicity, linewidth=0.7)  # 添加市界细节
    enshicity = cfeature.ShapelyFeature(worldmap_reader.geometries(), ccrs.PlateCarree(), edgecolor='grey', facecolor='none')
    ax.add_feature(enshicity, linewidth=0.6)  # 添加市界细节
    enshicity = cfeature.ShapelyFeature(coastline_reader.geometries(), ccrs.PlateCarree(), edgecolor='grey', facecolor='none')
    ax.add_feature(enshicity, linewidth=0.6)  # 添加市界细节
    ax.add_feature(cfeature.STATES.with_scale('50m'), edgecolor='grey', alpha=0.8)
    # ax.add_feature(cfeature.COASTLINE.with_scale('50m'), edgecolor='grey', alpha=0.8)

    #保存文件
    if not os.path.exists(os.path.dirname(outfile)):
        os.makedirs(os.path.dirname(outfile))
    plt.savefig(outfile, bbox_inches='tight')
    print('成功输出至：' + outfile)
    plt.close()

if __name__ == '__main__':
    infile = r"D:\data\datasource\sc\data\{rp_t:%Y%m%d}\{rp_t:%Y%m%d%H}00.nc"
    outfile = r"D:\data\datasource\sc\result\{rp_t:%Y%m%d}\{rp_t:%Y%m%d%H}00.png"
    box = [70, 140, 10, 60]
    stime = datetime.strptime(sys.argv[1].ljust(10, '0'), '%Y%m%d%H')
    etime = datetime.strptime(sys.argv[2].ljust(10, '0'), '%Y%m%d%H')
    begin_t = stime
    while begin_t <= etime:
        infile_path = infile.format(rp_t=begin_t)
        outfile_path = outfile.format(rp_t=begin_t)
        contourf_plot(infile_path, box, outfile_path, begin_t)
        begin_t += timedelta(hours=1)