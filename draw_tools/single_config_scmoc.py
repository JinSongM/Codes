# infile_format = r'/u01/SPFC/data_scmoc/{region}/{var}/{TT:%Y}/{TT:%Y%m%d}/{TT:%Y%m%d%H}.{cst:03d}'
# outfile_format = r'/u01/SPFC/pic_scmoc/{region}/{var}/{TT:%Y}/{TT:%Y%m%d}/{TT:%Y%m%d%H}.{cst:03d}.png'
# infile_format = r'/data/data/{var}/{TT:%Y}/{TT:%Y%m%d}/{TT:%Y%m%d%H}.{cst:03d}'
# outfile_format = r'/data/data/result/{var}/{TT:%Y}/{TT:%Y%m%d}/{TT:%Y%m%d%H}.{cst:03d}.png'
infile_format = r'/data/data/{var}/{TT:%Y}/{TT:%Y%m%d}/{TT:%Y%m%d%H}.{cst:03d}'
outfile_format = r'/data/data/result/{var}/{TT:%Y}/{TT:%Y%m%d}/{TT:%Y%m%d%H}.{cst:03d}.png'
t2m_title = "[{}]温度平均误差(℃)"
t2m_var = '温度平均误差(℃)'
t2m_max_title = "[{}]高温（K）"
t2m_max_var = '高温（K）'
t2m_min_title = "[{}]低温（K）"
t2m_min_var = '低温（K）'
cmap_tem = 'ncl/ncl_default'
# cmap_tem = [
# '#FFFF5B','#FF9833','#AD71B5',    '#70BE6E','#5F97C5','#E94749'
# ]
t2m_colorbar = [i/10 for i in range(-20, 20, 2)]


tp_title = "[{}]1h降水（mm）"
tp_var = '降水（mm）'
tp_units = 'mm'
tp_colorbar = [0, 0.1, 2.5, 5, 10, 25, 50, 100]
tp_hour_color = [
    [0, 0, 0],
    [255, 255, 255],
    [167, 242, 143],
    [54, 187, 68],
    [100, 230, 253],
    [100, 184, 253],
    [0, 0, 254],
    [255, 0, 255],
    [130, 0, 62]
]
cmap_tp_hour = ['#{:02x}{:02x}{:02x}'.format(*tuple(i)) for i in tp_hour_color]

RAT_title = "[{}]短时强降水"
RAT_var = '短时强降水'
RAT_colorbar = [0, 1, 2, 3]
cmap_RAT = ['#ffffff', '#FACC4F', '#808080']

SMG_title = "[{}]雷暴大风"
SMG_var = '雷暴大风'
SMG_colorbar = [0, 1, 2, 3]
cmap_SMG = ['#ffffff', '#FACC4F', '#808080']

ticks_step = 10
ticks_step_BABJ = 10