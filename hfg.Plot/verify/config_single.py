import numpy as np

MODEL_ROOT = "/data/cpvs/DataBase/MOD/{model}/{element}/{lev}/{report_time:%Y}/{report_time:%Y%m%d%H}/" \
             "{report_time:%Y%m%d%H}.{cst:03d}"

MODEL_SAVE_OUT = "/data/cpvs/Product/synoptic/{model}/{report_time:%Y%m%d%H}/{out_name}/{lev}/" \
                 "{region}_{report_time:%Y%m%d%H}.{cst:03d}.png"

MODEL_ROOT_CLDAS = "/cpvs/mnt/205/data/model_cldas/CLDAS/{element}/2M_ABOVE_GROUND/{lev}/{report_time:%Y}/{report_time:%Y%m%d}/" \
                   "{report_time:%y%m%d}{cst:02d}.000"

MODEL_ROOT_CLDAS_TP = "/cpvs/mnt/205/data/model/CLDAS/RAIN24_TRI_DATA_SOURCE/{lev}/{report_time:%Y}/{report_time:%Y%m%d}/" \
                      "{report_time:%y%m%d%H}.000"

MODEL_ROOT_CLDAS_TP_1h = "/cpvs/mnt/205/data/model_cldas/CLDAS/RAIN01_TRI_DATA_SOURCE/{lev}/{report_time:%Y}/{report_time:%Y%m%d}/" \
                         "{report_time:%y%m%d}{cst:02d}.000"

MODEL_SAVE_OUT_CLDAS = "/data/cpvs/Product/synoptic/{model}/{report_time:%Y%m%d}/{out_name}/{lev}/" \
                       "{region}_{report_time:%Y%m%d}{cst:02d}{add}.png"

STATION_PATH = "/data/cpvs/DownLoad/OBS/SURF/{obs_t:%Y}/{obs_t:%Y%m%d}/rawsh1_{obs_t:%Y%m%d%H}.dat"
STATION_out_PATH = "/data/cpvs/Product/synoptic/{model}/{report_time:%Y%m%d}/{out_name}/{lev}/" \
                       "{region}_{report_time:%Y%m%d}{cst:02d}{add}.png"
STATION_SAVE_OUT = "/data/cpvs/Product/synoptic/{model}/{report_time:%Y%m%d}/{out_name}/{lev}/" \
                 "{region}_{report_time:%Y%m%d%H}.{cst:03d}.png"

t2m_title = "[{}]温度（℃）"
t2m_var = '温度（℃）'
t2m_units = 'degC'
cmap_tem = 'ncl/ncl_default'
t2m_colorbar = [i for i in range(-36, 40, 4)]

t2m_min_title = "[{}]24h最低温（℃）"
t2m_min_var = '24h最低温（℃）'
t2m_max_title = "[{}]24h最高温（℃）"
t2m_max_var = '24h最高温（℃）'
t2m_min_units = 'degC'
t2m_min_color = [
    [120, 4, 113],
    [10, 67, 170],
    [24, 89, 183],
    [32, 115, 219],
    [65, 159, 233],
    [102, 213, 255],
    [152, 226, 239],
    [189, 248, 254],
    [243, 254, 255],
    [220, 255, 213],
    [192, 254, 179],
    [180, 255, 130],
    [251, 253, 143],
    [254, 242, 192],
    [254, 223, 176],
    [255, 174, 118],
    [251, 135, 138],
    [254, 86, 0],
    [255, 0, 0],
    [200, 0, 10],
    [143, 8, 20]
]
t2m_min_colorbar = [i for i in range(-32, 36, 4)]+[35]+[37, 40]

t2m_high_title = "[{}]高温（℃）"
t2m_high_colorbar = [35, 37, 40]
t2m_high_var = '温度（℃）'
t2m_high_units = 'degC'
cmap_tem_high = ['#FFFFFF', '#FFEE99', '#FFAA33', '#FF0000']

tem_change_title = "[{}]变温（℃）"
tem_change_var = '变温（℃）'
tem_change_units = 'degC'
tem_change_colorbar = [-18,-16,-14,-12,-10,-8,-6,-4,-2,-1,1,2,4,6,8,10]
tem_change_color = [
    [64,0,0],
    [125,2,3],
    [75,0,120],
    [165,0,231],
    [0,0,255],
    [0,75,170],
    [0,110,255],
    [115,180,215],
    [150,220,240],
    [190,255,231],
    [240,255,200],
    [255,225,130],
    [250,145,0],
    [240,95,5],
    [230,0,0],
    [190,0,50],
    [140,0,30],
]
# tem_change_colorbar = [i for i in range(-24, 24, 2)]
# tem_change_color = [
#     [44,12,81],
#     [79,30,179],
#     [2,12,100],
#     [17,49,139],
#     [38,87,179],
#     [59,126,219],
#     [97,150,224],
#     [135,175,229],
#     [154,196,220],
#     [152,214,196],
#     [151,232,173],
#     [215,222,126],
#     [244,217,99],
#     [247,180,45],
#     [241,147,3],
#     [239,117,17],
#     [231,75,26],
#     [208,36,14],
#     [169,2,16],
#     [122,24,24],
#     [72,8,8],
#     [34,2,2]
# ]

exwind_title = "[{}]24h极大风"
exwind_var = '24h极大风'
exwind_units = 'm/s'
wind_title = "[{}]1h阵风"
wind_var = '1h阵风'
exwind_color = [
    [255, 255, 255],
    [0, 208, 255],
    [0, 128, 246],
    [0, 25, 255],
    [255, 207, 0],
    [255, 143, 0],
    [255, 90, 90],
    [255, 0, 0],
    [204, 0, 0],
    [153, 0, 0],
    [106, 48, 167],
    [86, 42, 134],
    [63,33, 94],
]
exwind_colorbar = [i for i in range(5, 18, 1)]

rh_title = "[{}]相对湿度（%）"
rh_var = '相对湿度（%）'
rh_units = 'percent'
rh_colorbar = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95]
cmap_r = 'PRGn'
r_color = [
    [124, 49, 139],
    [141, 82, 156],
    [153, 112, 172],
    [168, 131, 183],
    [189, 158, 202],
    [204, 177, 215],
    [218, 195, 223],
    [231, 213, 232],
    [238, 228, 240],
    [243, 238, 242],
    [238, 244, 237],
    [227, 241, 223],
    [212, 238, 208],
    [194, 231, 186],
    [173, 221, 169],
    [147, 209, 144],
    [110, 187, 115],
    [80, 169, 91],
    [55, 148, 74],
    [26, 126, 54]
]

tp_title = "[{}]降水（mm）"
tp_var = '降水（mm）'
tp_units = 'mm'
tp_colorbar = [0, 0.1, 10, 25, 50, 100, 250]
tp_colorbar2 = [0, 0.1, 2.5, 5, 10, 25, 50, 100]

tp_color = [
    [255, 255, 255],
    [167, 242, 143],
    [54, 187, 68],
    [100, 184, 253],
    [0, 0, 254],
    [255, 0, 255],
    [130, 0, 62]
]
tp_hour_color = [
    [255, 255, 255],
    [167, 242, 143],
    [54, 187, 68],
    [100, 230, 253],
    [100, 184, 253],
    [0, 0, 254],
    [255, 0, 255],
    [130, 0, 62]
]

cp_title = "[{}]对流性降水（mm）"
cp_var = '对流性降水（mm）'
lsp_title = "[{}]大尺度降水（mm）"
lsp_var = '对大尺度降水（mm）'

sd_title = "[{}]24h降雪（mm）"
sd_var = '24h降雪（mm）'
sd_hour_title = "[{}]{}h降雪（mm）"
sd_hour_var = '{}h降雪（mm）'
sd_units = 'mm'
sd_colorbar = [0.1, 2.5, 5, 10, 20, 30]
sd_hour_colorbar = [0.01, 0.5, 1, 2.5, 5, 8, 10, 12, 15]
cmap_sd = 'ncl/MPL_Greys'
cmap_sd_hour = 'met/snow_nws'
windspeend_name = 'wind'


tp_df_title = "[{}]24h降水差（mm）"
tp_hour_df_title = "[{}]降水差（mm）"
tp_var_df = '降水差（mm）'
cmap_tp_hour_df = 'RdBu_r'
tp_colorbar_df = [-10, -5, -2.5, -1, 0, 1, 2.5, 5, 10]

tem_df_title = "[{}]温度差（℃）"
tem_var_df = "温度差（℃）"
cmap_tem_df = 'RdBu_r'
tem_colorbar_df = [-10, -5, -2, -1, 0, 1, 2, 5, 10]

temC_df_title = "[{}]变温差（℃）"
temC_var_df = "变温差（℃）"
cmap_temC_df = 'RdBu_r'
temC_colorbar_df = [-10, -5, -2, -1, 0, 1, 2, 5, 10]

tem_max_df_title = "[{}]高温差（℃）"
tem_max_var_df = "高温差（℃）"
cmap_tem_max_df = 'RdBu_r'
tem_max_colorbar_df = [-5, -3, -2, -1, 0, 1, 2, 3, 5]

rh_df_title = "[{}]相对湿度差（%）"
rh_var_df = "相对湿度差（%）"
cmap_rh_df = 'PRGn_r'
rh_colorbar_df = [-10, -5, -2, -1, 0, 1, 2, 5, 10]

tp_sd_title = "[{}]24h雨雪分布"
tp_sd_var = '24h雨雪分布'
cmap_tp_sd = ['#ffffff', '#97E8AD', '#FACC4F']

cmap_hpbl = [
    [93,93,255],
    [144,144,255],
    [169,169,255],
    [194,194,255],
    [220,220,255],
    [225,255,225],
    [195,255,195],
    [159,255,159],
    [115,255,115],
    [72,255,72],
    [0,255,0]
]