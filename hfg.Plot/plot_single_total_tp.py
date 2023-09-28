# -- coding: utf-8 --
# @Time : 2023/3/24 13:42
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : plot_single_total_tp.py
# @Software: PyCharm
import sys, os
import meteva.base as meb
from datetime import datetime, timedelta
from verify.config_single import *
from utils import MICAPS4 as M4
from metdig.graphics import draw_compose
from verify.plot_ms import metdig_single_plot
from verify.plot_model_single import horizontal_pallete_test

tp_color_5days = [
    [255, 255, 255],
    [167, 242, 143],
    [54, 187, 68],
    [100, 184, 253],
    [0, 0, 255],
    [255, 0, 255],
    [130, 0, 62],
    [253, 167, 17],
    [245, 110, 10],
    [230, 0, 10],
    [150, 0, 15]
]
REGION = [
    [60, 150, 0, 70],
    [70, 140, 10, 60],
    [110, 138, 35, 57],
    [105, 125, 30, 47],
    [104, 125, 26, 41],
    [104, 125, 16, 33],
    [92, 115, 20, 35],
    [73, 123, 37, 50]
]
path_GFS = './verify/mask_NH25.dat'
path_Model = './verify/mask_0p25.dat'
path_CLDAS = './verify/mask_005.dat'
REGION_NAME = ["EA", "CHN", "NE", "HB", "HHJH", "JNHN", "XN", "NW"]
tp_colorbar_5days = [0.1, 10, 25, 50, 100, 250, 400, 600, 1000, 1500]

# 掩膜数据
def read_mask():
    if os.path.exists(path_Model):
        grd_mask = meb.read_griddata_from_micaps4(path_Model)
    else:
        grd_mask = None
    if os.path.exists(path_GFS):
        GFS_mask = meb.read_griddata_from_micaps4(path_GFS)
    else:
        GFS_mask = None
    if os.path.exists(path_CLDAS):
        grd_mask_cldas = meb.read_griddata_from_micaps4(path_CLDAS)
    else:
        grd_mask_cldas = None

    return GFS_mask.data[0][0][0][0], grd_mask.data[0][0][0][0], grd_mask_cldas[0][0][0][0]
GFS_mask, mask_array, mask_array_cldas = read_mask()


def CLDAS_total_tp(Infile_list, step, region):
    File_Name = os.path.split(Infile_list[0])[1]
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])
    try:
        file_dir, file_name = os.path.split(Infile_list[0])
        father_file_dir = os.path.dirname(file_dir)
        lat_lon, freq = M4.open_m4(Infile_list[0]), 0
        lat_lon_data = lat_lon.data
        lat_lon_data[lat_lon_data == 9999] = np.nan
        for i in range(1, step):
            father_file_dir_name = (datetime.strptime(str(os.path.splitext(file_name)[0]), '%y%m%d%H') + timedelta(
                days=i)).strftime('%Y%m%d')
            father_file_name = (datetime.strptime(str(os.path.splitext(file_name)[0]), '%y%m%d%H') + timedelta(
                days=i)).strftime('%y%m%d%H') + file_name[-4:]
            father_file = os.path.join(father_file_dir, father_file_dir_name, father_file_name)
            if os.path.exists(father_file):
                data_tmp = M4.open_m4(father_file).data
                data_tmp[data_tmp == 9999] = np.nan
                lat_lon_data += data_tmp
                freq += 1
            else:
                freq += 0
            lat_lon_data[mask_array_cldas == 0] = np.nan

        if freq == step - 1:
            region_name, map_extent = region, tuple(REGION[REGION_NAME.index(region)])
            file_time_end = datetime.strptime(str(os.path.splitext(file_name)[0]), '%y%m%d%H') + timedelta(days=step-1)
            file_time_start = datetime.strptime(str(os.path.splitext(file_name)[0]), '%y%m%d%H') - timedelta(days=1)
            obs_time_dc = '起始时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(file_time_start)
            fst_time_dc = '结束时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(file_time_end)
            forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '{}天累计降水'.format(step)

            if region_name == 'CHN' or region_name == 'JNHN':
                add_scs_value = True
            else:
                add_scs_value = False
            fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info, add_south_china_sea=add_scs_value)
            png_path = os.path.join(Infile_list[1], region_name + '_20' + File_Name + ".png")
            if os.path.exists(png_path):
                os.remove(png_path)
            drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info, fig=fig,
                                                  ax=ax, output_dir=Infile_list[1], add_city=False,
                                                  is_clean_plt=True, map_extent=map_extent, add_tag=False,
                                                  png_name=region_name + '_20' + File_Name + ".png")
            drw.ax.tick_params(labelsize=16)
            metdig_single_plot(Infile_list, lat_lon, drw, lat_lon_data, Infile_list[6])
            drw.save()
    except:
        print(File_Name)


def model_total_tp(Infile_list, step, region):
    File_Name = os.path.split(Infile_list[0])[1]
    if not os.path.exists(Infile_list[1]):
        os.makedirs(Infile_list[1])
    try:
        if os.path.exists(Infile_list[0]):
            file_dir, file_name = os.path.split(Infile_list[0])
            if int(file_name[-3:]) >= step and int(file_name[-3:]) % step == 0:
                file_name_24 = '%.3f' % (float(file_name) - step / 1000)
                file_dir_24 = os.path.join(file_dir, str(file_name_24))
                if os.path.exists(file_dir_24):
                    lat_lon_data = M4.open_m4_org(Infile_list[0])
                    if "NCEP" in Infile_list[1]:
                        if File_Name.split('.')[1] == '024':
                            lat_lon_data_24_data = np.zeros_like(lat_lon_data.data)
                        else:
                            lat_lon_data_24_data = M4.open_m4_org(file_dir_24).data
                    else:
                        lat_lon_data_24_data = M4.open_m4_org(file_dir_24).data
                    if "NCEP" in Infile_list[1]:
                        lat_lon_data_obs = (lat_lon_data.data - lat_lon_data_24_data) / 1000
                    else:
                        lat_lon_data_obs = lat_lon_data.data - lat_lon_data_24_data

                    if "CMA_GFS" in Infile_list[1]:
                        mask = GFS_mask
                    else:
                        mask = mask_array
                    lat_lon_data_obs[mask == 0] = np.nan
                    region_name, map_extent = region, tuple(REGION[REGION_NAME.index(region)])
                    png_path = Infile_list[1] + region_name + '_' + File_Name + ".png"
                    if os.path.exists(png_path):
                        os.remove(png_path)
                    obs_time, step_time = os.path.basename(Infile_list[0]).split('.')
                    if step_time != '000':
                        OBS_time = datetime.strptime(obs_time, '%Y%m%d%H')
                        FST_time = OBS_time + timedelta(hours=int(step_time))
                        obs_time_dc = '起始时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(OBS_time)
                        fst_time_dc = '结束时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(FST_time)
                        forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '{}天累计降水'.format(
                            int(int(step_time)/24))
                        if region_name == 'CHN' or region_name == 'JNHN':
                            add_scs_value = True
                        else:
                            add_scs_value = False
                        fig, ax = horizontal_pallete_test(map_extent=map_extent, forcast_info=forcast_info,
                                                          add_south_china_sea=add_scs_value)
                        png_name = region_name + '_' + File_Name + ".png"
                        drw = draw_compose.horizontal_compose(title=Infile_list[2], description=forcast_info,
                                                              add_tag=False,
                                                              output_dir=Infile_list[1], add_city=False,
                                                              fig=fig, ax=ax,
                                                              is_clean_plt=True, map_extent=map_extent,
                                                              png_name=png_name)
                        drw.ax.tick_params(labelsize=16)
                        metdig_single_plot(Infile_list, lat_lon_data, drw, lat_lon_data_obs, Infile_list[6])
                        drw.save()
    except:
        print(File_Name)


def process_plot(argv):
    model_name = argv[1]
    report_time = datetime.strptime(argv[2], '%Y%m%d%H')
    cst = int(argv[3]) * 24
    region = argv[4]

    if int(argv[3]) < 4:
        cmap_tp = ['#{:02x}{:02x}{:02x}'.format(*tuple(i)) for i in tp_color]
        tp_colorbar_ticks = tp_colorbar
    else:
        cmap_tp = ['#{:02x}{:02x}{:02x}'.format(*tuple(i)) for i in tp_color_5days]
        tp_colorbar_ticks = tp_colorbar_5days

    CLDAS_tp = [
        MODEL_ROOT_CLDAS_TP.format(model='CLDAS', report_time=report_time+timedelta(days=1), element='tp', lev=''),
        os.path.dirname(MODEL_SAVE_OUT_CLDAS).format(model='CLDAS', report_time=report_time,
                                                     out_name='total_pre', lev=''),
        tp_title.format(model_name), tp_var, tp_units, tp_colorbar_ticks, cmap_tp
    ]
    file_tp = [MODEL_ROOT.format(model=model_name, report_time=report_time, cst=cst, element='tp', lev=''),
               os.path.dirname(MODEL_SAVE_OUT).format(model=model_name, report_time=report_time,
                                                      out_name='total_pre', lev=''),
               tp_title.format(model_name), tp_var, tp_units, tp_colorbar_ticks, cmap_tp
               ]

    # if argv[1] == 'CLDAS':
    #     CLDAS_total_tp(CLDAS_tp, int(argv[3]), region)
    # else:
    #     model_total_tp(file_tp, cst, region)
    CLDAS_total_tp(CLDAS_tp, int(argv[3]), region)
    model_total_tp(file_tp, cst, region)

if __name__ == '__main__':
    #argv：模式名称 %Y%m%d%H 时效 区域名称
    process_plot(sys.argv)