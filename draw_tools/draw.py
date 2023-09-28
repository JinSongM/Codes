import meteva.base as meb
from scipy.interpolate import RectBivariateSpline
from scipy.interpolate import CubicSpline
import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import pandas as pd
import cv2
import xarray as xr
from PIL import Image 
import os
import glob


def draw():
    file = r"C:\Users\wiztek\Documents\WeChat Files\wxid_43vosvk7mvre22\FileStorage\File\2023-09\gf.txt"
    mean_data = meb.read_griddata_from_micaps4(file)
    lats = mean_data.lat.data
    lons = mean_data.lon.data
    longitudes, latitudes = np.meshgrid(lons, lats)
    slon = 70
    slat = 0
    elon = 140
    elat = 60
    m = Basemap(llcrnrlon=slon, llcrnrlat=slat, urcrnrlon=elon, urcrnrlat=elat)
    longitude, latitude = m(longitudes, latitudes)
    levels = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    cdict = ['#66FF99', '#9933FF', '#0099CC', '#9999FF', '#00CC6C', '#0066FF', '#DDF400', '#66FFFF', '#FFB100',
             '#FF7E00', '#FF3000', '#E5002C', '#CC00C0', '#000000']
    cmap = colors.ListedColormap(cdict)
    norm = colors.BoundaryNorm(levels, (cmap.N) + 1)
    cb_ticks = levels
    cb_label = levels
    mean_data.data[mean_data.data < -50] = np.nan
    mean_data.data[mean_data.data > 50] = np.nan
    cs = m.contourf(longitude, latitude, mean_data.data[0][0][0][0], levels=levels, colors=cdict,
                    extend='both')
    cbar = m.colorbar(cs, location='bottom', size='5%', pad='10%', ticks=cb_ticks, label=cb_label, extend='both')
    cbar.set_label("gf")
    m.drawparallels(np.arange(slat, elat, 10), labels=[1, 0, 0, 0], fontsize=10, linewidth=0)
    m.drawmeridians(np.arange(slon, elon, 10), labels=[0, 0, 0, 1], fontsize=10, linewidth=0)

    m.readshapefile(r'D:/data/datasource/Geoserver/2023最新行政边界/2023年省级/2023年初省级矢量', '2023年初省级矢量', drawbounds=True)
    m.drawstates(color='0.2', linewidth=0.5)
    m.drawcountries(color='0.2', linewidth=0.5)
    # plt.scatter(116.4694, 39.8061, s=20, color='red', marker=(5, 2))
    plt.title("阵风系数 5km")
    # plt.text(116.4694, 39.8061, "北京站", fontsize=8)
    product = "1.png"
    folder = os.path.dirname(product)
    # if not os.path.exists(folder):
    #     os.makedirs(folder)
   # plt.savefig("./1.png", dpi=120, bbox_inches='tight')
    plt.savefig(product, dpi=180, bbox_inches='tight')
    plt.close()



if __name__ == '__main__':
    draw()