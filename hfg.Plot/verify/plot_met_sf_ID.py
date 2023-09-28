import os.path
import numpy as np
from datetime import datetime
from .config import *
from utils import MICAPS4 as M4
from met_plot.plot_model import PlotHgtWindProd
import xarray as xr

REGION_NAME = ["EA", "CHN", "NE", "HB", "HHJH", "JNHN", "XN", "NW", "NH"]
REGION = [
    [60, 150, 0, 70],
    [70, 150, 10, 60],
    [110, 138, 35, 57],
    [105, 125, 30, 47],
    [104, 125, 26, 41],
    [104, 125, 16, 33],
    [92, 115, 20, 35],
    [73, 123, 37, 50],
    [0, 240, 0, 90]
]
LEV = [1000, 925, 850, 700, 500, 200, 100]

def get_org_data(model_name: str, report_time, cst, element, lev, scale=1):
    file_path = MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element=element, lev=lev)
    if not os.path.exists(file_path):
        return None
    lat_lon_data = M4.open_m4(file_path)
    latitudes = np.linspace(lat_lon_data.start_lat, lat_lon_data.end_lat, lat_lon_data.lat_count)
    longitudes = np.linspace(lat_lon_data.start_lon, lat_lon_data.end_lon, lat_lon_data.lon_count)
    if lev != "":
        xr_data = xr.DataArray([[[[lat_lon_data.data * scale]]]],
                               coords=[[model_name.replace("_", "-")], [report_time], [cst], [int(lev)], latitudes,
                                       longitudes],
                               dims=["member", "time", "dtime", "level", "lat", "lon"])
    else:
        xr_data = xr.DataArray([[[lat_lon_data.data * scale]]],
                               coords=[[model_name.replace("_", "-")], [report_time], [cst], latitudes, longitudes],
                               dims=["member", "time", "dtime", "lat", "lon"])

    return xr_data


def plot_wind_speed(argv, is_overwrite):

    model_name = argv[0]
    report_time = argv[1]
    var = argv[2]
    for lev in LEV:
        for cst in range(0, 123, 3):
            u_data = get_org_data(model_name, report_time, cst, "u", lev)
            v_data = get_org_data(model_name, report_time, cst, "v", lev)
            try:
                if lev == 100:
                    gh_data_100 = get_org_data(model_name, report_time, cst, "gh", 100)
                    pwp = PlotHgtWindProd(model_name, gh_data_100, u_data, v_data)
                elif lev == 200:
                    gh_data_200 = get_org_data(model_name, report_time, cst, "gh", 200)
                    pwp = PlotHgtWindProd(model_name, gh_data_200, u_data, v_data)
                else:
                    gh_data = get_org_data(model_name, report_time, cst, "gh", "500")
                    pwp = PlotHgtWindProd(model_name, gh_data, u_data, v_data)
                for idx in range(len(REGION)):
                    region_name, map_extent = REGION_NAME[idx], REGION[idx]
                    pwp.plot_hgt_wind_speed(report_time, cst, var, region_name, map_extent, lev, is_overwrite=is_overwrite)
            except BaseException:
                continue

def plot_wind(argv, overW):
    model_name = argv[0]
    report_time = argv[1]
    var = argv[2]
    for cst in range(0, 123, 3):
        try:
            gh_data = get_org_data(model_name, report_time, cst, "gh", "500")
            if var == 'gh500_wind500_t':
                u500_data = get_org_data(model_name, report_time, cst, "u", "500")
                v500_data = get_org_data(model_name, report_time, cst, "v", "500")
                pwp = PlotHgtWindProd(model_name, gh_data, u500_data, v500_data)
                t500_data = get_org_data(model_name, report_time, cst, "t", "500")
                for idx in range(len(REGION)):
                    region_name, map_extent = REGION_NAME[idx], REGION[idx]
                    pwp.plot_hgt_wind_t(t500_data, report_time, cst, var, region_name, map_extent, '',
                                         np.arange(-60, 8, 4), cmap='gist_earth', is_overwrite=overW)

            elif var == 'gh500_wind700_q':
                u700_data = get_org_data(model_name, report_time, cst, "u", "700")
                v700_data = get_org_data(model_name, report_time, cst, "v", "700")
                q850_data = get_org_data(model_name, report_time, cst, "q", "850", scale=10)
                pwp = PlotHgtWindProd(model_name, gh_data, u700_data, v700_data)
                for idx in range(len(REGION)):
                    if q850_data is not None:
                        region_name, map_extent = REGION_NAME[idx], REGION[idx]
                        pwp.plot_hgt_wind_spfh(q850_data, report_time, cst, "gh500_wind700_q", region_name,
                                                map_extent, "", is_overwrite=overW)
            else:
                u_data = get_org_data(model_name, report_time, cst, "u", "850")
                v_data = get_org_data(model_name, report_time, cst, "v", "850")
                pwp = PlotHgtWindProd(model_name, gh_data, u_data, v_data)
                if var == 'gh500_wind850_kindex':
                    k_data = get_org_data(model_name, report_time, cst, "k", "")
                    for idx in range(len(REGION)):
                        region_name, map_extent = REGION_NAME[idx], REGION[idx]
                        pwp.plot_hgt_wind_k(k_data, report_time, cst, var, region_name, map_extent, "", is_overwrite=overW)
                if var == 'gh500_wind850_cth':
                    ct_data = get_org_data(model_name, report_time, cst, "ct", "")
                    for idx in range(len(REGION)):
                        region_name, map_extent = REGION_NAME[idx], REGION[idx]
                        pwp.plot_hgt_wind_ct(ct_data, report_time, cst, var, region_name, map_extent, "", is_overwrite=overW)
                if var == 'gh500_wind850_hpbl':
                    hpbl_data = get_org_data(model_name, report_time, cst, "hpbl", "")
                    for idx in range(len(REGION)):
                        region_name, map_extent = REGION_NAME[idx], REGION[idx]
                        pwp.plot_hgt_wind_hpbl(hpbl_data, report_time, cst, var, region_name, map_extent, "", is_overwrite=overW)
                if var == 'gh500_wind850_rcr':
                    rcr_data = get_org_data(model_name, report_time, cst, "radar", "")
                    for idx in range(len(REGION)):
                        region_name, map_extent = REGION_NAME[idx], REGION[idx]
                        pwp.plot_hgt_wind_rcr(rcr_data, report_time, cst, var, region_name, map_extent, "", is_overwrite=overW)
                if var == 'rcr':
                    rcr_data = get_org_data(model_name, report_time, cst, "radar", "")
                    for idx in range(len(REGION)):
                        region_name, map_extent = REGION_NAME[idx], REGION[idx]
                        pwp.plot_rcr(rcr_data, report_time, cst, var, region_name, map_extent, "", is_overwrite=overW)
                elif var == 'gh500_wind850_msl':
                    msl_data = get_org_data(model_name, report_time, cst, "msl", "")
                    for idx in range(len(REGION)):
                        region_name, map_extent = REGION_NAME[idx], REGION[idx]
                        pwp.plot_hgt_wind_msl(msl_data, report_time, cst, var, region_name, map_extent, "", is_overwrite=overW)
                elif var == 'gh500_wind850_tcwv':
                    tcwv_data = get_org_data(model_name, report_time, cst, "tcwv", "")
                    for idx in range(len(REGION)):
                        region_name, map_extent = REGION_NAME[idx], REGION[idx]
                        pwp.plot_hgt_wind_tcwv(tcwv_data, report_time, cst, var, region_name, map_extent, "", is_overwrite=overW)
                elif var == 'gh500_wind850_cape':
                    cape_data = get_org_data(model_name, report_time, cst, "cape", "")
                    for idx in range(len(REGION)):
                        region_name, map_extent = REGION_NAME[idx], REGION[idx]
                        pwp.plot_hgt_wind_cape(cape_data, report_time, cst, var, region_name, map_extent, "", is_overwrite=overW)
                elif var == 'gh500_wind850_t':
                    t_data = get_org_data(model_name, report_time, cst, "t", "850")
                    for idx in range(len(REGION)):
                        region_name, map_extent = REGION_NAME[idx], REGION[idx]
                        pwp.plot_hgt_wind_t(t_data, report_time, cst, var, region_name, map_extent, '',
                                            np.arange(-32, 34, 4), cmap='guide/cs36', is_overwrite=overW)
                elif var == 'gh500_wind850_r':
                    for lev in LEV:
                        rh_data = get_org_data(model_name, report_time, cst, "r", lev)
                        for idx in range(len(REGION)):
                            region_name, map_extent = REGION_NAME[idx], REGION[idx]
                            pwp.plot_hgt_wind_rh(rh_data, report_time, cst, var, region_name, map_extent, lev, is_overwrite=overW)
                elif var == 'gh500_wind850_q':
                    for lev in LEV:
                        q_data = get_org_data(model_name, report_time, cst, "q", lev, scale=10)
                        for idx in range(len(REGION)):
                            region_name, map_extent = REGION_NAME[idx], REGION[idx]
                            pwp.plot_hgt_wind_spfh(q_data, report_time, cst, var, region_name, map_extent, lev, is_overwrite=overW)
                elif var == 'gh500_wind850_wvfl':
                    for lev in LEV:
                        q_data = get_org_data(model_name, report_time, cst, "q", lev, scale=10)
                        for idx in range(len(REGION)):
                            region_name, map_extent = REGION_NAME[idx], REGION[idx]
                            pwp.plot_hgt_wind_wvfl(q_data, report_time, cst, var, region_name, map_extent, lev, is_overwrite=overW)
                elif var == 'gh500_wind850_wvfldiv':
                    for lev in LEV:
                        q_data = get_org_data(model_name, report_time, cst, "q", lev, scale=10)
                        for idx in range(len(REGION)):
                            region_name, map_extent = REGION_NAME[idx], REGION[idx]
                            pwp.plot_hgt_wind_wvfldiv(q_data, report_time, cst, var, region_name, map_extent, lev, is_overwrite=overW)
        except:
            continue