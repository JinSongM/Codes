import os, re

import cv2
import xarray
import struct
import netCDF4
import numpy as np
import pandas as pd
import meteva.base as meb
import cartopy.crs as ccrs
from osgeo import gdal
from datetime import datetime
import matplotlib.pyplot as plt
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

__all__ = ["save_array", "load_array", "get_parent_dir", "mkdir", "cartopy_subplot", "read_m3_file",
           "read_tiff", "write_tiff", "creat_M3_grd", 'd_to_jd', 'jd_to_time', "MaskTIF", "openMicaps3FileAsDataframe",
           "low_pass_filter", "bw_filter", "notch_filter", "creat_M4_grd", 'save_uv_to_m11', 'save_nc']

#年月日转年积日
def d_to_jd(time):
    fmt = '%Y.%m.%d'
    dt = datetime.strptime(time, fmt)
    tt = dt.timetuple()
    return tt.tm_year * 1000 + tt.tm_yday

#年积日转年月日
def jd_to_time(time):
    dt = datetime.strptime(time, '%Y%j').date()
    fmt = '%Y.%m.%d'
    return dt.strftime(fmt)

def save_nc(data, lons, lats, filename):
    import netCDF4 as nc
    if data is None:
        raise ValueError("no data")
    da = nc.Dataset(filename, "w")
    da.createDimension("lon", len(lons))
    da.createDimension("lat", len(lats))
    da.createVariable("lon", "f", ("lon",), zlib=True)
    da.createVariable("lat", "f", ("lat",), zlib=True)
    da.variables["lon"][:] = lons
    da.variables["lat"][:] = lats
    da.createVariable("time", "f", ("lat", "lon"), zlib=True)
    da.variables["time"][:] = data
    da.close()

def get_parent_dir(path=None, offset=-1):
    """
    获取多层父级目录
    :param path: 文件路径
    :param offset: 父级层数
    :return:
    """
    result = path if path else __file__
    for i in range(abs(offset)):
        result = os.path.dirname(result)
    return result

def creat_M3_grd(ID_LIST, Lon_list, Lat_list, Data_list):
    """
    构建m3标准格式
    :param ID_LIST: 站号列表
    :param Lon_list: 经度列表
    :param Lat_list: 维度列表
    :param Data_list: 数据列表
    :return:
    """
    data = {
        '站号': ID_LIST,
        "经度": Lon_list,
        "纬度": Lat_list,
        "数据": Data_list,
    }
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

def save_uv_to_m11(file_path, data, reportTime, cst, desc, startlon, endlon, startlat, endlat,
                   lonInterval, latInterval, lonGridCount, latGridCount, level=999):
    """
    生成m11文件
    :param file_path: micapes11文件输出地址
    :param data: uv合并的三维array
    :param reportTime: 数据起报时间
    :param cst: 数据预报时效
    :param desc: 数据head描述信息
    :param startlon: 起始经度
    :param endlon: 截止经度
    :param startlat: 起始经纬度
    :param endlat: 截止纬度
    :param lonInterval: 经度分辨率
    :param latInterval: 纬度分辨率
    :param lonGridCount: 经度网格数
    :param latGridCount: 纬度网格数
    :param level: 级别

    :return:
    """

    str_time = datetime.strftime(reportTime, '%Y%m%d%H')
    str_time2 = datetime.strftime(reportTime, '%Y %m %d %H')
    str_array = []
    str_array.append("diamond 11 %s\n" % (str_time + "_" + str(cst) + "_" + desc))

    str_array.append("%s %d %s %.3f %.3f %.3f %.3f %.3f %.3f %d %d %s\n" % (
        str_time2, int(cst), level, lonInterval, latInterval, startlon,
        endlon, startlat, endlat, lonGridCount, latGridCount, "0 10 -50 60 1 "))

    u_str = [" ".join(u) for u in np.array(data[0], dtype=str)]
    u_str = ["{}\n".format(one) for one in u_str]

    v_str = [" ".join(v) for v in np.array(data[1], dtype=str)]
    v_str = ["{}\n".format(one) for one in v_str]

    str_array.extend(u_str)
    str_array.extend(v_str)

    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    with open(file_path, 'w+', encoding="utf8") as fl:
        fl.writelines(str_array)
    print('成功输出micapes11')


def mkdir(fil_path):
    """
    创建目录
    :param file:
    :return:
    """
    if not os.path.exists(os.path.dirname(fil_path)):
        os.makedirs(os.path.dirname(fil_path))

def openMicaps3FileAsDataframe(file, encoding="utf8"):
    p_s = re.compile("\\s+")
    with open(file, "r", encoding=encoding) as content:
        lines = content.readlines()

    data = [p_s.split(line.strip()) for line in lines if len(p_s.split(line.strip())) == 5]
    data = np.array(data, dtype=object)
    df_data = pd.DataFrame({
        "STATION_ID": np.array(data[:, 0]),
        "LON": np.array(data[:, 1], dtype=float),
        "LAT": np.array(data[:, 2], dtype=float),
        "ALTI": np.array(data[:, 3], dtype=float),
        "VALUE": np.array(data[:, 4], dtype=float),
    })

    return df_data

def read_m3_file(filedata):
    '''
    Infile：M3文件
    Outfile：三维数组（经度、纬度和值）
    '''
    lat_lon_data = openMicaps3FileAsDataframe(filedata)
    value = lat_lon_data['VALUE']
    value_file = value
    latitudes_file = list(lat_lon_data['LAT'])
    longitudes_file = list(lat_lon_data['LON'])
    value_file = [longitudes_file, latitudes_file, value_file]
    return value_file

def save_array(array, file):
    """
    将二维浮点数组保存到二进制文件上
    :param array:
    :param file:
    :return:
    """

    dir_name = os.path.split(file)[0]
    data = struct.pack(("%df" % len(array)), *array)

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    if os.path.exists(file):
        os.remove(file)

    f = open(file, "wb+")
    f.write(data)
    f.close()


def load_array(file, big=False):
    """
    从二进制文件中加载二维数组并返回
    :param big:
    :param file:
    :return:
    """
    f = open(file, "rb+")
    c = f.read()
    if big:
        data = struct.unpack((">%df" % (len(c) / 4)), c)
    else:
        data = struct.unpack(("%df" % (len(c) / 4)), c)
    return list(data)

def cartopy_subplot(nrows, ncols, box, xystep, china_shp, png_path):
    '''
    地理子图
    :param nrows: 子图行数
    :param ncols: 子图列数
    :return:
    '''

    '''
    plt.rcParams['axes.unicode_minus'] = False 字符显示
    plt.rcParams['font.sans-serif'] = 'SimHei' 设置中文字体
    plt.rcParams['font.size'] = 18 设置字体大小
    plt.rcParams['font.family'] = 'serif' 设置英文字体
    plt.rcParams['font.serif'] = ['Times New Roman'] 设置英文字体
    线条样式：lines
    plt.rcParams['lines.linestyle'] = '-.' 线条样式
    plt.rcParams['lines.linewidth'] = 3 线条宽度
    plt.rcParams['lines.color'] = 'blue' 线条颜色
    plt.rcParams['lines.marker'] = None 默认标记
    plt.rcParams['lines.markersize'] = 6 标记大小
    plt.rcParams['lines.markeredgewidth'] = 0.5 标记附近的线宽
    横、纵轴：xtick、ytick
    plt.rcParams['xtick.labelsize'] 横轴字体大小
    plt.rcParams['ytick.labelsize'] 纵轴字体大小
    plt.rcParams['xtick.major.size'] x轴最大刻度
    plt.rcParams['ytick.major.size'] y轴最大刻度
    figure中的子图：axes
    plt.rcParams['axes.titlesize'] 子图的标题大小
    plt.rcParams['axes.labelsize'] 子图的标签大小
    图像、图片：figure、savefig
    plt.rcParams['figure.dpi'] 图像分辨率
    plt.rcParams['figure.figsize'] 图像显示大小
    plt.rcParams['savefig.dpi'] 图片像素
    matplotlib: https://geek-docs.com/matplotlib/matplotlib-axes/matplotlib-axes-axes-set_adjustable-in-python.html
    '''

    fig, axes = plt.subplots(figsize=(16, 9), dpi=120, nrows=nrows, ncols=ncols,
                             subplot_kw=dict(projection=ccrs.PlateCarree(), aspect='auto'))

    for i, ax in zip(np.arange(0, nrows * ncols), axes.flat):
        ax.set_xticks(np.arange(int(box[0]), box[1] + xystep, xystep))
        ax.set_yticks(np.arange(int(box[2]), box[3] + xystep, xystep))
        ax.set_extent(box, crs=ccrs.PlateCarree())
        plt.tick_params(axis="both", which="major", width=1, length=10, pad=10)

        # 标注坐标轴
        china_reader = Reader(china_shp).geometries()
        china = cfeature.ShapelyFeature(china_reader, ccrs.PlateCarree(), edgecolor='grey', facecolor='none')
        ax.add_feature(china, linewidth=0.6)  # 添加中国边界
        # ax.add_feature(cfeature.STATES.with_scale('50m'), edgecolor='grey', alpha=0.8)
        # ax.add_feature(cfeature.COASTLINE.with_scale('50m'), edgecolor='grey', alpha=0.8)

        # zero_direction_label用来设置经度的0度加不加E和W
        lon_formatter = LongitudeFormatter(zero_direction_label=False)
        lat_formatter = LatitudeFormatter()
        ax.xaxis.set_major_formatter(lon_formatter)
        ax.yaxis.set_major_formatter(lat_formatter)

        # ax.grid(True, linestyle="--", alpha=0.5, axis='x')
        # ax.yticks(fontproperties='SimHei', size=16)
        # ax.xticks(xlabels, X_labels, fontproperties='SimHei', size=16)
        # ax.xaxis.set_major_locator(MultipleLocator(2))
        # ax.yaxis.set_major_locator(MultipleLocator(20))
        # fontdict = {'fontsize': 10, 'family': ['serif', 'SimSun'], 'weight': 'bold'}
        # ax.set_ylabel('label', fontdict=fontdict)
        # ax.set_xlabel('label', fontdict=fontdict)
        # ax.set_title('title', fontdict=fontdict)

        # ax.plot(x, y, color='m', linewidth=2, transform=ccrs.PlateCarree(), marker='o', markersize='10',
        #         markerfacecolor='none', label='label')

        # ax.text(x, y, forcast_info, transform=ccrs.PlateCarree(), fontfamily='SimHei', fontsize=14, va='top', rotation=20,
        #             ha='left', bbox=dict(facecolor='#FFFFFFCC', edgecolor='black', pad=3.0), zorder=20)
        
        # l, b, w, h = ax.get_position().bounds
        # cax = fig.add_axes([l, b - h * 0.06 - 0.05, w, h * 0.02])
        # contourf_cb = plt.contourf(lon, lat, data_array, cmap='Reds', levels=ticks)
        # ax.colorbar(contourf_cb, cax=cax, aspect=50, shrink=0.6, pad=0.08, orientation='horizontal', extend='both', extendfrac='auto')

        # scatter_cb = plt.scatter(x, y, marker='.', s=5, c=value, cmap=cmp, norm=norm)
        # ax.colorbar(scatter_cb, cax=cax, aspect=50, shrink=0.5, pad=0.08, orientation='horizontal', extend='both', ticks=ticks)


    plt.title('title', loc='center', fontproperties='SimHei', fontsize=22)
    fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=None)
    plt.legend(fontsize=18, bbox_to_anchor=(0.5, -0.05), loc=None, ncol=None, frameon=False)
    # plt.show()
    plt.savefig(png_path, dpi=180, bbox_inches="tight")

def read_tiff(path):
    """
    读取 TIFF 文件
    :param path: str，unicode，dataset
    :return:
    """
    # 参数类型检查
    if isinstance(path, gdal.Dataset):
        dataset = path
    else:
        dataset = gdal.Open(path)

    if dataset:
        im_width = dataset.RasterXSize  # 栅格矩阵的列数
        im_height = dataset.RasterYSize  # 栅格矩阵的行数
        im_bands = dataset.RasterCount  # 波段数
        im_proj = dataset.GetProjection()  # 获取投影信息
        im_geotrans = dataset.GetGeoTransform()  # 获取仿射矩阵信息
        im_data = dataset.ReadAsArray(0, 0, im_width, im_height)  # 获取数据
        return im_data, im_width, im_height, im_bands, im_geotrans, im_proj
    else:
        print('error in read tiff')


def write_tiff(im_data, im_geotrans, im_proj, out_path=None, no_data_value=None, return_mode='TIFF'):
    """
    写dataset（需要一个更好的名字）
    :param im_data: 输入的矩阵
    :param im_geotrans: 仿射矩阵
    :param im_proj: 坐标系
    :param out_path: 输出路径，str，None
    :param no_data_value: 无效值 ；num_list ，num
    :param return_mode: TIFF : 保存为本地文件， MEMORY：保存为缓存
    :return: 当保存为缓存的时候，输出为 dataset
    """

    # FIXME  no_data_value 要注意类型

    # 保存类型选择
    if 'int8' in im_data.dtype.name or 'bool' in im_data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in im_data.dtype.name:
        datatype = gdal.GDT_Int16
    else:
        datatype = gdal.GDT_Float32
    # 矩阵波段识别
    if len(im_data.shape) == 3:
        im_bands, im_height, im_width = im_data.shape
    elif len(im_data.shape) == 2:
        # 统一处理为三维矩阵
        im_data = np.array([im_data], dtype=im_data.dtype)
        im_bands, im_height, im_width = im_data.shape
    else:
        im_bands, (im_height, im_width) = 1, im_data.shape
    # 根据存储类型的不同，获取不同的驱动
    if out_path:
        dataset = gdal.GetDriverByName('GTiff').Create(out_path, im_width, im_height, im_bands, datatype)
    else:
        dataset = gdal.GetDriverByName('MEM').Create('', im_width, im_height, im_bands, datatype)
    # 写入数据
    if dataset is not None:
        dataset.SetGeoTransform(im_geotrans)
        dataset.SetProjection(im_proj)
    # 写入矩阵
    for i in range(im_bands):
        dataset.GetRasterBand(i + 1).WriteArray(im_data[i])
        # 写入无效值
        if no_data_value is not None:
            # 当每个图层有一个无效值的时候
            if isinstance(no_data_value, list) or isinstance(no_data_value, tuple):
                if no_data_value[i] is not None:
                    dataset.GetRasterBand(i + 1).SetNoDataValue(no_data_value[i])
            else:
                dataset.GetRasterBand(i + 1).SetNoDataValue(no_data_value)
    # 根据返回类型的不同，返回不同的值
    if return_mode.upper() == 'MEMORY':
        return dataset
    elif return_mode.upper == 'TIFF':
        del dataset

 #裁剪
def MaskTIF(Infile, save_path, shapefile_path):
    """
    Infile:输入栅格文件
    save_path:输出路径
    """
    gdal.Warp(save_path,  # 裁剪图像保存完整路径（包括文件名）
              Infile,  # 待裁剪的影像
              format='GTiff',  # 保存图像的格式
              cutlineDSName=shapefile_path,  # 矢量文件的完整路径
              cropToCutline=True,  # 保证裁剪后影像大小跟矢量文件的图框大小一致（设置为False时，结果图像大小会跟待裁剪影像大小一样，则会出现大量的空值区域）
              dstNodata = np.nan)


def low_pass_filter(img, radius=80):
    """
    低通滤波器
    :param img:
    :param radius:
    :return:
    """
    rows, cols = img.shape
    center = int(rows/2), int(cols/2)

    mask = np.zeros((rows, cols, 2), np.uint8)
    x, y = np.ogrid[:rows, :cols]
    mask_area = (x-center[0])**2+(y-center[1])**2 <= radius*radius
    mask[mask_area] = 1
    return mask

def gaus_filter(img, radius=80):
    """
    高斯滤波器
    :param img:
    :param radius:
    :return:
    """
    rows, cols = img.shape
    center = int(rows/2), int(cols/2)

    mask = np.zeros((rows, cols, 2), np.float32)
    for i in range(rows):
        for j in range(cols):
            dist = (i-center[0])**2+(j-center[1])**2
            mask[i, j] = np.exp(-0.5*dist/(radius**2))
    return mask

def bw_filter(img, radius=80, n=2):
    """
    巴特沃斯滤波器
    :param img:
    :param radius:
    :param n:
    :return:
    """
    rows, cols = img.shape
    center = int(rows / 2), int(cols / 2)

    mask = np.zeros((rows, cols, 2), np.float32)
    for i in range(rows):
        for j in range(cols):
            dist = (i - center[0]) ** 2 + (j - center[1]) ** 2
            mask[i, j] = 1/(1+(dist/radius)**(n/2))
    return mask

def notch_filter(img, h, w):
    """
    陷波滤波器
    :param img:
    :param h:
    :param w:
    :return:
    """
    rows, cols = img.shape
    center = int(rows / 2), int(cols / 2)

    mask = np.zeros((rows, cols, 2), np.float32)
    for u in range(rows):
        for v in range(cols):
            mask[u,v]=0
    for u in range(rows):
        for v in range(cols):
            if abs(u - center[0]) < h and abs(v - center[1]) < w:
                mask[u, v] = 1

    return mask

def creat_M11_grd(lon, lat, data_array):
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
                            dtime_list=[1], member_list=["u", "v"])
    return grd

if __name__ == "__main__":
    u_file = r'D:\data\cpvs\DataBase\MOD\CMA_GFS\u10\2023\2023012808\2023012808.003'
    v_file = r'D:\data\cpvs\DataBase\MOD\CMA_GFS\v10\2023\2023012808\2023012808.003'
    U = meb.read_griddata_from_micaps4(u_file).data
    V = meb.read_griddata_from_micaps4(v_file).data
    uv_array = [np.squeeze(U), np.squeeze(V)]
    save_uv_to_m11('./a.000', uv_array, datetime.now(), 24, 'wind', 70, 140, 0, 60, 0.25, 0.25, 281, 241)
