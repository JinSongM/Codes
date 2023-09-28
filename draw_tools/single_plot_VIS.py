from datetime import datetime,timedelta
import numpy as np
import metdig
import meteva.base as meb
from  matplotlib import font_manager
import matplotlib.pyplot as plt
import os, re, sys
import multiprocessing as mp
from metdig.graphics import draw_compose, contourf_method
import xarray as xr
font_manager.fontManager.addfont('/mnt/shortQPF/simhei.ttf')



tp_color =  [
		[255, 255, 255],
		[167, 242, 143],
		[54, 187, 68],
		[100, 184, 253],
		[0, 0, 254],
		[255, 0, 255],
		[130, 0, 62]
	]

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

def open_m4(file: str, encoding='gbk'):
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

    lat_lon_data = LatLonData(start_lon, end_lon, start_lat, end_lat, delt_lon, delt_lat, lon_count, lat_count)

    _array = np.reshape(np.array(array[22:], dtype=float), (lat_count, lon_count))
    lat_lon_data.data = _array
    return lat_lon_data

def metdig_single_plot(Infile_list, lat_lon_data, drw, data, cmap):

    lats = np.linspace(lat_lon_data.start_lat, lat_lon_data.end_lat, lat_lon_data.lat_count)
    lons = np.linspace(lat_lon_data.start_lon, lat_lon_data.end_lon, lat_lon_data.lon_count)
    xr_data = xr.DataArray(data, coords=(lats, lons), dims=("lat", "lon"))
    std_data = metdig.utl.xrda_to_gridstda(xr_data, level_dim='level', time_dim='time', lat_dim='lat',
                                           lon_dim='lon', dtime_dim='dtime',
                                           var_name=Infile_list[3], np_input_units=Infile_list[4])
    contourf_method.contourf_2d(drw.ax, std_data, levels=Infile_list[5], cb_label=Infile_list[3], cmap=cmap)

def createdir(arg_dir):
    if os.path.exists(arg_dir):
        print('file path exists: ' + arg_dir)
    else:
        os.makedirs(arg_dir)
        print('Create file path: ' + arg_dir)

def plot(path, output_dir):
    createdir(output_dir)

    if os.path.exists(path):
        lat_lon_data = open_m4(path, encoding='utf-8')
        lats = np.linspace(lat_lon_data.start_lat, lat_lon_data.end_lat, lat_lon_data.lat_count)
        lons = np.linspace(lat_lon_data.start_lon, lat_lon_data.end_lon, lat_lon_data.lon_count)
        grid_w = meb.grid([115., 124.99, 0.03], [30., 39.99, 0.03])
        grb = meb.read_griddata_from_micaps4(r'D:\data\cpvs\DataBase\MOD\vis_g\mask-1km.txt', grid = grid_w)
        mask = grb[0][0][0][0].data
        lat_lon_data.data[mask > 10] = np.nan
        lat_lon_data.data[mask < 10] = np.nan
        xr_data = xr.DataArray(lat_lon_data.data, coords=(lats, lons), dims=("lat", "lon"))
        std_data = metdig.utl.xrda_to_gridstda(xr_data, level_dim='level', time_dim='time', lat_dim='lat',
                                               lon_dim='lon', dtime_dim='dtime',
                                               var_name='vis', np_input_units='km')
        file_time = os.path.split(path)[1].split('.')[0]
        Fst_time = int(os.path.split(path)[1].split('.')[1])
        obs_time_dc = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(datetime.strptime(file_time, '%Y%m%d%H'))
        fst_time_dc = '预报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(datetime.strptime(file_time, '%Y%m%d%H') + timedelta(hours=Fst_time))
        forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时'.format(Fst_time)
        png_name = file_time + '.' + os.path.split(path)[1].split('.')[1] + '.PNG'

        cmap_tp =  ["#722700", "#9D00FF", 'E63F00',"#FD0200", "#FF5500", "#FFBB03", "#FFEA00", "#D8FC2B", "#00FF00",
               "#30F9AB", "#65C8EA", "#97DCF2", "#97DDF1"]
        if not os.path.exists(os.path.join(output_dir, png_name)):
            drw = draw_compose.horizontal_compose(title="[VIS]能见度", description=forcast_info, output_dir=output_dir,add_tag=False, add_city=False,
                                                  map_extent=(116, 122, 30, 36), png_name=png_name, is_return_figax=True)
            contourf_method.contourf_2d(drw.ax, std_data, levels=[0, 0.2, 0.5, 1, 2, 3, 5, 10, 20, 30], cb_label="VIS", cmap=cmap_tp, extend = 'neither')
            drw.save()
    else:
        pass

def main(UTC_Now, file_paths, file_savepaths):

    args = []
    for i in range(24, 25):
        file_obs_path = file_paths.format(report = UTC_Now, cst = i)
        file_savepath = file_savepaths.format(report = UTC_Now)
        args.append([file_obs_path, file_savepath])

    pool = mp.Pool()
    res = pool.starmap_async(plot, args)
    res.get()
    pool.close()
    pool.join()


if __name__ == '__main__':

    file_paths = r'D:\cpvs\mnt\205\data/{report:%Y%m%d%H}.{cst:03d}'
    file_savepaths = r'D:\cpvs\mnt\205\data/{report:%Y%m%d}'

    if len(sys.argv) == 3:
        date_start = datetime.strptime(sys.argv[1], "%Y%m%d%H")
        date_end = datetime.strptime(sys.argv[2], "%Y%m%d%H")
        while date_start <= date_end:
            main(date_start, file_paths, file_savepaths)
            date_start += timedelta(hours=1)
    if len(sys.argv) == 2:
        date_start = datetime.strptime(sys.argv[1], "%Y%m%d%H")
        date_end = datetime.strptime(sys.argv[1], "%Y%m%d%H")
        while date_start <= date_end:
            main(date_start, file_paths, file_savepaths)
            date_start += timedelta(days=1)
    if len(sys.argv) == 1:
        date_end = datetime.utcnow()
        date_start = datetime.utcnow() - timedelta(hours=1)
        while date_start <= date_end:
            main(date_start, file_paths, file_savepaths)
            date_start += timedelta(hours=1)
