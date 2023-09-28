# -- coding: utf-8 --
# @Time : 2023/5/29 13:39
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : Example.py
# @Software: PyCharm
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeat
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.path as mpath
import matplotlib.patches as mpatches
import shapely.geometry as sgeom
plt.rcParams['font.sans-serif']=['SimHei']
###虚构中尺度路径数据###################################################
def sample_data():
    lons=[108.5,108.8,109,109.5,109.8,109.9]
    lats=[31.5,31.5,31.5,31.5,31,31]
    return lons,lats
def main():
    extent=[107.5,111.5,28.5,32]#定义绘图范围
    shp_path = r'E:\shp\行政边界.shp'
    proj = ccrs.PlateCarree() #创建坐标系
    lons,lats=sample_data()
    fig=plt.figure(figsize=(5,5),dpi=600)
    ax = fig.add_axes([0, 0, 1, 1], projection=proj,
                      frameon=False)
    ax.set_extent(extent, proj)
    cities_shp=r'E:\shp\行政边界.shp'
    ax.set_title('一次中尺度对流影响的县市',fontsize=20)
    track = sgeom.LineString(zip(lons, lats))#将台风线条转化为地理信息
    track_buffer = track.buffer(1)#缓冲1度
    track_buffer2=track.buffer(2)#缓冲2度
    def colorize_state(geometry):
        facecolor = (0.9375, 0.9375, 0.859375)
        if geometry.intersects(track):
            facecolor = 'red'
        elif geometry.intersects(track_buffer):
            facecolor = '#FF7E00'
        elif geometry.intersects(track_buffer2):
            facecolor='green'
        return {'facecolor': facecolor, 'edgecolor': 'black'}
    ax.add_geometries(shpreader.Reader(cities_shp).geometries(),ccrs.PlateCarree(),lw=0.5,styler=colorize_state)
    ax.add_geometries([track_buffer2], ccrs.PlateCarree(),
                      facecolor='cyan', alpha=0.2)
    ax.add_geometries([track_buffer], ccrs.PlateCarree(),
                      facecolor='#C8A2C8', alpha=0.5)
    ax.add_geometries([track], ccrs.PlateCarree(),
                      facecolor='none', edgecolor='k')
    ax.scatter(lons,lats, s=150, marker='.',
            edgecolors="red", facecolors='none', linewidth=2.3,zorder=3)
    ############添加其他信息##############
    ax.add_feature(cfeat.RIVERS.with_scale('10m'))
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=0.7, color='k', alpha=0.5, linestyle='--')
    gl.xlabels_top = False  # 关闭顶端的经纬度标签
    gl.ylabels_right = False  # 关闭右侧的经纬度标签
    gl.xformatter = LONGITUDE_FORMATTER  # x轴设为经度的格式
    gl.yformatter = LATITUDE_FORMATTER  # y轴设为纬度的格式
    gl.xlocator = mticker.FixedLocator(np.arange(extent[0], extent[1]+2, 1))
    gl.ylocator = mticker.FixedLocator(np.arange(extent[2], extent[3]+2, 1))
    nameandstation={"恩施":[109.5,30.2],"利川":[109,30.3],"巴东":[110.34,31.04],"建始":[109.72,30.6],"宣恩":[109.49,29.987],"来凤":[109.407,29.493],"咸丰":[109.14,29.665],"鹤峰":[110.034,29.89]}
    for key,value in nameandstation.items():
        ax.scatter(value[0] , value[1] , marker='.' , s=65 , color = "k" , zorder = 3)
        ax.text(value[0]-0.09 , value[1]+0.05 , key , fontsize = 9 , color = "k")
    ###########################################
    direct_hit = mpatches.Rectangle((0, 0), 1, 1, facecolor="red")
    within_1_deg = mpatches.Rectangle((0, 0), 1, 1, facecolor="#FF7E00")
    within_2_deg = mpatches.Rectangle((0, 0), 1, 1, facecolor="green")
    labels = ['强对流过境',
              '风雨影响','外围缓和区']
    ax.legend([direct_hit, within_1_deg,within_2_deg], labels,
              loc='lower left', bbox_to_anchor=(0.7, 0.04), fancybox=True)
    fig.savefig('一次中尺度对流影响的县市',bbox_inches='tight')
    plt.show()
if __name__ == '__main__':
    main()