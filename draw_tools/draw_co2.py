# -- coding: utf-8 --
# @Time : 2023/6/18 10:37
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : cartopy_plot.py
# @Software: PyCharm
import glob
import os.path
import sys
import numpy as np
import meteva.base as meb
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from datetime import datetime, timedelta
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import metdig.graphics.lib.utl_plotmap as utl_plotmap
from cartopy.io.shapereader import Reader
from matplotlib import colors


from pathlib import Path
plt.rcParams.update({
    'font.sans-serif': 'Times New Roman',
    'font.size': 18
    })
plt.rcParams['axes.unicode_minus']=False

class argparseConfig:
    """
    配置文件
    params:
    return:
    """
    def __init__(self):
        self.china_shp = r'D:\data\datasource\Geoserver\Geoserver\全国边界线\chinaGJSJ\china_20220325.shp'
        self.worldmap_shp = r'D:\data\datasource\Geoserver\Geoserver\全国边界线\coastLine\worldmap.shp'
        self.coastline_shp = r'D:\data\datasource\Geoserver\Geoserver\全国边界线\coastLine\ne_10m_coastline.shp'
        self.southsea_png = r'D:\data\datasource\Geoserver\Geoserver\全国边界线\coastLine\white.png'

        self.levels_radar = [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70]
        self.colors_radar = ['#01A0F6', '#00ECEC', '#00D800', '#019000', '#FFFF00', '#E7C000', '#FF9000', '#FF0000', '#D60000', '#C00000',
                  '#FF00F0', '#9600B4', '#AD90F0']
        self.levels_wind = [2, 4, 6, 8, 10, 12, 14]
        self.colors_wind = ['#FFFFFF', '#E8F49E', '#FFED00', '#EDA549', '#EF073D', '#6171F6', '#B5C9FF']
        self.levels_scatter = [10, 20, 30, 40, 50, 60, 70]
        self.colors_scatter = ['#E8F49E', '#01A0F6', '#E8F49E', '#FFED00', '#EDA549', '#EF073D', '#6171F6', '#B5C9FF']
        import metdig.graphics.cmap.cm as cm_collected
        self.cmap, self.norm = cm_collected.get_cmap('ncl/WhiteBlueGreenYellowRed', extend='both', levels=np.arange(350, 432, 2))

        self.cmap_radar = colors.ListedColormap(self.colors_radar)
        self.norm_radar = colors.BoundaryNorm(self.levels_radar, self.cmap_radar.N - 1)

        self.cmap_wind = colors.ListedColormap(self.colors_wind)
        self.norm_wind = colors.BoundaryNorm(self.levels_wind, self.cmap_wind.N - 1)

        self.cmap_scatter = colors.ListedColormap(self.colors_scatter)
        self.norm_scatter = colors.BoundaryNorm(self.levels_scatter, self.cmap_scatter.N, extend='both')

        '''
        1 plt.rcParams[’axes.unicode_minus’] = False 字符显示
        2 plt.rcParams[’font.sans-serif’] = ‘SimHei’ 设置字体
        线条样式：lines
        3 plt.rcParams[’lines.linestyle’] = ‘-.’ 线条样式
        4 plt.rcParams[’lines.linewidth’] = 3 线条宽度
        5 plt.rcParams[’lines.color’] = ‘blue’ 线条颜色
        6 plt.rcParams[’lines.marker’] = None 默认标记
        7 plt.rcParams[’lines.markersize’] = 6 标记大小
        8 plt.rcParams[’lines.markeredgewidth’] = 0.5 标记附近的线宽
        横、纵轴：xtick、ytick
        9 plt.rcParams[’xtick.labelsize’] 横轴字体大小
        10 plt.rcParams[’ytick.labelsize’] 纵轴字体大小
        11 plt.rcParams[’xtick.major.size’] x轴最大刻度
        12 plt.rcParams[’ytick.major.size’] y轴最大刻度
        figure中的子图：axes
        13 plt.rcParams[’axes.titlesize’] 子图的标题大小
        14 plt.rcParams[’axes.labelsize’] 子图的标签大小
        图像、图片：figure、savefig
        15 plt.rcParams[’figure.dpi’] 图像分辨率
        16 plt.rcParams[’figure.figsize’] 图像显示大小
        17 plt.rcParams[’savefig.dpi’] 图片像素
        '''

class draw_tools(argparseConfig):

    def __init__(self, box, ax, fileName, outfile):
        super().__init__()
        self.box = box
        self.ax = ax
        self.fileName = fileName
        self.outfile = outfile

    def add_ticks(self):
        # 设置xy轴坐标
        box, xstep, ystep = self.box, 1, 1
        self.ax.set_xticks(np.arange(int(box[0]), box[1] + xstep, xstep * 10))  # xstep * 100
        self.ax.set_yticks(np.arange(int(box[2]), box[3] + ystep, xstep * 10))
        self.ax.set_extent(box, crs=ccrs.PlateCarree())
        plt.tick_params(axis="both", which="major", width=1, length=5)
        lon_formatter = LongitudeFormatter(zero_direction_label=False)
        lat_formatter = LatitudeFormatter()
        self.ax.xaxis.set_major_formatter(lon_formatter)
        self.ax.yaxis.set_major_formatter(lat_formatter)

    def add_annotate_fst(self):
        # 设置添加预报数据描述信息
        reportTime, cst = self.fileName.split('.')[0], int(self.fileName.split('.')[1])
        obs_time_dc = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(datetime.strptime(reportTime, '%Y%m%d%H'))
        fst_time_dc = '预报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(
            datetime.strptime(reportTime, '%Y%m%d%H') + timedelta(hours=cst))
        forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时'.format(cst)
        self.ax.text(0.01, 0.985, forcast_info, transform=self.ax.transAxes, size=12, va='top', fontdict={'family': 'simhei'},
                ha='left', bbox=dict(facecolor='#FFFFFFCC', edgecolor='black', pad=3.0), zorder=20)

    def add_annotate_obs(self):
        # 设置添加实况数据描述信息
        reportTime, cst = self.fileName.split('.')[0], int(self.fileName.split('.')[1])
        forcast_info = '实况时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(datetime.strptime(reportTime, '%Y%m%d%H'))
        self.ax.text(0.01, 0.985, forcast_info, transform=self.ax.transAxes, size=12, va='top', fontdict={'family': 'simhei'},
                ha='left', bbox=dict(facecolor='#FFFFFFCC', edgecolor='black', pad=3.0), zorder=20)

    def add_annotate_custom(self, x, y, describe, c, font_size):
        # 设置添加自定义描述信息
        self.ax.text(x, y, describe, c=c, fontsize=font_size, fontdict={'family': 'simhei'}, zorder=20)

    def add_south_china_sea(self):
        # 添加南海小地图
        l, b, w, h = self.ax.get_position().bounds
        utl_plotmap.add_south_china_sea_png(pos=[l + w - 0.1, b + 0.005, 0.11, 0.211], name='white')  # 直接贴图

    def add_shpfiles(self):
        # 标注矢量边界
        china_reader, worldmap_reader, coastline_reader = Reader(self.china_shp), Reader(self.worldmap_shp), Reader(self.coastline_shp)
        enshicity = cfeature.ShapelyFeature(china_reader.geometries(), ccrs.PlateCarree(), edgecolor='k',
                                            facecolor='none')
        self.ax.add_feature(enshicity, linewidth=0.7, zorder=2)  # 添加省界细节
        enshicity = cfeature.ShapelyFeature(worldmap_reader.geometries(), ccrs.PlateCarree(), edgecolor='grey',
                                            facecolor='none')
        self.ax.add_feature(enshicity, linewidth=0.6, zorder=1)  # 添加国界细节
        enshicity = cfeature.ShapelyFeature(coastline_reader.geometries(), ccrs.PlateCarree(), edgecolor='grey',
                                            facecolor='none')
        self.ax.add_feature(enshicity, linewidth=0.6, zorder=1)  # 添加海岸线细节
        # ax.add_feature(cfeature.STATES.with_scale('50m'), edgecolor='grey', alpha=0.8)

    def save_fig(self):
        # 保存文件
        if not os.path.exists(os.path.dirname(self.outfile)):
            os.makedirs(os.path.dirname(self.outfile))
        plt.savefig(self.outfile, bbox_inches='tight')
        print('成功输出至：' + self.outfile)
        plt.close()

class draw_barbsMap(argparseConfig):
    """
    绘制风羽图
    Args:
    Returns:
        [type]: [绘图对象]
    """
    def __init__(self, infile_U, infile_V, outfile, box, title_name, colorbar_name):
        super().__init__()
        self.U = infile_U
        self.V = infile_V
        self.box = box
        self.outfile = outfile
        self.title_name = title_name
        self.colorbar_name = colorbar_name

    def transformUV(self, u, v):
        from metpy.units import units
        import metpy.calc as mpcalc
        data_u = units.Quantity(u, 'm/s')
        data_v = units.Quantity(v, 'm/s')
        data_dir = mpcalc.wind_direction(data_u, data_v)
        data_speed = mpcalc.wind_speed(data_u, data_v, )
        return np.array(data_dir), np.array(data_speed)

    def barbsMap(self):
        """
        绘制风羽图
        Args:
            add_south_china_sea: 是否添加南海
        Returns:
            [type]: [绘图对象]
        """
        try:
            xr_data_U = meb.read_griddata_from_micaps4(self.U)
            xr_data_V = meb.read_griddata_from_micaps4(self.V)
            fig = plt.figure(figsize=(16, 9), dpi=120)
            ax = plt.axes(projection=ccrs.PlateCarree())
            plt.title(self.title_name, loc='left', fontsize=20, fontdict={'family': 'simhei'})
            LAT = xr_data_U.lat.to_numpy()
            LON = xr_data_U.lon.to_numpy()
            lon, lat = np.meshgrid(LON, LAT)
            xr_data_U_array = np.squeeze(xr_data_U.data)
            xr_data_V_array = np.squeeze(xr_data_V.data)
            windDir, windSpeed = self.transformUV(xr_data_U_array, xr_data_V_array)
            windSpeed[windSpeed < min(self.levels_wind)] = np.NAN

            fileName = os.path.basename(self.U)
            draw_tools_obj = draw_tools(self.box, ax, fileName, self.outfile)
            draw_tools_obj.add_ticks()
            draw_tools_obj.add_annotate_fst()

            # 绘制风羽图
            cs = ax.pcolormesh(lon, lat, windSpeed, norm=self.norm_wind, cmap=self.cmap_wind, transform=ccrs.PlateCarree())
            plt.colorbar(cs, ax=ax, aspect=50, shrink=0.6, pad=0.08, location='bottom', label=self.colorbar_name, extend='max')
            plt.barbs(LON, LAT, xr_data_U_array, xr_data_V_array, regrid_shape=20, transform=ccrs.PlateCarree(),
                      sizes=dict(emptybarb=0), barbcolor='b', barb_increments={'half': 2, 'full': 4, 'flag': 20}, length=6)
            draw_tools_obj.add_south_china_sea()
            draw_tools_obj.add_shpfiles()
            draw_tools_obj.save_fig()
        except Exception as e:
            print('绘图错误：{}'.format(str(e)))

class draw_spatialMap(argparseConfig):
    """
    绘制气象要素空间分布图
    Args:
    Returns:
        [type]: [绘图对象]
    """
    def __init__(self, infile, outfile, box, title_name, colorbar_name):
        super().__init__()
        self.infile = infile
        self.box = box
        self.outfile = outfile
        self.title_name = title_name
        self.colorbar_name = colorbar_name

    def pcolormeshMap(self):
        """
        绘制气象要素pcolormesh图
        Args:
            add_south_china_sea: 是否添加南海
        Returns:
            [type]: [绘图对象]
        """
        try:
            import netCDF4 as nc
            xr_data = nc.Dataset(self.infile, 'r')
            LON = xr_data['Data']["geolocation"]['longitude'][()]
            LAT = xr_data['Data']["geolocation"]['latitude'][()]
            xr_data_array = xr_data['Data']['latticeInformation']['XCO2Average'][()]
            xr_data_array = np.ma.masked_where(xr_data_array < -1000, xr_data_array)
            reportTime = os.path.basename(self.infile)[9:15]

            fig = plt.figure(figsize=(16, 9), dpi=120)
            ax = plt.axes(projection=ccrs.PlateCarree())
            plt.title(self.title_name, loc='left', fontsize=22, fontdict={'family': 'simhei'})

            outpath = self.outfile.format(rp_t=datetime.strptime(reportTime, '%Y%m'))
            fileName = os.path.basename(self.infile) # 读取文件名称
            draw_tools_obj = draw_tools(self.box, ax, fileName, outpath)
            draw_tools_obj.add_ticks() # 添加并设置经纬度坐标轴

            forcast_info = '{0:%Y}年{0:%m}月平均值'.format(datetime.strptime(reportTime, '%Y%m'))
            ax.text(0.01, 0.985, forcast_info, transform=ax.transAxes, size=14, va='top',
                         fontdict={'family': 'simhei'}, ha='left', bbox=dict(facecolor='#FFFFFFCC', edgecolor='black', pad=3.0), zorder=20)

            cs = plt.pcolormesh(LON, LAT, xr_data_array, transform=ccrs.PlateCarree(), cmap=self.cmap, norm=self.norm, alpha=0.8)
            plt.colorbar(cs, ax=ax, aspect=60, shrink=0.6, pad=0.08, location='bottom', label=self.colorbar_name, extend='both')
            # draw_tools_obj.add_south_china_sea() # 添加南海小图
            draw_tools_obj.add_shpfiles() # 添加省市国界
            draw_tools_obj.save_fig() # 保存绘图结果
        except Exception as e:
            print('绘图错误：{}'.format(str(e)))

    def contourfMap(self):
        """
        绘制气象要素contourf图
        Args:
            add_south_china_sea: 是否添加南海
        Returns:
            [type]: [绘图对象]
        """
        try:
            xr_data = meb.read_griddata_from_micaps4(self.infile)

            fig = plt.figure(figsize=(16, 9), dpi=120)
            ax = plt.axes(projection=ccrs.PlateCarree())
            plt.title(self.title_name, loc='left', fontsize=20, fontdict={'family': 'simhei'})
            LAT = xr_data.lat.to_numpy()
            LON = xr_data.lon.to_numpy()
            xr_data_array = np.squeeze(xr_data.data)

            fileName = os.path.basename(self.infile) # 读取文件名称
            draw_tools_obj = draw_tools(self.box, ax, fileName, self.outfile)
            draw_tools_obj.add_ticks() # 添加并设置经纬度坐标轴
            draw_tools_obj.add_annotate_fst() # 添加实况/预报描述信息

            # # 绘制等值线填充图
            cs = plt.pcolormesh(LON, LAT, xr_data_array, transform=ccrs.PlateCarree(), cmap=self.cmap_radar, levels=self.levels_radar)
            plt.colorbar(cs, ax=ax, aspect=50, shrink=0.6, pad=0.08, location='bottom', label=self.colorbar_name, extend='max')
            draw_tools_obj.add_south_china_sea() # 添加南海小图
            draw_tools_obj.add_shpfiles() # 添加省市国界
            draw_tools_obj.save_fig() # 保存绘图结果
        except Exception as e:
            print('绘图错误：{}'.format(str(e)))

    def scatterMap(self):
        """
        绘制气象要素scatter散点图
        Args:
            add_south_china_sea: 是否添加南海
        Returns:
            [type]: [绘图对象]
        """
        try:
            xr_data = meb.read_stadata_from_micaps3(self.infile)

            plt.figure(figsize=(16, 9), dpi=120)
            ax = plt.axes(projection=ccrs.PlateCarree())
            plt.title(self.title_name, loc='left', fontsize=20, fontdict={'family': 'simhei'})
            LAT = xr_data.lat.to_numpy()
            LON = xr_data.lon.to_numpy()
            xr_data_array = xr_data.data0.to_list()

            fileName = os.path.basename(self.infile) # 读取文件名称
            draw_tools_obj = draw_tools(self.box, ax, fileName, self.outfile)
            draw_tools_obj.add_ticks() # 添加并设置经纬度坐标轴
            # draw_tools_obj.add_annotate_obs() # 添加实况/预报描述信息

            # 绘制散点图
            cs = plt.scatter(LON, LAT, marker='.', s=5, c=xr_data_array, cmap=self.cmap_scatter, norm=self.norm_scatter)
            plt.colorbar(cs, aspect=50, shrink=0.6, pad=0.08, orientation='horizontal', ticks=self.levels_scatter)
            #orientation = 'horizontal'\'vertical'

            draw_tools_obj.add_south_china_sea() # 添加南海小图
            draw_tools_obj.add_shpfiles() # 添加省市国界
            draw_tools_obj.save_fig() # 保存绘图结果
        except Exception as e:
            print('绘图错误：{}'.format(str(e)))


if __name__ == '__main__':
    infile = r"D:\data\cpvs\DataBase\MOD\CMA_GFS\radar\{rp_t:%Y}\{rp_t:%Y%m%d%H}\{rp_t:%Y%m%d%H}.{cst:03d}"
    infile_u = r"D:\data\cpvs\DataBase\MOD\CMA_GFS\u10\{rp_t:%Y}\{rp_t:%Y%m%d%H}\{rp_t:%Y%m%d%H}.{cst:03d}"
    infile_v = r"D:\data\cpvs\DataBase\MOD\CMA_GFS\v10\{rp_t:%Y}\{rp_t:%Y%m%d%H}\{rp_t:%Y%m%d%H}.{cst:03d}"
    outfile = r"D:\data\cpvs\DataBase\MOD\CMA_MESO\co2\draw_china\{rp_t:%Y%m}.average.png"
    box = [70, 140, 10, 60]
    stime = datetime.strptime(sys.argv[1].ljust(10, '0'), '%Y%m%d%H')
    etime = datetime.strptime(sys.argv[2].ljust(10, '0'), '%Y%m%d%H')
    cst = int(sys.argv[3])
    begin_t = stime
    import glob
    filelist = glob.glob(r'D:\data\cpvs\DataBase\MOD\CMA_MESO\co2\CO2\*.h5')
    for file in filelist:
        radar_map = draw_spatialMap(file,  outfile, box, '二氧化碳', 'ppmv')
        radar_map.pcolormeshMap()