MODEL_ROOT = "/data/cpvs/DataBase/MOD/{model}/{element}/{lev}/{report_time:%Y}/{report_time:%Y%m%d%H}/" \
             "{report_time:%Y%m%d%H}.{cst:03d}"

MODEL_ROOT_OBS = "/data/cpvs/DataBase/OBS/{model}/{element}/{lev}/{report_time:%Y}/{report_time:%Y%m%d%H}/" \
             "{report_time:%Y%m%d%H}.{cst:03d}"

MODEL_SAVE_OUT = "/data/cpvs/Product/synoptic/{model}/{report_time:%Y%m%d%H}/{out_name}/{lev}/" \
                 "{region}_{report_time:%Y%m%d%H}.{cst:03d}.png"

MODEL_SAVE_OUT_OBS = "/data/cpvs/Product/synoptic/{model}/{report_time:%Y%m%d}/{out_name}/{lev}/" \
                 "{region}_{report_time:%Y%m%d%H}.{cst:03d}.png"

t_850 = [
    [130, 30, 197],
    [142, 54, 241],
    [25, 25, 160],
    [25, 25, 210],
    [84, 120, 228],
    [52, 155, 255],
    [25, 197, 255],
    [170, 215, 255],
    [214, 246, 255],
    [255, 255, 205],
    [255, 228, 70],
    [255, 178, 25],
    [255, 124, 25],
    [255, 75, 25],
    [255, 25, 25],
    [205, 25, 25],
    [169, 57, 57],
    [255, 105, 180]
]
cape_850 = [
    [210, 240, 255],
    [200, 216, 255],
    [190, 202, 255],
    [127, 176, 255],
    [0, 100, 255],
    [127, 226, 152],
    [176, 255, 127],
    [226, 255, 152],
    [255, 255, 127],
    [255, 207, 127],
    [255, 150, 25],
    [255, 25, 0],
]
import numpy as np
cmap_t_850 = ['#{:02x}{:02x}{:02x}'.format(*tuple(i)) for i in t_850]
cmap_cape_850 = ['#{:02x}{:02x}{:02x}'.format(*tuple(i)) for i in cape_850]
contour_levels = np.arange(0, 2000, 4)