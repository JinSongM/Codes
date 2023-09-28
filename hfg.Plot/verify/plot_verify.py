import os.path

from plot.plot_map_verify import DrawImages
from plot.colors_verify import COLORS_DICT, CONTOUR_DICT
from .config import *
from utils.calc import *
from utils import MICAPS4 as M4

REGION_NAME = ["CHN", "NE", "HB", "HHJH", "JNHN", "XN"]
REGION = [
    [70, 150, 10, 60, 10, 5],
    [110, 138, 35, 57, 5, 5],
    [105, 125, 30, 47, 5, 5],
    [104, 125, 26, 41, 5, 5],
    [104, 125, 16, 33, 5, 5],
    [92, 115, 20, 35, 5, 5]
]
LEV = [1000, 200, 300, 400, 500, 600, 700, 800, 850, 900, 925, 950, 975]


def get_org_data(model_name, report_time, cst, element, lev):
    print(model_name)
    file_path = MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element=element, lev=lev)
    print(file_path)
    if not os.path.exists(file_path):
        return None
    return M4.open_m4(file_path)


def get_drw(idx, report_time, cst_hour, title):
    extent = np.array(REGION[idx])
    drw = DrawImages(extent=extent[0:4], y_scale=extent[5], x_scale=extent[4])
    if idx == 0:
        drw.add_one_or_multi_province(ocean_color="#ffffff", sub_offset_y=-0.02)
    else:
        drw.add_one_or_multi_province(ocean_color="#ffffff", add_sub_nine_dashed=False)
    left = "{:%Y-%m-%d %H}:00 +{:03d}H".format(report_time, cst_hour)
    right = "CST:{:%Y-%m-%d %H}:00".format(report_time, cst_hour)
    drw.set_left_and_right_text_and_title(title, left, right)
    return drw


def __plot_contourf(drw, lat_lon_data, contourf_key):
    if lat_lon_data is None:
        return
    cfg = COLORS_DICT[contourf_key]

    lons = np.linspace(lat_lon_data.start_lon, lat_lon_data.end_lon, lat_lon_data.lon_count)
    lats = np.linspace(lat_lon_data.start_lat, lat_lon_data.end_lat, lat_lon_data.lat_count)

    drw.add_contourf(lons, lats, lat_lon_data.data, cfg["levels"], cfg["colors"], add_color_bar=False)
    drw.add_color_bar(cfg["colors"], cfg["levels"])


def __plot_contour(drw: DrawImages, lat_lon_data, contour_key):
    if lat_lon_data is None:
        return
    cfg = CONTOUR_DICT[contour_key]
    lons = np.linspace(lat_lon_data.start_lon, lat_lon_data.end_lon, lat_lon_data.lon_count)
    lats = np.linspace(lat_lon_data.start_lat, lat_lon_data.end_lat, lat_lon_data.lat_count)
    drw.add_contour(lons, lats, lat_lon_data.data, levels=cfg["levels"], colors=cfg["colors"])


def __plot_wind_bar(drw: DrawImages, u_lat_lon_data, v_lat_lon_data):
    lons = np.linspace(u_lat_lon_data.start_lon, u_lat_lon_data.end_lon, u_lat_lon_data.lon_count)
    lats = np.linspace(u_lat_lon_data.start_lat, u_lat_lon_data.end_lat, u_lat_lon_data.lat_count)
    drw.add_wind_bar(lons, lats, u_lat_lon_data.data, v_lat_lon_data.data, barb_color="black")


def __plot_save_fig(drw: DrawImages, model_name, report_time, cst, out_name, region, lev=""):
    file_out = MODEL_SAVE_OUT.format(model=model_name, report_time=report_time, cst=cst, out_name=out_name,
                                     region=region, lev=lev)
    drw.save_fig(file_out)


def plot_gh500_msl(model_name, report_time, cst_hour):
    """
    :param model_name:模式名
    :param report_time:起报时间
    :param cst_hour:预报时效
    :return:
    """
    out_name = "msl_gh500"
    file_out = MODEL_SAVE_OUT.format(model=model_name, report_time=report_time, cst=cst_hour, out_name=out_name,
                                     region="CHN", lev="")
    if os.path.exists(file_out):
        return
    gh_lat_lon_data = get_org_data(model_name, report_time, cst_hour, "gh", "500")
    msl_lat_lon_data = get_org_data(model_name, report_time, cst_hour, "msl", "")
    for idx in range(len(REGION_NAME)):
        drw = get_drw(idx, report_time, cst_hour, "{} 500hPa位势高度和海平面气压场".format(model_name))
        __plot_contourf(drw, msl_lat_lon_data, "msl")

        __plot_contour(drw, gh_lat_lon_data, "gh_500")
        __plot_save_fig(drw, model_name, report_time, cst_hour, out_name, REGION_NAME[idx])


def plot_gh500_wind(model_name, report_time, cst_hour):
    """
        切换风场
    :param model_name:
    :param report_time:
    :param cst_hour:
    :return:
    """
    print(model_name)
    out_name = "wind_gh500"
    gh_lat_lon_data = get_org_data(model_name, report_time, cst_hour, "gh", "500")
    for lev in LEV:
        file_out = MODEL_SAVE_OUT.format(model=model_name, report_time=report_time, cst=cst_hour, out_name=out_name,
                                         region="CHN", lev=lev)
        if os.path.exists(file_out):
            continue

        u_lat_lon_data = get_org_data(model_name, report_time, cst_hour, "u", str(lev))
        v_lat_lon_data = get_org_data(model_name, report_time, cst_hour, "v", str(lev))
        wind_dir, wind_speed = calc_wind_dir_and_wind_speed(u_lat_lon_data.data, v_lat_lon_data.data)
        for idx in range(len(REGION_NAME)):
            drw = get_drw(idx, report_time, cst_hour, "500hPa位势高度和{}hPa风场".format(lev))
            __plot_wind_bar(drw, u_lat_lon_data, v_lat_lon_data)
            u_lat_lon_data.data = wind_speed
            __plot_contourf(drw, u_lat_lon_data, "wind_speed")
            __plot_contour(drw, gh_lat_lon_data, "gh_500")
            __plot_save_fig(drw, model_name, report_time, cst_hour, out_name, REGION_NAME[idx], lev)


def plot(model_name, report_time, cst_hour):
    plot_gh500_wind(model_name, report_time, cst_hour)
    plot_gh500_msl(model_name, report_time, cst_hour)
