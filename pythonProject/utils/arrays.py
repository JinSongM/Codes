# -- coding: utf-8 --
# @Time : 2023/5/11 9:57
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : arrays.py
# @Software: PyCharm
"""
数组到二进制文件的压码、解码
"""
import os
import struct
import netCDF4
import numpy
import xarray

__all__ = ["save_array", "load_array",
           "save_to_nc_time_ens_y_x", "load_nc_time_ens_lat_lon", "interpolation_linear_g_to_s"]


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
    # c = zlib.decompress(c)
    if big:
        data = struct.unpack((">%df" % (len(c) / 4)), c)
    else:
        data = struct.unpack(("%df" % (len(c) / 4)), c)
    return list(data)


# 将一个厂保存到nc格式的文件
def save_to_nc_time_ens_y_x(
        data: numpy.array,
        filename: str,
        key: str,
        time: str,
        times: numpy.array,
        ens: numpy.array,
        lats: numpy.array,
        lons: numpy.array
):
    print("save: {}".format(filename))

    da = netCDF4.Dataset(filename, "w", format="NETCDF4")

    da.createDimension("time", len(times))  # 创建坐标点
    da.createDimension("ens", len(ens))  # 创建坐标点
    da.createDimension("lat", len(lats))  # 创建坐标点
    da.createDimension("lon", len(lons))  # 创建坐标点

    da.createVariable("time", int, ("time",))
    da.createVariable("ens", int, ("ens",))
    da.createVariable("lat", float, ("lat",))  # 添加coordinates 'f'为数据类型，不可或缺
    da.createVariable("lon", float, ("lon",))  # 添加coordinates 'f'为数据类型，不可或缺

    da.variables["time"].setncattr(
        "units", "hours since %s" % ("%s-%s-%s %s:00:00" % (time[0:4], time[4:6], time[6:8], time[8:10])))

    da.variables["lat"].setncattr("units", "degrees_north")
    da.variables["lon"].setncattr("units", "degrees_east")

    da.variables["time"][:] = times
    da.variables["ens"][:] = ens
    da.variables["lat"][:] = lats
    da.variables["lon"][:] = lons

    da.createVariable(key, "f4", ("time", "ens", "lat", "lon"), zlib=True)
    da.variables[key][:] = data
    da.close()


def load_nc_time_ens_lat_lon(filename: str, key: str):
    with netCDF4.Dataset(filename=filename) as nc:
        var = nc.variables[key]
        result = xarray.DataArray(
            var[:, :, :, :],
            [("time", nc.variables["time"]), ("level", nc.variables["level"]), ("lat", nc.variables["lat"]),
             ("lon", nc.variables["lon"])])
    return result


def load_nc_time_ens_lat_lon_t2m(filename: str, key: str):
    with netCDF4.Dataset(filename=filename) as nc:
        var = nc.variables[key]
        result = xarray.DataArray(
            var[:, :, :, :, :],
            [("ens", nc.variables["ens"]), ("time", nc.variables["time"]), ("level", nc.variables["level"]),
             ("lat", nc.variables["lat"]), ("lon", nc.variables["lon"])])
    return result


# 线性插值，格点数据插值到站点数据，并且获取相应的站点数据
def interpolation_linear_g_to_s(grid_data, station_lons, station_lats, source_start_lon, source_start_lat,
                                source_end_lon, source_end_lat, source_lon_interval, source_lat_interval, **kwargs):
    """
    格点插值到站点
    :param grid_data: 格点场数据
    :param station_lons: 站点经度数组 numpy.array
    :param station_lats: 站点纬度数组 numpy.array
    :param source_start_lon: 起始经度
    :param source_start_lat: 起始纬度
    :param source_end_lon: 终止经度
    :param source_end_lat: 终止纬度
    :param source_lon_interval: 经度间隔
    :param source_lat_interval: 纬度间隔
    :return:
    """
    dat = numpy.squeeze(grid_data)
    ig = ((station_lons - source_start_lon) // source_lon_interval).astype(dtype='int16')
    jg = ((station_lats - source_start_lat) // source_lat_interval).astype(dtype='int16')
    dx = (station_lons - source_start_lon) / source_lon_interval - ig
    dy = (station_lats - source_start_lat) / source_lat_interval - jg
    c00 = (1 - dx) * (1 - dy)
    c01 = dx * (1 - dy)
    c10 = (1 - dx) * dy
    c11 = dx * dy
    gnlon = int((source_end_lon - source_start_lon) / source_lon_interval)
    gnlat = int((source_end_lat - source_start_lat) / source_lat_interval + 1)
    ig1 = numpy.minimum(ig + 1, gnlon - 1)
    jg1 = numpy.minimum(jg + 1, gnlat - 1)
    dat_sta = c00 * dat[jg, ig] + c01 * dat[jg, ig1] + c10 * dat[jg1, ig] + c11 * dat[jg1, ig1]
    return dat_sta


# 读取所有站点信息
def load_station_information():
    f = open('./file/dict_sta.txt', 'r', encoding='utf8')
    station_information_list = f.read().split('\n')
    station_information_list.remove('Station_Id_d,Lon,Lat,Alti,Station_Name,Province,City')
    station_id = []
    station_lon = []
    station_lat = []
    station_alti = []
    station_name = []
    station_province = []
    for line in station_information_list:
        station_information = line.split(',')
        if len(station_information) >= 6:
            if 70 <= float(station_information[1]) <= 140:
                if 10 <= float(station_information[2]) <= 60:
                    station_id.append(str(station_information[0]))
                    station_lon.append(float(station_information[1]))
                    station_lat.append(float(station_information[2]))
                    station_alti.append(float(station_information[3]))
                    station_name.append(station_information[4])
                    station_province.append(station_information[5])
    f.close()
    return numpy.array(station_id), numpy.array(station_lon), numpy.array(station_lat), numpy.array(
        station_alti), numpy.array(station_name), numpy.array(station_province)


if __name__ == "__main__":
    pass
