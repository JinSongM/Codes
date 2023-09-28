import numpy as np

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
