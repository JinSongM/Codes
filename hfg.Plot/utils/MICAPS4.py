import re
import numpy as np
from utils import LatLonData as lld
import datetime
import struct
import os
from utils.logging import logger
import math

def loss_data(file_path):
    if os.path.exists(file_path):
        name = os.path.split(file_path)[1][0:-4] + '.txt'
        outpath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'loss_data', 'error', name)
        if not os.path.exists(os.path.dirname(outpath)):
            os.makedirs(os.path.dirname(outpath))
        with open(outpath, 'a') as f:
            f.write(file_path)
            f.write('\r\n')
            f.close()

def open_m4_org(file: str, encoding='utf8'):
    """
    打开 m4文件
    :param encoding:
    :param file:
    :return:
    """
    if not os.path.exists(file):
        return None
    # 打开文件，进行解析
    with open(file, "r", encoding=encoding) as fh:
        lines = fh.readlines()
    p = re.compile("\\s+")
    array = []
    for line in lines:
        array.extend(p.split(line.replace("\n", "").strip()))

    delt_lon = float(array[9])
    delt_lat = float(array[10])
    start_lon = float(array[11])
    end_lon = float(array[12])
    start_lat = float(array[13])
    end_lat = float(array[14])
    lon_count = int(array[15])
    lat_count = int(array[16])

    try:
        lat_lon_data = lld.LatLonData(start_lon, end_lon, start_lat, end_lat, delt_lon, delt_lat, lon_count, lat_count)
        _array = np.reshape(np.array(array[22:], dtype=float), (lat_count, lon_count))
        lat_lon_data.data = _array
        return lat_lon_data
    except:
        loss_data(file)
        return None

def open_m4(file: str, encoding='utf8'):
    """
    打开 m4文件
    :param encoding:
    :param file:
    :return:
    """
    if not os.path.exists(file):
        return None
    # 打开文件，进行解析
    with open(file, "r", encoding=encoding) as fh:
        lines = fh.readlines()
    p = re.compile("\\s+")
    array = []
    for line in lines:
        array.extend(p.split(line.replace("\n", "").strip()))

    delt_lon = float(array[9])
    delt_lat = float(array[10])
    start_lon = float(array[11])
    end_lon = float(array[12])
    start_lat = float(array[13])
    end_lat = float(array[14])
    lon_count = int(array[15])
    lat_count = int(array[16])

    try:
        lat_lon_data = lld.LatLonData(start_lon, end_lon, start_lat, end_lat, delt_lon, delt_lat, lon_count, lat_count)
        _array = np.reshape(np.array(array[22:], dtype=float), (lat_count, lon_count))
        _array[_array > 9000] = np.nan
        lat_lon_data.data = _array
        return lat_lon_data
    except:
        loss_data(file)
        return None

def open_m11(file: str, encoding='utf8'):
    """
    打开 m4文件
    :param encoding:
    :param file:
    :return:
    """

    if not os.path.exists(file):
        return None, None, None, None

    # 打开文件，进行解析
    with open(file, "r", encoding=encoding) as fh:
        lines = fh.readlines()

    p = re.compile("\\s+")

    head = p.split(lines[1].strip())
    start_lon = float(head[8])
    end_lon = float(head[9])
    start_lat = float(head[10])
    end_lat = float(head[11])
    lon_count = int(head[12])
    lat_count = int(head[13])

    array = []

    for line in lines[2:]:
        array.extend(p.split(line.replace("\n", "").strip()))

    lats = np.linspace(start_lat, end_lat, lat_count)
    lons = np.linspace(start_lon, end_lon, lon_count)
    lons, lats = np.meshgrid(lons, lats)
    array1 = np.reshape(np.array(array[0:int(len(array) / 2)], dtype=float), (lat_count, lon_count))
    array2 = np.reshape(np.array(array[int(len(array) / 2):], dtype=float), (lat_count, lon_count))

    return lats, lons, array1, array2


def save_m4(lat_lon_data, file, date=datetime.datetime.now(), hour=0, level="9999", desc="", contour=" 1 10 50 1 0"):
    """
    保存为m4格式文件
    :param contour:
    :param lat_lon_data:
    :param file:
    :param date:
    :param hour:
    :param level:
    :param desc:
    :return:
    """
    str_array = []
    str_time = datetime.datetime.strftime(date, '%Y%m%d%H')
    str_time2 = datetime.datetime.strftime(date, '%Y %m %d %H')
    str_array.append("diamond 4 %s\n" % (str_time + "_" + re.sub(r'\\s+', "_", desc)))

    str_array.append("%s %d %s %.3f %.3f %.3f %.3f %.3f %.3f %d %d %s\n" % (
        str_time2, int(hour), level, lat_lon_data.delt_lon,
        lat_lon_data.delt_lat, lat_lon_data.start_lon, lat_lon_data.end_lon, lat_lon_data.start_lat,
        lat_lon_data.end_lat,
        lat_lon_data.lon_count, lat_lon_data.lat_count, contour))

    for array in lat_lon_data.data:
        str_line = ""
        for arr in array:
            str_line += "%.2f%s" % (arr, " ")

        str_array.append((str_line + "\n").strip(" "))
    if not os.path.exists(os.path.dirname(file)):
        os.makedirs(os.path.dirname(file))
    with open(file, 'w+', encoding="utf8") as fl:
        fl.writelines(str_array)

    logger.info('save over for m4：{}'.format(file))


def open_m4_grid(file, start_lon, end_lon, start_lat, end_lat, delt_lon, delt_lat, lon_count, lat_count):
    """
        打开二进制文件
    :param file:
    :param start_lon:
    :param end_lon:
    :param start_lat:
    :param end_lat:
    :param delt_lon:
    :param delt_lat:
    :param lon_count:
    :param lat_count:
    :return: LatLonData
    """
    if not os.path.exists(file):
        return None
    lat_lon_data = lld.LatLonData(start_lon, end_lon, start_lat, end_lat, delt_lon, delt_lat, lon_count, lat_count)
    with open(file, 'rb') as f:
        c = f.read()
        data = struct.unpack(('%df' % (len(c) / 4)), c)
    z = np.array(data).reshape(lat_count, lon_count)  # 将一维数组分成二维数组
    lat_lon_data.data = z

    return lat_lon_data


def save_m4_grid(lat_lon_data, file):
    """
    保存成二进制格式
    :param lat_lon_data:
    :param file:
    :return:
    """
    if not os.path.exists(os.path.dirname(file)):
        os.makedirs(os.path.dirname(file))
    array = np.array(lat_lon_data.data).reshape(-1, )
    array_byte = struct.pack("%df" % (len(array)), *array)
    with open(file, 'wb+') as fl:
        fl.write(array_byte)

    logger.info('save over for grid')


def save_uv_to_m11(file_path, data, d_date, d_hour, start_lat, end_lat, start_lon, end_lon, dx, dy, nx, ny, level,
                   desc):
    str_time = datetime.datetime.strftime(d_date, '%Y%m%d%H')
    str_time2 = datetime.datetime.strftime(d_date, '%Y %m %d %H')
    str_array = []
    str_array.append("diamond 4 %s\n" % (str_time + "_" + re.sub(r'\\s+', "_", desc)))

    str_array.append("%s %d %s %.3f %.3f %.3f %.3f %.3f %.3f %d %d %s\n" % (
        str_time2, int(d_hour), level, dx, dy, start_lon, end_lon, start_lat, end_lat, nx, ny, "0 10 -50 60 1 "))

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

    logger.info('save over for m11：{}'.format(file_path))

def open_m11_uv(file: str, encoding='utf8'):
    """
    打开 m4文件
    :param encoding:
    :param file:
    :return:
    """

    if not os.path.exists(file):
        return None, None, None, None

    # 打开文件，进行解析
    with open(file, "r", encoding=encoding) as fh:
        lines = fh.readlines()

    p = re.compile("\\s+")

    head = p.split(lines[1].strip())
    start_lon = float(head[8])
    end_lon = float(head[9])
    start_lat = float(head[10])
    end_lat = float(head[11])
    lon_count = int(head[12])
    lat_count = int(head[13])

    array = []

    for line in lines[2:]:
        array.extend(p.split(line.replace("\n", "").strip()))

    lats = np.linspace(start_lat, end_lat, lat_count)
    lons = np.linspace(start_lon, end_lon, lon_count)
    # lons, lats = np.meshgrid(lons, lats)
    array1 = np.reshape(np.array(array[0:int(len(array) / 2)], dtype=float), (lat_count, lon_count))
    array2 = np.reshape(np.array(array[int(len(array) / 2):], dtype=float), (lat_count, lon_count))

    return lats, lons, array1, array2

if __name__ == '__main__':
    import xarray as xr

    data = open_m4_grid("../time_contour/2022010420.000", 60, 150, -10, 60, 0.125, 0.125, 721, 561)
    lat = np.linspace(-10, 60, 561)
    lon = np.linspace(60, 150, 721)
    new_lat = np.linspace(-10, 60, 281)
    new_lon = np.linspace(60, 150, 361)
    xr_data = xr.DataArray(data.data, coords=[lat, lon], dims=["lat", "lon"])
    f_data = xr_data.interp(lat=new_lat, lon=new_lon)
    array = np.array(f_data.values).reshape(-1, )
    array_byte = struct.pack("%df" % (len(array)), *array)
    with open("../ncl/sp.dat", 'wb+') as fl:
        fl.write(array_byte)
