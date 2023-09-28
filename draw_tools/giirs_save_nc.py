import glob
import os.path
import xarray as xr
import pandas as pd
import numpy as np
import meteva.base as meb
import netCDF4 as nc


def save_nc(data, lons, lats, pressure,  filename):
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))
    if data is None:
        raise ValueError("no data")
    da = nc.Dataset(filename, "w")
    da.createDimension("lon", len(lons))
    da.createDimension("lat", len(lats))
    da.createDimension("pressure", len(pressure))
    da.createVariable("lon", "f", ("lon",), zlib=True)
    da.createVariable("lat", "f", ("lat",), zlib=True)
    da.createVariable("pressure", "f", ("pressure",), zlib=True)
    da.variables["lon"][:] = lons
    da.variables["lat"][:] = lats
    da.variables["pressure"][:] = pressure
    da.createVariable("val", "f", ("lat", "lon", "pressure"), zlib=True)
    da.variables["val"][:] = data
    da.close()

def transFrom_FY4A_GIIRS(inpath, outpath):
    grd0 = xr.open_dataset(inpath, engine='netcdf4')  # 通过xarray读入网格数据
    v = grd0['AT_Prof'].values
    v[v < 0] = np.nan
    lon = grd0["LW_Longitude"].values
    lon[lon < 0] = np.nan
    lat = grd0["LW_Latitude"].values
    lat[lat < 0] = np.nan
    grid = meb.grid([70, 140, 0.05], [0, 55, 0.05])  # 设置一个等经纬度的网格信息变量

    grds = []
    level_list = []#v.shape[0]
    for i in range(v.shape[0]):
        df = pd.DataFrame({"level": i+1, "time": "202302130800", "dtime": 0,
                           "lon": lon.flatten(),
                           "lat": lat.flatten(),
                           "id": np.arange(lat.size),
                           "AT_Prof": v[i, :, :].flatten()
                           })
        df = df.dropna()
        sta = meb.sta_data(df)  # 将DataFrame变量转换成站点数据格式
        grd1 = meb.interp_sg_idw(sta, grid=grid, nearNum=4, effectR=20)  # 将站点数据插值到网格上
        grds.append(np.array(grd1.data[0][0][0][0]))
        level_list.append(grd0['Pressure'].data[i])

    grid0 = meb.grid([70, 140, 0.05], [0, 55, 0.05],gtime=["202302130800"],dtime_list = [0],level_list = level_list)
    grd = meb.grid_data(grid0, np.array(grds))
    meb.write_griddata_to_nc(grd, outpath, effectiveNum = 2)
    print('Finished ' + os.path.split(inpath)[1])

if __name__ =="__main__":
    file_path = r'\\192.168.0.4\wiztek\FY4A\GIIRS\20230212'
    save_path = r'\\192.168.0.4\wiztek\FY4A\GIIRS\20230212\Transfrom'
    files = glob.glob(os.path.join(file_path, '*.NC'))
    for file in files:
        file_name = os.path.split(file)[1]
        out_path = os.path.join(save_path, file_name)
        if not os.path.exists(out_path):
            transFrom_FY4A_GIIRS(file, out_path)