import numpy as np
import math
from utils import bilinear as linear

MISS_VALUE = 9999.0


class LatLonData(object):
    def __init__(self, start_lon, end_lon, start_lat, end_lat, delt_lon, delt_lat, lon_count, lat_count):
        self.start_lon = start_lon
        self.end_lon = end_lon
        self.start_lat = start_lat
        self.end_lat = end_lat
        self.delt_lon = delt_lon
        self.delt_lat = delt_lat
        self.lon_count = lon_count
        self.lat_count = lat_count
        self.data = np.zeros(shape=(lat_count, lon_count))

    def transform(self, start_lon, end_lon, start_lat, end_lat, delt_lon, delt_lat, lon_count, lat_count,
                  bilinear=False):

        newData = np.zeros((lat_count, lon_count), dtype=float)
        for y, lat in enumerate(np.arange(start_lat, end_lat, delt_lat)):
            for x, lon in enumerate(np.arange(start_lon, end_lon, delt_lon)):
                if lon < self.start_lon:
                    lon = (lon + 360) % 360
                elif lon > self.end_lon:
                    lon = - ((360 - lon) % 360)
                newData[y, x] = self.get_data(lat, lon, bilinear)

        self.data = newData

        self.start_lon = start_lon
        self.end_lon = end_lon
        self.start_lat = start_lat
        self.end_lat = end_lat
        self.delt_lon = delt_lon
        self.delt_lat = delt_lat
        self.lon_count = lon_count
        self.lat_count = lat_count

    def crop(self, start_lon, end_lon, start_lat, end_lat):
        _x1 = int(round((start_lon - self.start_lon) / self.delt_lon))
        _x2 = int(round((end_lon - self.start_lon) / self.delt_lon))

        _y1 = int(round((start_lat - self.start_lat) / self.delt_lat))
        _y2 = int(round((end_lat - self.start_lat) / self.delt_lat))
        new_data = self.data[_y1:_y2 + 1, _x1:_x2 + 1]
        self.start_lon = start_lon
        self.end_lon = end_lon
        self.start_lat = start_lat
        self.end_lat = end_lat
        self.data = new_data
        self.lon_count = _x2 - _x1 + 1
        self.lat_count = _y2 - _y1 + 1

    def get_data(self, lat=None, lon=None, bilinear=False):
        if not bilinear:
            lon = (lon + 360) % 360

            y = int(round((lat - self.start_lat) / self.delt_lat))
            x = int(round((lon - self.start_lon) / self.delt_lon))

            if 0 <= y < self.lat_count and 0 <= x < self.lon_count:
                return self.data[y, x]
            else:
                return MISS_VALUE
        # 超出范围，返回缺测

        if lat > max(self.start_lat, self.end_lat) or \
                lat < min(self.start_lat, self.end_lat) or lon < self.start_lon or lon > self.end_lon:
            return MISS_VALUE

        # 所在格点定点索引位置
        y0 = min(int(math.floor((lat - self.start_lat) / self.delt_lat)), self.lat_count - 2) - 1
        x0 = min(int(math.floor((lon - self.start_lon) / self.delt_lon)), self.lon_count - 2) - 1

        # 指定点在当前格子内的位置百分比
        yy = (lat - (self.start_lat + self.delt_lat * (y0 + 1))) / self.delt_lat
        xx = (lon - (self.start_lon + self.delt_lon * (x0 + 1))) / self.delt_lon

        # 四个顶点的相关值
        v00 = self.data[y0][x0]
        v01 = self.data[y0][x0 + 1]
        v10 = self.data[y0 + 1][x0]
        v11 = self.data[y0 + 1][x0 + 1]

        # 插值到指定的点
        return float(linear.calc(v00, v01, v10, v11, yy, xx))

    def transform_new(self, start_lon, end_lon, start_lat, end_lat, delt_lon, delt_lat, lon_count,
                      lat_count):

        """
        :param start_lon:
        :param end_lon:
        :param start_lat:
        :param end_lat:
        :param delt_lon:
        :param delt_lat:
        :param lon_count:
        :param lat_count:
        :return:
        """
        src_lons = np.linspace(start_lon, end_lon, lon_count)
        src_lats = np.linspace(start_lat, end_lat, lat_count)
        src_lons, src_lats = np.meshgrid(src_lons, src_lats)
        dat = np.squeeze(self.data)
        ig = ((src_lons - self.start_lon) // self.delt_lon).astype(dtype='int16')

        jg = ((src_lats - self.start_lat) // self.delt_lat).astype(dtype='int16')
        dx = (src_lons - self.start_lon) / self.delt_lon - ig
        dy = (src_lats - self.start_lat) / self.delt_lat - jg
        c00 = (1 - dx) * (1 - dy)
        c01 = dx * (1 - dy)
        c10 = (1 - dx) * dy
        c11 = dx * dy
        ig1 = np.minimum(ig + 1, lon_count - 1)
        jg1 = np.minimum(jg + 1, lat_count - 1)
        dat_sta = c00 * dat[jg, ig] + c01 * dat[jg, ig1] + c10 * dat[jg1, ig] + c11 * dat[jg1, ig1]
        self.data = dat_sta

        self.start_lon = start_lon
        self.end_lon = end_lon
        self.start_lat = start_lat
        self.end_lat = end_lat
        self.delt_lon = delt_lon
        self.delt_lat = delt_lat
        self.lon_count = lon_count
        self.lat_count = lat_count
