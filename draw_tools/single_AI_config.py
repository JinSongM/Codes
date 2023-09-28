infile_format = r'/u02/AI/{var}/{model}/{lev}/{RT:%Y%m}/{RT:%Y%m%d%H}.{cst:03d}'
windfile_format = r'/u02/AI/{var}/{model}/{lev}/{RT:%Y%m}/{lab}_{RT:%Y%m%d%H}.{cst:03d}'
outfile_format = r'/u02/AI/pic/{var}/{model}/{lev}/{label}/{inter}/{RT:%Y}/{RT:%Y%m%d}/{RT:%Y%m%d%H}.{cst:03d}.PNG'
outfile_month_format = r'/u02/AI/pic/{var}/{model}/{lev}/{label}/{inter}/{RT:%Y}/{RT:%Y%m}/{RT:%Y%m}.{RT:%H}.{cst:03d}.PNG'
#标题标签
t2m_title = "[{}]{} 温度{}(℃)"
t2m_title_pc = "[{}]{} 温度PC(%)"
t2m_var = '温度{}(℃)'
t2m_var_pc = '温度PC(%)'

gh_title = "[{}]{} 位势高度{}"
gh_var = '位势高度{}(hpa)'

sh_title = "[{}]{} 比湿{}(g/kg)"
sh_var = '比湿{}(g/kg)'

wind_title = "[{}]{} 风速{}(m/s)"
wind_title_pc = "[{}]{} 风速PC(%)"
wind_title_pcd = "[{}]{} 风向PC(%)"
wind_var = '风速{}(m/s)'
wind_var_pc = '风速PC(%)'
wind_var_pcd = '风向PC(%)'
#色标、间隔
cmap = 'ncl/ncl_default'
level_tmp = [i/10 for i in range(-20, 22, 2)]
level_gh = [i for i in range(-10, 11, 1)]
level_sh = [i/10 for i in range(-20, 22, 2)]
level_wind = [i/10 for i in range(-20, 22, 2)]

# cmap_sg = 'ncl/MPL_YlOrRd'
level_tmp_sg = [0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]
level_gh_sg = [i for i in range(0, 11, 1)]
level_sh_sg = [0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]
level_wind_sg = [0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]

# cmap_pc = ['#FFFF5B', '#FF9833', '#AD71B5', '#70BE6E', '#5F97C5', '#E94749']
cmap_pc = ['#8000FF', '#4D4FFC', '#1996F3', '#1ACEE3', '#4DF3CE', '#80FFB4',
            '#B3F396', '#E6CE74', '#FF964F', '#FF4F28'
           ]
level_pc = [50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
ticks_S = 10