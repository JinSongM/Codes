import re
import numpy as np
from utils import LatLonData as lld
import datetime
import struct
import os
from utils.logging import logger


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

    head = p.split(lines[1].strip())

    delt_lon = float(head[6])
    delt_lat = float(head[7])
    start_lon = float(head[8])
    end_lon = float(head[9])
    start_lat = float(head[10])
    end_lat = float(head[11])
    lon_count = int(head[12])
    lat_count = int(head[13])

    lat_lon_data = lld.LatLonData(start_lon, end_lon, start_lat, end_lat, delt_lon, delt_lat, lon_count, lat_count)

    array = []

    for line in lines[2:]:
        array.extend(p.split(line.replace("\n", "").strip()))

    array = np.reshape(np.array(array, dtype=float), (lat_count, lon_count))
    lat_lon_data.data = array
    return lat_lon_data


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

    logger.info('save over for m4')


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
    z = np.round(np.array(data).reshape(lat_count, lon_count), 2)  # 将一维数组分成二维数组
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


if __name__ == '__main__':
    fil = "../data/NWFD/2021010108.024"
    open_m4(fil, "gbk")
