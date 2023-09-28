import os.path
import numpy as np
from .config import *
from utils import MICAPS4 as M4
from met_plot.plot_model import PlotHgtWindProd
import xarray as xr

REGION_NAME = ["CHN"]
REGION = [
    [70, 150, 10, 60]
]
# REGION_NAME = ["EA", "CHN", "NE", "HB", "HHJH", "JNHN", "XN", "NW", "NH"]
# REGION = [
#     [60, 150, 0, 70],
#     [70, 150, 10, 60],
#     [110, 138, 35, 57],
#     [105, 125, 30, 47],
#     [104, 125, 26, 41],
#     [104, 125, 16, 33],
#     [92, 115, 20, 35],
#     [73, 123, 37, 50],
#     [0, 240, 0, 90]
# ]
LEV = [850, 1000, 925, 700, 500, 200, 100]


def get_org_data(model_name: str, report_time, cst, element, lev, scale=1):
    if model_name == 'ERA5' or model_name == 'FNL':
        file_path = MODEL_ROOT_OBS.format(model=model_name, report_time=report_time, cst=cst, element=element, lev=lev)
    else:
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


def plot_wind_speed(model_name, report_time, cst, is_overwrite):
    gh_data = get_org_data(model_name, report_time, cst, "gh", "500")
    gh_data_100 = get_org_data(model_name, report_time, cst, "gh", 100)
    gh_data_200 = get_org_data(model_name, report_time, cst, "gh", 200)
    for lev in LEV:
        try:
            u_data = get_org_data(model_name, report_time, cst, "u", lev)
            v_data = get_org_data(model_name, report_time, cst, "v", lev)
            pwp = None
            if lev == 100:
                pwp = PlotHgtWindProd(model_name, gh_data_100, u_data, v_data)
            elif lev == 200:
                pwp = PlotHgtWindProd(model_name, gh_data_200, u_data, v_data)
            else:
                pwp = PlotHgtWindProd(model_name, gh_data, u_data, v_data)

            for idx in range(len(REGION)):
                pwp.plot_hgt_wind_speed(report_time, cst, "gh500_speed", REGION_NAME[idx], REGION[idx], lev, is_overwrite=is_overwrite)
        except Exception as e:
            print(e)
            continue


def plot_wind(model_name, report_time, cst, is_overwrite):
    gh_data = get_org_data(model_name, report_time, cst, "gh", "500")
    u_data = get_org_data(model_name, report_time, cst, "u", "850")
    v_data = get_org_data(model_name, report_time, cst, "v", "850")
    t_data = get_org_data(model_name, report_time, cst, "t", "850")
    rcr_data = get_org_data(model_name, report_time, cst, "radar", "")
    msl_data = get_org_data(model_name, report_time, cst, "msl", "")
    tcwv_data = get_org_data(model_name, report_time, cst, "tcwv", "")
    cape_data = get_org_data(model_name, report_time, cst, "cape", "")
    k_data = get_org_data(model_name, report_time, cst, "k", "")
    hpbl_data = get_org_data(model_name, report_time, cst, "hpbl", "")
    ct_data = get_org_data(model_name, report_time, cst, "ct", "")
    try:
        pwp = PlotHgtWindProd(model_name, gh_data, u_data, v_data)
        for idx in range(len(REGION)):
            if ct_data is not None:
                pwp.plot_hgt_wind_ct(ct_data, report_time, cst, "gh500_wind850_cth",
                                     REGION_NAME[idx], REGION[idx], "", is_overwrite=is_overwrite)
            if hpbl_data is not None:
                pwp.plot_hgt_wind_hpbl(hpbl_data, report_time, cst, "gh500_wind850_hpbl", REGION_NAME[idx], REGION[idx],
                                       "", is_overwrite=is_overwrite)
            if k_data is not None:
                pwp.plot_hgt_wind_k(k_data, report_time, cst, "gh500_wind850_kindex",
                                    REGION_NAME[idx], REGION[idx], "", is_overwrite=is_overwrite)
            if msl_data is not None:
                pwp.plot_hgt_wind_msl(msl_data, report_time, cst, "gh500_wind850_msl", REGION_NAME[idx], REGION[idx],
                                      "", is_overwrite=is_overwrite)
            if tcwv_data is not None:
                pwp.plot_hgt_wind_tcwv(tcwv_data, report_time, cst, "gh500_wind850_tcwv", REGION_NAME[idx], REGION[idx],
                                       "", is_overwrite=is_overwrite)
            if cape_data is not None:
                pwp.plot_hgt_wind_cape(cape_data, report_time, cst, "gh500_wind850_cape", REGION_NAME[idx], REGION[idx],
                                       "", is_overwrite=is_overwrite)
            if rcr_data is not None:
                pwp.plot_hgt_wind_rcr(rcr_data, report_time, cst, "gh500_wind850_rcr", REGION_NAME[idx], REGION[idx],
                                      "", is_overwrite=is_overwrite)
                pwp.plot_rcr(rcr_data, report_time, cst, "rcr", REGION_NAME[idx], REGION[idx], "", is_overwrite=is_overwrite)
            if t_data is not None:
                pwp.plot_hgt_wind_t(t_data, report_time, cst, "gh500_wind850_t", REGION_NAME[idx], REGION[idx], '',
                                    np.arange(-32, 34, 4), cmap=cmap_t_850, is_overwrite=is_overwrite)

        for lev in LEV:
            q_data = get_org_data(model_name, report_time, cst, "q", lev, scale=10)
            rh_data = get_org_data(model_name, report_time, cst, "r", lev)

            for idx in range(len(REGION)):
                if rh_data is not None:
                    pwp.plot_hgt_wind_rh(rh_data, report_time, cst, "gh500_wind850_r", REGION_NAME[idx], REGION[idx],
                                         lev, is_overwrite=is_overwrite)
                if q_data is not None:
                    pwp.plot_hgt_wind_spfh(q_data, report_time, cst, "gh500_wind850_q", REGION_NAME[idx], REGION[idx],
                                           lev, is_overwrite=is_overwrite)
                    pwp.plot_hgt_wind_wvfl(q_data, report_time, cst, "gh500_wind850_wvfl", REGION_NAME[idx],
                                           REGION[idx], lev, is_overwrite=is_overwrite)
                    pwp.plot_hgt_wind_wvfldiv(q_data, report_time, cst, "gh500_wind850_wvfldiv", REGION_NAME[idx],
                                              REGION[idx], lev, is_overwrite=is_overwrite)

        u500_data = get_org_data(model_name, report_time, cst, "u", "500")
        v500_data = get_org_data(model_name, report_time, cst, "v", "500")
        t500_data = get_org_data(model_name, report_time, cst, "t", "500")
        pwp2 = PlotHgtWindProd(model_name, gh_data, u500_data, v500_data)
        for idx in range(len(REGION)):
            if t500_data is not None:
                pwp2.plot_hgt_wind_t(t500_data, report_time, cst, "gh500_wind500_t", REGION_NAME[idx], REGION[idx], '',
                                     np.arange(-60, 8, 4), cmap='gist_earth', is_overwrite=is_overwrite)

        u700_data = get_org_data(model_name, report_time, cst, "u", "700")
        v700_data = get_org_data(model_name, report_time, cst, "v", "700")
        q850_data = get_org_data(model_name, report_time, cst, "q", "850", scale=10)
        pwp3 = PlotHgtWindProd(model_name, gh_data, u700_data, v700_data)
        for idx in range(len(REGION)):
            if q850_data is not None:
                pwp3.plot_hgt_wind_spfh(q850_data, report_time, cst, "gh500_wind700_q", REGION_NAME[idx], REGION[idx],
                                        "", is_overwrite=is_overwrite)
    except Exception as e:
        print(e)