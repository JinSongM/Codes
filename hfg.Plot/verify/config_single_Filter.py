import numpy as np

MODEL_ROOT = "/data/cpvs/DataBase/MOD/{model}/{element}/{lev}/{report_time:%Y}/{report_time:%Y%m%d%H}/" \
             "{report_time:%Y%m%d%H}.{cst:03d}"

MODEL_SAVE_OUT = "/data/cpvs/Product/synoptic/{model}/{report_time:%Y%m%d%H}/{out_name}/Filter/{lev}/" \
                 "{region}_{report_time:%Y%m%d%H}.{cst:03d}.png"

MODEL_ROOT_CLDAS = "/cpvs/mnt/205/data/ANALYSIS/{element}/{lev}/{report_time:%Y%m%d}/" \
                   "{report_time:%Y%m%d}{cst:02d}.000"

MODEL_ROOT_CLDAS_TP = "/cpvs/mnt/205/data/model/CLDAS/RAIN24_TRI_DATA_SOURCE/{lev}/{report_time:%Y}/{report_time:%Y%m%d}/" \
                      "{report_time:%y%m%d%H}.000"

MODEL_ROOT_CLDAS_TP_1h = "/cpvs/mnt/205/data/model_cldas/CLDAS/RAIN01_TRI_DATA_SOURCE/{lev}/{report_time:%Y}/{report_time:%Y%m%d}/" \
                         "{report_time:%y%m%d}{cst:02d}.000"

MODEL_SAVE_OUT_CLDAS = "/data/cpvs/Product/synoptic/{model}/{report_time:%Y%m%d}/{out_name}/Filter/{lev}/" \
                       "{region}_{report_time:%Y%m%d}{cst:02d}{add}.png"

t2m_title = "[{}]温度（℃）"
t2m_var = '温度（℃）'
t2m_units = 'degC'
cmap_tem = 'ncl/ncl_default'
t2m_colorbar = [i for i in range(-36, 40, 4)]

t2m_high_title = "[{}]高温（℃）"
t2m_high_colorbar = [35, 37, 40]
t2m_high_var = '温度（℃）'
t2m_high_units = 'degC'
cmap_tem_high = ['#FFFFFF', '#FFEE99', '#FFAA33', '#FF0000']

tem_change_title = "[{}]变温（℃）"
tem_change_var = '变温（℃）'
tem_change_units = 'degC'
tem_change_colorbar = [i for i in range(-24, 24, 2)]
tem_change_color = [
    [44,12,81],
    [79,30,179],
    [2,12,100],
    [17,49,139],
    [38,87,179],
    [59,126,219],
    [97,150,224],
    [135,175,229],
    [154,196,220],
    [152,214,196],
    [151,232,173],
    [215,222,126],
    [244,217,99],
    [247,180,45],
    [241,147,3],
    [239,117,17],
    [231,75,26],
    [208,36,14],
    [169,2,16],
    [122,24,24],
    [72,8,8],
    [34,2,2]
]

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
sd_units = 'mm'
sd_colorbar = [0.1, 2.5, 5, 10, 20, 30]
cmap_sd = 'ncl/MPL_Greys'
windspeend_name = 'wind'
