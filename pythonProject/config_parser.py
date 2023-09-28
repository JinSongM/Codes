# -- coding: utf-8 --
# @Time : 2023/5/17 17:28
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : config_parser.py
# @Software: PyCharm
import meteva.base as meb
#目标文件目录
path_C3E = r'/CMADAAS/ORIG-DATA/NAFP/ECMWF/ENS/%Y/%Y%m%d/W_NAFP_C_ECMF_([0-9]{14})_P_C3E([0-9]{8})([0-9]{7})01.bz2'
path_C1D = r'/CMADAAS/DATA/NAFP/ECMF/C1D/%Y/%Y%m%d/ECMFC1D_PRTY_1_%Y%m%d%H_GLB_1_2.grib2'
path_D1D = r'/CMADAAS/DATA/NAFP/ECMF/D1D/%Y/%Y%m%d/ECMFD1D_CAPE_1_%Y%m%d%H_GLB_1.grib1'
station_file = './xz_all_11277.m3'
#文件保存目录
# save_PRTY_C3E = r'D:/data/cpvs/Download/XT/result/FST_NAFP/paser_res/C3E/PRTY/%Y/%Y%m%d/%Y%m%d%H_{pnum:03d}.{cst:03d}'
# save_PRTY_C1D = r'D:/data/cpvs/Download/XT/result/FST_NAFP/paser_res/C1D/PRTY/%Y/%Y%m%d/%Y%m%d%H.{cst:03d}'
# land_obs = r'D:/data/cpvs/Download/XT/data/obs/{rp_T:%Y}/{rp_T:%Y%m%d}/{rp_T:%Y%m%d%H}.m3'

save_PRTY_C3E = r'/share/DATASOURCE/PRTY/data/C3E/%Y/%Y%m%d/%Y%m%d%H_{pnum:03d}.{cst:03d}'
save_PRTY_C1D = r'/share/DATASOURCE/PRTY/data/C1D/%Y/%Y%m%d/%Y%m%d%H.{cst:03d}'
save_PRTY_D1D = r'/share/DATASOURCE/CAPE/data/D1D/%Y/%Y%m%d/%Y%m%d%H.{cst:03d}'
land_obs = r'/share/DATASOURCE/PRTY/data/OBS/{rp_T:%Y}/{rp_T:%Y%m%d}/{rp_T:%Y%m%d%H}.m3'

filters_PTYPE = {'shortName':'ptype'}
grid_w = meb.grid([70., 140., 0.25], [10., 60., 0.25])
outer_value = None

dataCode = 'SURF_CHN_MUL_HOR'
element = 'WEP_Now'
userID = 'NMC_GUOYUNQIAN'
pwd = '19871013Guo!'
# userID = 'NMC_XIONG1'
# pwd = 'Xiong111111#'
cmadaas_url = r'http://10.40.17.54/music-ws/api?'