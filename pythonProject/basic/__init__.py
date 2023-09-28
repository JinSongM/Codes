# -- coding: utf-8 --
# @Time : 2023/5/11 9:56
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : __init__.py.py
# @Software: PyCharm
import codecs
import datetime
import os
import re
import struct

import xarray as xr
import numpy as np
import netCDF4 as nc

from utils import arrays


class grid_data:
    def __init__(self, lon_start, lon_end, lon_res, lat_start, lat_end, lat_res):
        self._lon_start = lon_start
        self._lon_end = lon_end
        self._lon_res = lon_res
        self._lat_start = lat_start
        self._lat_end = lat_end
        self._lat_res = lat_res
        self._lon_num = None
        self._lat_num = None
        self._lons = None
        self._lats = None
        self._olons = None
        self._olats = None
        self._data = None
        self._kwargs = dict()

    def set_data(self, data):
        self._data = data

    def set_kwargs(self, **kwargs):
        self._kwargs = dict()
        for key in kwargs.keys():
            self._kwargs[key] = kwargs[key]

    def change_kwargs(self, **kwargs):
        for key in kwargs.keys():
            self._kwargs[key] = kwargs[key]

    @property
    def data(self):
        return self._data

    @property
    def kwargs(self):
        return self._kwargs

    @property
    def lon_start(self):
        return self._lon_start

    @property
    def lon_end(self):
        return self._lon_end

    @property
    def lon_res(self):
        return self._lon_res

    @property
    def lat_start(self):
        return self._lat_start

    @property
    def lat_end(self):
        return self._lat_end

    @property
    def lat_res(self):
        return self._lat_res

    @property
    def lon_num(self):
        self._lon_num = (self._lon_end - self._lon_start) / self._lon_res + 1
        return self._lon_num

    @property
    def lat_num(self):
        self._lat_num = (self._lat_end - self._lat_start) / self._lat_res + 1
        return self._lat_num

    @property
    def lons(self):
        self._lons = np.arange(self.lon_start, self.lon_end + self.lon_res / 10, self.lon_res)
        return self._lons

    @property
    def lats(self):
        self._lats = np.arange(self.lat_start, self.lat_end + self.lat_res / 10, self.lat_res)
        return self._lats

    @property
    def olons(self):
        self._olons, self._olats = np.meshgrid(self.lons, self.lats)
        return self._olons

    @property
    def olats(self):
        self._olons, self._olats = np.meshgrid(self.lons, self.lats)
        return self._olats

    def copy(self):
        re = grid_data(self.lon_start, self.lon_end, self.lon_res, self.lat_start, self.lat_end, self.lat_res)
        re._lons = self._lons
        re._lats = self._lats
        re._olons = self._olons
        re._olats = self._olats
        re._lon_num = self._lon_num
        re._lat_num = self._lat_num
        return re

    def copy_t2m(self):
        re = t2m_grid_data(self.lon_start, self.lon_end, self.lon_res, self.lat_start, self.lat_end, self.lat_res)
        re._lons = self._lons
        re._lats = self._lats
        re._olons = self._olons
        re._olats = self._olats
        re._lon_num = self._lon_num
        re._lat_num = self._lat_num
        return re

    def copy_ptype(self):
        re = ptype_grid_data(self.lon_start, self.lon_end, self.lon_res, self.lat_start, self.lat_end, self.lat_res)
        re._lons = self._lons
        re._lats = self._lats
        re._olons = self._olons
        re._olats = self._olats
        re._lon_num = self._lon_num
        re._lat_num = self._lat_num
        return re

    def copy_time(self):
        re = time_grid_data(self.lon_start, self.lon_end, self.lon_res, self.lat_start, self.lat_end, self.lat_res)
        re._lons = self._lons
        re._lats = self._lats
        re._olons = self._olons
        re._olats = self._olats
        return re

    def transform(self, start_lon, end_lon, start_lat, end_lat, delt_lon, delt_lat):
        if (start_lon == self.lon_start) & (end_lon == self.lon_end) & (start_lat == self.lat_start) & (end_lat == self.lat_end) & (delt_lon == self.lon_res) & (delt_lat == self.lat_res):
            pass
        else:
            da = xr.DataArray(self.data, [("lat", self.lats), ("lon", self.lons)])
            lons = np.arange(start_lon, end_lon + delt_lon * 0.1, delt_lon)
            lats = np.arange(start_lat, end_lat + delt_lat * 0.1, delt_lat)
            data_temp = da.interp(lat=lats, lon=lons, method="linear")
            self.set_data(np.array(data_temp, dtype=float))
            self._lon_start = start_lon
            self._lon_end = end_lon
            self._lat_start = start_lat
            self._lat_end = end_lat
            self._lon_res = delt_lon
            self._lat_res = delt_lat

    def save_m4(self, filename, date=datetime.datetime.now(), hour=0, level="9999", desc="", contour=" 1 1 5 1 0"):
        str_array = []
        str_time = datetime.datetime.strftime(date, '%Y%m%d%H')
        str_time2 = datetime.datetime.strftime(date, '%Y %m %d %H')
        str_array.append("diamond 4 %s\n" % (str_time + "_" + re.sub(r'\\s+', "_", desc)))

        str_array.append("%s %d %s %.3f %.3f %.3f %.3f %.3f %.3f %d %d %s\n" % (
            str_time2, int(hour), level, self.lon_res, self.lat_res, self.lon_start, self.lon_end, self.lat_start, self.lat_end, self.lon_num, self.lat_num, contour))

        for array in self.data:
            str_line = ""
            for arr in array:
                str_line += "%.2f%s" % (arr, " ")
            str_array.append((str_line + "\n").strip(" "))
        try:
            create_direction_if_not_exist(filename)
        except Exception as ex:
            raise ex
        with open(filename, 'w+', encoding="utf8") as fl:
            fl.writelines(str_array)

    def save_nc(self, filename, **kwargs):
        if self.data is None:
            raise ValueError("no data")
        create_direction_if_not_exist(filename)
        da = nc.Dataset(filename, "w")
        da.createDimension("lon", len(self.lons))
        da.createDimension("lat", len(self.lats))
        da.createVariable("lon", "f", ("lon",), zlib=True)
        da.createVariable("lat", "f", ("lat",), zlib=True)
        da.variables["lon"][:] = self.lons
        da.variables["lat"][:] = self.lats
        da.createVariable("val", "f", ("lat", "lon"), zlib=True)
        da.variables["val"][:] = self.data
        for key in self.kwargs:
            da.setncattr(key, self.kwargs[key])
        for key in kwargs:
            da.setncattr(key, kwargs[key])
        da.close()


class t2m_grid_data(grid_data):
    def __init__(self, lon_start, lon_end, lon_res, lat_start, lat_end, lat_res):
        super().__init__(lon_start, lon_end, lon_res, lat_start, lat_end, lat_res)

    def transform(self, start_lon, end_lon, start_lat, end_lat, delt_lon, delt_lat):
        if (start_lon == self.lon_start) & (end_lon == self.lon_end) & (start_lat == self.lat_start) & (end_lat == self.lat_end) & (delt_lon == self.lon_res) & (delt_lat == self.lat_res):
            pass
        else:
            da = xr.DataArray(self.data, [("lat", self.lats), ("lon", self.lons)])
            lons = np.arange(start_lon, end_lon + delt_lon * 0.1, delt_lon)
            lats = np.arange(start_lat, end_lat + delt_lat * 0.1, delt_lat)
            data_temp = da.interp(lat=lats, lon=lons, method="linear")
            self.set_data(np.array(data_temp, dtype=float))
            self._lon_start = start_lon
            self._lon_end = end_lon
            self._lat_start = start_lat
            self._lat_end = end_lat
            self._lon_res = delt_lon
            self._lat_res = delt_lat

    def save_nc(self, filename, **kwargs):
        if self.data is None:
            raise ValueError("no data")
        create_direction_if_not_exist(filename)
        da = nc.Dataset(filename, "w")
        da.createDimension("lon", len(self.lons))
        da.createDimension("lat", len(self.lats))
        da.createVariable("lon", "f", ("lon",), zlib=True)
        da.createVariable("lat", "f", ("lat",), zlib=True)
        da.variables["lon"][:] = self.lons
        da.variables["lat"][:] = self.lats
        da.createVariable("t2m", "f", ("lat", "lon"), zlib=True)
        da.variables["t2m"][:] = self.data
        for key in self.kwargs:
            da.setncattr(key, self.kwargs[key])
        for key in kwargs:
            da.setncattr(key, kwargs[key])
        da.close()


class ptype_grid_data(grid_data):
    def __init__(self, lon_start, lon_end, lon_res, lat_start, lat_end, lat_res):
        super().__init__(lon_start, lon_end, lon_res, lat_start, lat_end, lat_res)

    def transform(self, start_lon, end_lon, start_lat, end_lat, delt_lon, delt_lat):
        if (start_lon == self.lon_start) & (end_lon == self.lon_end) & (start_lat == self.lat_start) & (end_lat == self.lat_end) & (delt_lon == self.lon_res) & (delt_lat == self.lat_res):
            pass
        else:
            da = xr.DataArray(self.data, [("lat", self.lats), ("lon", self.lons)])
            lons = np.arange(start_lon, end_lon + delt_lon * 0.1, delt_lon)
            lats = np.arange(start_lat, end_lat + delt_lat * 0.1, delt_lat)
            data_temp = da.interp(lat=lats, lon=lons, method="linear")
            self.set_data(np.array(data_temp, dtype=float))
            self._lon_start = start_lon
            self._lon_end = end_lon
            self._lat_start = start_lat
            self._lat_end = end_lat
            self._lon_res = delt_lon
            self._lat_res = delt_lat

    def save_m4(self, filename, date=datetime.datetime.now(), hour=0, level="9999", desc="", contour=" 1 0 4 1 0"):
        str_array = []
        str_time = datetime.datetime.strftime(date, '%Y%m%d%H')
        str_time2 = datetime.datetime.strftime(date, '%Y %m %d %H')
        str_array.append("diamond 4 %s\n" % (str_time + "_" + re.sub(r'\\s+', "_", desc)))

        str_array.append("%s %d %s %.3f %.3f %.3f %.3f %.3f %.3f %d %d %s\n" % (
            str_time2, int(hour), level, self.lon_res, self.lat_res, self.lon_start, self.lon_end, self.lat_start, self.lat_end, self.lon_num, self.lat_num, contour))

        for array in self.data:
            str_line = ""
            for arr in array:
                str_line += "%d%s" % (arr, " ")
            str_array.append((str_line + "\n").strip(" "))
        try:
            create_direction_if_not_exist(filename)
        except Exception as ex:
            raise ex
        with open(filename, 'w+', encoding="utf8") as fl:
            fl.writelines(str_array)

    def save_nc(self, filename, **kwargs):
        if self.data is None:
            raise ValueError("no data")
        create_direction_if_not_exist(filename)
        da = nc.Dataset(filename, "w")
        da.createDimension("lon", len(self.lons))
        da.createDimension("lat", len(self.lats))
        da.createVariable("lon", "f", ("lon",), zlib=True)
        da.createVariable("lat", "f", ("lat",), zlib=True)
        da.variables["lon"][:] = self.lons
        da.variables["lat"][:] = self.lats
        da.createVariable("ptype", "i", ("lat", "lon"), zlib=True)
        da.variables["ptype"][:] = self.data
        for key in self.kwargs:
            da.setncattr(key, self.kwargs[key])
        for key in kwargs:
            da.setncattr(key, kwargs[key])
        da.close()


class ec_grib_data(grid_data):
    def __init__(self, lon_start, lon_end, lon_res, lat_start, lat_end, lat_res):
        super().__init__(lon_start, lon_end, lon_res, lat_start, lat_end, lat_res)
        self._ensemble = None

    @property
    def ensemble(self):
        return self._ensemble

    @property
    def ensemble_count(self):
        return len(self._ensemble)

    def set_ensemble(self, ensemble):
        self._ensemble = ensemble

    def transform(self, start_lon, end_lon, start_lat, end_lat, delt_lon, delt_lat):
        if (start_lon == self.lon_start) & (end_lon == self.lon_end) & (start_lat == self.lat_start) & (end_lat == self.lat_end) & (delt_lon == self.lon_res) & (delt_lat == self.lat_res):
            pass
        else:
            if (delt_lon == self.lon_res) & (delt_lat == self.lat_res):
                lat_start = (start_lat - self.lat_start) / delt_lat
                lat_end = (end_lat - self.lat_start) / delt_lat + delt_lat
                data_temp = self.data[lat_start:lat_end, lat_start, lat_end]
                self.set_data(np.array(data_temp, dtype=float))
                self._lon_start = start_lon
                self._lon_end = end_lon
                self._lat_start = start_lat
                self._lat_end = end_lat
                self._lon_res = delt_lon
                self._lat_res = delt_lat
            else:
                da = xr.DataArray(self.data, [("lat", self.lats), ("lon", self.lons), ("ensemble", self.ensemble)])
                lons = np.arange(start_lon, end_lon + delt_lon * 0.1, delt_lon)
                lats = np.arange(start_lat, end_lat + delt_lat * 0.1, delt_lat)
                data_temp = da.interp(lat=lats, lon=lons, method="linear")
                self.set_data(np.array(data_temp, dtype=float))
                self._lon_start = start_lon
                self._lon_end = end_lon
                self._lat_start = start_lat
                self._lat_end = end_lat
                self._lon_res = delt_lon
                self._lat_res = delt_lat

    def save_nc(self, filename, **kwargs):
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        if self.data is None:
            raise ValueError("no data")
        da = nc.Dataset(filename, "w")
        da.createDimension("lon", len(self.lons))
        da.createDimension("lat", len(self.lats))
        da.createDimension("ensemble", len(self.ensemble))
        da.createVariable("lon", "f", ("lon",), zlib=True)
        da.createVariable("lat", "f", ("lat",), zlib=True)
        da.createVariable("ensemble", "f", ("ensemble",), zlib=True)
        da.variables["lon"][:] = self.lons
        da.variables["lat"][:] = self.lats
        da.variables["ensemble"][:] = self.ensemble
        da.createVariable("val", "f", ("lat", "lon", "ensemble"), zlib=True)
        da.variables["val"][:] = self.data
        for key in self.kwargs:
            da.setncattr(key, self.kwargs[key])
        for key in kwargs:
            da.setncattr(key, kwargs[key])
        da.close()


class time_grid_data(grid_data):
    def __init__(self, lon_start, lon_end, lon_res, lat_start, lat_end, lat_res):
        super().__init__(lon_start, lon_end, lon_res, lat_start, lat_end, lat_res)

    def transform(self, start_lon, end_lon, start_lat, end_lat, delt_lon, delt_lat):
        if (start_lon == self.lon_start) & (end_lon == self.lon_end) & (start_lat == self.lat_start) & (end_lat == self.lat_end) & (delt_lon == self.lon_res) & (delt_lat == self.lat_res):
            pass
        else:
            lons = np.arange(start_lon, end_lon + delt_lon * 0.1, delt_lon)
            lats = np.arange(start_lat, end_lat + delt_lat * 0.1, delt_lat)
            index_lons = np.array(np.round((lons - self.lon_start) / self.lon_res), dtype=int)
            index_lats = np.array(np.round((lats - self.lat_start) / self.lat_res), dtype=int)
            lon_index, lat_index = np.meshgrid(index_lons, index_lats)
            temp_data = self.data[(lat_index, lon_index)]
            self.set_data(temp_data)
            self._lon_start = start_lon
            self._lon_end = end_lon
            self._lat_start = start_lat
            self._lat_end = end_lat
            self._lon_res = delt_lon
            self._lat_res = delt_lat

    def save_m4(self, filename, date=datetime.datetime.now(), hour=0, level="9999", desc="", contour=" 100 0 1200 1 0"):
        str_array = []
        str_time = datetime.datetime.strftime(date, '%Y%m%d%H')
        str_time2 = datetime.datetime.strftime(date, '%Y %m %d %H')
        str_array.append("diamond 4 %s\n" % (str_time + "_" + re.sub(r'\\s+', "_", desc)))

        str_array.append("%s %d %s %.3f %.3f %.3f %.3f %.3f %.3f %d %d %s\n" % (
            str_time2, int(hour), level, self.lon_res, self.lat_res, self.lon_start, self.lon_end, self.lat_start, self.lat_end, self.lon_num, self.lat_num, contour))

        for array in self.data:
            str_line = ""
            for arr in array:
                str_line += "%d%s" % (arr, " ")
            str_array.append((str_line + "\n").strip(" "))
        try:
            create_direction_if_not_exist(filename)
        except Exception as ex:
            raise ex
        with open(filename, 'w+', encoding="utf8") as fl:
            fl.writelines(str_array)

    def save_nc(self, filename, **kwargs):
        if self.data is None:
            raise ValueError("no data")
        create_direction_if_not_exist(filename)
        da = nc.Dataset(filename, "w")
        da.createDimension("lon", len(self.lons))
        da.createDimension("lat", len(self.lats))
        da.createVariable("lon", "f", ("lon",), zlib=True)
        da.createVariable("lat", "f", ("lat",), zlib=True)
        da.variables["lon"][:] = self.lons
        da.variables["lat"][:] = self.lats
        da.createVariable("time", "f", ("lat", "lon"), zlib=True)
        da.variables["time"][:] = self.data
        for key in self.kwargs:
            da.setncattr(key, self.kwargs[key])
        for key in kwargs:
            da.setncattr(key, kwargs[key])
        da.close()


class terrain_grid_data(grid_data):
    def __init__(self, lon_start, lon_end, lon_res, lat_start, lat_end, lat_res):
        super().__init__(lon_start, lon_end, lon_res, lat_start, lat_end, lat_res)
        pass


def load_ptype_data_ec(filename):
    try:
        if not os.path.exists(filename):
            # logger.error("文件缺失：{}".format(filename))
            return None
        with nc.Dataset(filename, mode="r") as da:
            lon = da.variables['lon'][:]
            lat = da.variables['lat'][:]
            val = da.variables["ptype"][:]
            lon_r = (lon[-1] - lon[0]) / (len(lon) - 1)
            lat_r = (lat[-1] - lat[0]) / (len(lat) - 1)
            ec_grid = ptype_grid_data(lon[0], lon[-1], lon_r, lat[0], lat[-1], lat_r)
            ec_grid.set_data(val)
        return ec_grid
    except Exception as ex:
        raise ex


def load_ptype_data_m4(filename):
    try:
        if not os.path.exists(filename):
            # logger.error("文件缺失：{}".format(filename))
            return None
        # 打开文件，进行解析
        with open(filename, "r", encoding="utf8") as fh:
            lines = fh.readlines()
        p = re.compile("\\s+")
        head = p.split(lines[1].strip())

        lon_start, lon_end, lon_res = float(head[8]), float(head[9]), float(head[6])
        lat_start, lat_end, lat_res = float(head[10]), float(head[11]), float(head[7])
        lon_count, lat_count = int(head[12]), int(head[13])

        m4_grid = ptype_grid_data(lon_start, lon_end, lon_res, lat_start, lat_end, lat_res)
        array = []
        for line in lines[2:]:
            array.extend(p.split(line.replace("\n", "").strip()))
        array = np.reshape(np.array(array, dtype=int), (lat_count, lon_count))
        m4_grid.set_data(array)
        return m4_grid
    except Exception as ex:
        # logger.error("文件解析报错: {}".format(filename), ex)
        raise ex


def load_tp_data_bin(filename, dst_dict: dict):
    try:
        if not os.path.exists(filename):
            # logger.error("文件缺失：{}".format(filename))
            return None
        # logger.info("加载EC降水确定性预报数据: {}".format(filename))
        with open(filename, 'rb') as f:
            c = f.read()
            fmt_header = 'iffffffiiiffff'
            version, lon0, lon1, lat0, lat1, dx, dy, nx, ny, length, mn, mx, delta, missing = struct.unpack(
                fmt_header, c[8:64])
            fmt_array = '%dH' % (nx * ny)
            array = np.array(struct.unpack(
                fmt_array, c[64:]), np.float32).reshape(ny, nx)
            array = array * delta + mn
        temp_grid = grid_data(lon0, lon1, dx, lat0, lat1, dy)
        temp_grid.set_data(array)
        temp_grid.transform(dst_dict["lon_s"], dst_dict["lon_e"], dst_dict["lat_s"], dst_dict["lat_e"], dst_dict["lon_d"], dst_dict["lat_d"])
        return temp_grid
    except Exception as ex:
        # logger.error("文件解析报错: {}".format(filename), ex)
        raise ex


def load_terrain_array(filename, dst_dict, type=np.float64):
    try:
        a = arrays.load_array(filename)
        b = np.array(a, dtype=type).reshape(1201, 1401)
        b[b < -9990] = np.nan
        temp_data = terrain_grid_data(70, 140, 0.05, 0, 60, 0.05)
        temp_data.set_data(b)
        temp_data.transform(dst_dict["lon_s"], dst_dict["lon_e"], dst_dict["lat_s"], dst_dict["lat_e"], dst_dict["lon_d"], dst_dict["lat_d"])
        temp_data.set_data(np.array(temp_data.data, dtype=type))
        temp_data.data[np.isnan(temp_data.data)] = 9999
        return temp_data
    except Exception as ex:
        # logger.error("文件解析报错: {}".format(filename), ex)
        raise ex


def trans_degree(arr):
    lonlat = np.array(arr, dtype='float32') / 100.

    just = np.floor(lonlat)
    return just + (lonlat - just) * 100 / 60


def read_from_file(filename, dst_lon_lat=None, isTransDegree10=True):
    try:
        file_object = codecs.open(filename, mode='r', encoding='GBK')
        all_the_text = file_object.read().strip()
        file_object.close()
        contents = re.split(r'[\s]+', all_the_text)

        stationsum = int(contents[3].strip())

        data = np.array(contents[4: 4 + stationsum * 4]).reshape((stationsum, 4))

        if isTransDegree10:
            lat = trans_degree(data[:, 1])  # 经度 60进制乘以100的整数 => 10进制浮点数
            lon = trans_degree(data[:, 2])  # 纬度 60进制乘以100的整数 => 10进制浮点数
        else:
            lat = np.array(data[:, 1], dtype='float32')  # 经度 60进制
            lon = np.array(data[:, 2], dtype='float32')  # 纬度 60进制
        lats = list()
        lons = list()
        for i in range(0, len(lat)):
            if lat[i] > dst_lon_lat["lat_e"] or lat[i] < dst_lon_lat["lat_s"] or lon[i] > dst_lon_lat["lon_e"] or lon[i] < dst_lon_lat["lon_s"]:
                continue
            lats.append(lat[i])
            lons.append(lon[i])
        return {"lat": lats, "lon": lons}
    except Exception as ex:
        # logger.error("文件解析报错: {}".format(filename), ex)
        raise ex

def load_bin_array(filename, dst_dict, type=np.float64):
    try:
        a = arrays.load_array(filename)
        b = np.array(a, dtype=type).reshape(6001, 7001)
        temp_data = grid_data(70, 140, 0.01, 0, 60, 0.01)
        temp_data.set_data(b)
        temp_data.transform(dst_dict["lon_s"], dst_dict["lon_e"], dst_dict["lat_s"], dst_dict["lat_e"], dst_dict["lon_d"], dst_dict["lat_d"])
        temp_data.set_data(np.array(temp_data.data, dtype=type))
        temp_data.data[np.isnan(temp_data.data)] = 9999
        return temp_data
    except Exception as ex:
        # logger.error("文件解析报错: {}".format(filename), ex)
        raise ex


def load_bin_time_array(filename, src_dict, dst_dict):
    try:
        lon_s, lon_e, lat_s, lat_e, lon_d, lat_d = src_dict["lon_s"], src_dict["lon_e"], src_dict["lat_s"], src_dict["lat_e"], src_dict["lon_d"], src_dict["lat_d"]
        lon_c = len(np.arange(lon_s, lon_e + lon_d * 0.1, lon_d))
        lat_c = len(np.arange(lat_s, lat_e + lat_d * 0.1, lat_d))
        a = arrays.load_array(filename)
        b = np.array(a, dtype=np.int).reshape(lat_c, lon_c)
        temp_data = time_grid_data(lon_s, lon_e, lon_d, lat_s, lat_e, lat_d)
        temp_data.set_data(b)
        temp_data.transform(dst_dict["lon_s"], dst_dict["lon_e"], dst_dict["lat_s"], dst_dict["lat_e"], dst_dict["lon_d"], dst_dict["lat_d"])
        temp_data.set_data(np.array(temp_data.data))
        temp_data.data[np.isnan(temp_data.data)] = 9999
        return temp_data
    except Exception as ex:
        # logger.error("文件解析报错: {}".format(filename), ex)
        raise ex


def load_th_hss_max(filename, dst_dict):
    try:
        temp_dict = dict()
        if not os.path.exists(filename):
            # logger.error("文件缺失：{}".format(filename))
            return None
        data_temp_dict = dict()
        with nc.Dataset(filename, mode="r") as da:
            lon = da.variables['longitude'][:]
            lat = da.variables['latitude'][:]
            data_temp_dict["freezing"] = da.variables["freezing"][:]
            data_temp_dict["rain"] = da.variables["rain"][:]
            data_temp_dict["sleet"] = da.variables["sleet"][:]
            data_temp_dict["snow"] = da.variables["snow"][:]
        lon_start = lon[0]
        lon_end = lon[-1]
        lon_res = (lon_end - lon_start) / (len(lon) - 1)
        lat_start = lat[0]
        lat_end = lat[-1]
        lat_res = (lat_end - lat_start) / (len(lat) - 1)

        for k, v in data_temp_dict.items():
            temp_list = list()
            for i in range(0, 10):
                temp = grid_data(lon_start, lon_end, lon_res, lat_start, lat_end, lat_res)
                temp.set_data(v[i])
                temp.transform(dst_dict["lon_s"], dst_dict["lon_e"], dst_dict["lat_s"], dst_dict["lat_e"], dst_dict["lon_d"], dst_dict["lat_d"])
                temp_list.append(temp)
            temp_dict[k.upper()] = temp_list
        return temp_dict
    except Exception as ex:
        # logger.error("文件解析报错: {}".format(filename), ex)
        raise ex


def load_m4(filename: str, dst_dict, type, encoding="utf8"):
    try:
        if not os.path.exists(filename):
            # logger.error("文件缺失：{}".format(filename))
            return None
        # 打开文件，进行解析
        with open(filename, "r", encoding=encoding) as fh:
            lines = fh.readlines()
        p = re.compile("\\s+")
        head = p.split(lines[1].strip())

        lon_start, lon_end, lon_res = float(head[8]), float(head[9]), float(head[6])
        lat_start, lat_end, lat_res = float(head[10]), float(head[11]), float(head[7])
        lon_count, lat_count = int(head[12]), int(head[13])

        temp = grid_data(lon_start, lon_end, lon_res, lat_start, lat_end, lat_res)
        array = []
        for line in lines[2:]:
            array.extend(p.split(line.replace("\n", "").strip()))
        array = np.reshape(np.array(array, dtype=type), (lat_count, lon_count))
        temp.set_data(array)
        temp.transform(dst_dict["lon_s"], dst_dict["lon_e"], dst_dict["lat_s"], dst_dict["lat_e"], dst_dict["lon_d"], dst_dict["lat_d"])
        temp.data[np.isnan(temp.data)] = 9999
        return temp
    except Exception as ex:
        # logger.error("文件解析报错: {}".format(filename), ex)
        raise ex


def load_t2m_m4(filename: str, dst_dict, encoding="utf8"):
    try:
        if not os.path.exists(filename):
            # logger.error("文件缺失：{}".format(filename))
            return None
        # 打开文件，进行解析
        with open(filename, "r", encoding=encoding) as fh:
            lines = fh.readlines()
        p = re.compile("\\s+")
        head = p.split(lines[1].strip())

        lon_start, lon_end, lon_res = float(head[8]), float(head[9]), float(head[6])
        lat_start, lat_end, lat_res = float(head[10]), float(head[11]), float(head[7])
        lon_count, lat_count = int(head[12]), int(head[13])

        temp = t2m_grid_data(lon_start, lon_end, lon_res, lat_start, lat_end, lat_res)
        array = []
        for line in lines[2:]:
            array.extend(p.split(line.replace("\n", "").strip()))
        array = np.reshape(np.array(array, dtype=np.float), (lat_count, lon_count))
        temp.set_data(array)
        temp.transform(dst_dict["lon_s"], dst_dict["lon_e"], dst_dict["lat_s"], dst_dict["lat_e"], dst_dict["lon_d"], dst_dict["lat_d"])
        temp.data[np.isnan(temp.data)] = 9999
        return temp
    except Exception as ex:
        # logger.error("文件解析报错: {}".format(filename), ex)
        raise ex


def load_time_m4(filename: str, dst_dict, encoding="utf8"):
    try:
        if not os.path.exists(filename):
            # logger.error("文件缺失：{}".format(filename))
            return None
        # 打开文件，进行解析
        with open(filename, "r", encoding=encoding) as fh:
            lines = fh.readlines()
        p = re.compile("\\s+")
        head = p.split(lines[1].strip())

        lon_start, lon_end, lon_res = float(head[8]), float(head[9]), float(head[6])
        lat_start, lat_end, lat_res = float(head[10]), float(head[11]), float(head[7])
        lon_count, lat_count = int(head[12]), int(head[13])

        temp = time_grid_data(lon_start, lon_end, lon_res, lat_start, lat_end, lat_res)
        array = []
        for line in lines[2:]:
            array.extend(p.split(line.replace("\n", "").strip()))
        array = np.reshape(np.array(array, dtype=int), (lat_count, lon_count))
        temp.set_data(array)
        temp.transform(dst_dict["lon_s"], dst_dict["lon_e"], dst_dict["lat_s"], dst_dict["lat_e"], dst_dict["lon_d"], dst_dict["lat_d"])
        return temp
    except Exception as ex:
        # logger.error("文件解析报错: {}".format(filename), ex)
        raise ex


def load_precipitation_nc(filename: str, dst_dict: dict):
    try:
        if not os.path.exists(filename):
            # logger.error("文件缺失：{}".format(filename))
            return None
        with nc.Dataset(filename, mode="r") as da:
            lon = da.variables['lon'][:]
            lat = da.variables['lat'][:]
            ensemble = da.variables["ensemble"][:]
            val = da.variables["val"][:]
            lon_r = (lon[-1] - lon[0]) / (len(lon) - 1)
            lat_r = (lat[-1] - lat[0]) / (len(lat) - 1)
            ec_grib = ec_grib_data(lon[0], lon[-1], lon_r, lat[0], lat[-1], lat_r)
            ec_grib.set_ensemble(ensemble)
            ec_grib.set_data(val)
            ec_grib.transform(dst_dict["lon_s"], dst_dict["lon_e"], dst_dict["lat_s"], dst_dict["lat_e"], dst_dict["lon_d"], dst_dict["lat_d"])
        return ec_grib
    except Exception as ex:
        # logger.error("文件解析报错: {}".format(filename), ex)
        raise ex


def create_direction_if_not_exist(filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except Exception as ex:
            # logger.error("创建文件路径报错: {}".format(filename), ex)
            raise ex


if __name__ == '__main__':
    load_tp_data_bin("//192.168.0.4/product/007_ECMWF_DATA/ECMWF_D1D/2022061608/tp/2022061608.006")
