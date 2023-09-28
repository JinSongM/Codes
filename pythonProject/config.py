# -- coding: utf-8 --
# @Time : 2023/5/16 10:36
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : config.py
# @Software: PyCharm

china_shp = r'./shpfile/china_20220325.shp'
worldmap_shp = r'./shpfile/worldmap.shp'
coastline_shp = r'./shpfile/ne_10m_coastline.shp'

# 模式相态概率
# infile_path_c3e = r'D:\data\cpvs\Download\XT\result\FST_NAFP\paser_res\C3E\PRTY\{rp_T:%Y}\{rp_T:%Y%m%d}\{rp_T:%Y%m%d%H}_{ens:03d}.{cst:03d}'
# infile_path_c1d = r'D:\data\cpvs\Download\XT\result\FST_NAFP\paser_res\C1D\PRTY\{rp_T:%Y}\{rp_T:%Y%m%d}\{rp_T:%Y%m%d%H}.{cst:03d}'
#
# c3e_Ppt1 = r'D:\data\cpvs\Download\XT\result\FST_NAFP\typeTP_PP\C3E\PRTY\{rp_T:%Y}\{rp_T:%Y%m%d}\{rp_T:%Y%m%d%H}_{cst:03d}.csv'
# c1d_Ppt2 = r'D:\data\cpvs\Download\XT\result\FST_NAFP\typeTP_PP\C1D\PRTY\{rp_T:%Y}\{rp_T:%Y%m%d}\{rp_T:%Y%m%d%H}_{cst:03d}.csv'
# c3e_pt1 = r'D:\data\cpvs\Download\XT\result\FST_NAFP\typeTP_PP\C3E\PRTY\{rp_T:%Y}\{rp_T:%Y%m%d}\{rp_T:%Y%m%d%H}_{cst:03d}.nc'
# c1d_pt2 = r'D:\data\cpvs\Download\XT\result\FST_NAFP\typeTP_PP\C1D\PRTY\{rp_T:%Y}\{rp_T:%Y%m%d}\{rp_T:%Y%m%d%H}_{cst:03d}.nc'
# c1d_Ppt2_sta = r'D:\data\cpvs\Download\XT\result\FST_NAFP\typeTP_PP\C1D\Ppt2_sta\{rp_T:%Y}\{rp_T:%Y%m%d}\{rp_T:%Y%m%d%H}_{cst:03d}.m3'

infile_path_c3e = r'/share/DATASOURCE/PRTY/data/C3E/{rp_T:%Y}/{rp_T:%Y%m%d}/{rp_T:%Y%m%d%H}_{ens:03d}.{cst:03d}'
infile_path_c1d = r'/share/DATASOURCE/PRTY/data/C1D/{rp_T:%Y}/{rp_T:%Y%m%d}/{rp_T:%Y%m%d%H}.{cst:03d}'

c3e_Ppt1 = r'/share/DATASOURCE/PRTY/typeTP/C3E/{rp_T:%Y}/{rp_T:%Y%m%d}/{rp_T:%Y%m%d%H}_{cst:03d}.csv'
c1d_Ppt2 = r'/share/DATASOURCE/PRTY/typeTP/C1D/{rp_T:%Y}/{rp_T:%Y%m%d}/{rp_T:%Y%m%d%H}_{cst:03d}.csv'
c3e_pt1 = r'/share/DATASOURCE/PRTY/typeTP/C3E/{rp_T:%Y}/{rp_T:%Y%m%d}/{rp_T:%Y%m%d%H}_{cst:03d}.nc'
c1d_pt2 = r'/share/DATASOURCE/PRTY/typeTP/C1D/{rp_T:%Y}/{rp_T:%Y%m%d}/{rp_T:%Y%m%d%H}_{cst:03d}.nc'
c1d_Ppt2_sta = r'/share/DATASOURCE/PRTY/typeTP/C1D_sta/{rp_T:%Y}/{rp_T:%Y%m%d}/{rp_T:%Y%m%d%H}_{cst:03d}.m3'

#模式相态概率
# land_obs6 = r'D:\data\cpvs\Download\XT\result\OBS_LAND\{rp_T:%Y}\{rp_T:%Y%m%d}\{rp_T:%Y%m%d%H}.m3'
# land_obs = r'D:\data\cpvs\Download\XT\data\obs\{rp_T:%Y}\{rp_T:%Y%m%d}\{rp_T:%Y%m%d%H}.m3'
# typePP_out = r'D:\data\cpvs\Download\XT\result\STATIS_HIS\{rp_T:%Y}\{rp_T:%Y%m}\{rp_T:%Y%m}_{HR:02d}_{cst:03d}_{label}.csv'
# NAFP_png = r'D:\data\cpvs\Download\XT\result\IMAGES\{rp_T:%Y}\{rp_T:%Y%m%d}\{model}_{rp_T:%Y%m%d%H}_{cst:03d}_{model_type}.png'
land_obs6 = r'/share/DATASOURCE/PRTY/typeTP/OBS/{rp_T:%Y}/{rp_T:%Y%m%d}/{rp_T:%Y%m%d%H}.m3'
land_obs = r'/share/DATASOURCE/PRTY/data/OBS/{rp_T:%Y}/{rp_T:%Y%m%d}/{rp_T:%Y%m%d%H}.m3'
typePP_out = r'/share/DATASOURCE/PRTY/STATIS_HIS/{rp_T:%Y}/{rp_T:%Y%m}/{rp_T:%Y%m}_{HR:02d}_{cst:03d}_{label}.csv'
NAFP_png = r'/share/DATASOURCE/PRTY/IMAGES/{rp_T:%Y}/{rp_T:%Y%m%d}/{model}_{rp_T:%Y%m%d%H}_{cst:03d}_{model_type}.png'
station_path = r'./xz_all_11277.m3'
fst_h = [i for i in range(0, 75, 3)] + [i for i in range(72, 246, 6)]


step = 10
title_name = ['实况', '无降水', '雨', '雨夹雪', '雪', '冻雨']
cmap_obs = ['#FFFFFF', '#36BB44', '#64B8FD', '#3333FF', '#6633FF', '#CC33CC']
ticks = [0, 1, 2, 3, 4, 9, 10]
cb_ticks = [0.5, 1.5, 2.5, 3.5, 6.5, 9.5]
tick_label = ['无降水', '雨', '雨夹雪', '雪', '冻雨', '缺测']
nafp_rgb = [
    [255, 255, 255],
    [167, 242, 143],
    [54, 187, 68],
    [100, 184, 253],
    [0, 0, 254],
]
cmap_nafp = ['#{:02x}{:02x}{:02x}'.format(*tuple(i)) for i in nafp_rgb]
levels = [0, 0.2, 0.4, 0.6, 0.8, 1]
levels_sta = [0, 1, 3, 5, 6, 7, 8, 9]
cb_levels = [0.5, 2, 4, 5.5, 6.5, 7.5, 8.5]
levels_label = ['无降水', '雨', '冻雨', '干雪', '湿雪', '雨夹雪', '冰粒']
cmap_sta = ['#FFFFFF', '#36BB44', '#6633FF', '#3333FF', '#3383FF', '#64B8FD', '#DC3760']
title_name_hrd = ['实况', '站点相态']