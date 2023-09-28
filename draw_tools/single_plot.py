import glob


import meteva.base as meb
import math
from single_config import *
from matplotlib.ticker import MultipleLocator
from metdig.graphics.draw_compose import *
from datetime import datetime,timedelta
from metdig.graphics import draw_compose, contourf_method
from metdig.graphics.pcolormesh_method import *
from matplotlib import font_manager
# font_manager.fontManager.addfont(os.path.join(os.path.dirname(__file__), 'SIMHEI.TTF'))

def metdig_plot(infile, outfile, ini_config):
    try:
        lat_lon_data = meb.read_griddata_from_micaps4(infile)
        map_extent = (int(min(list(lat_lon_data.lon.data))), math.ceil(max(list(lat_lon_data.lon.data))),
                      int(min(list(lat_lon_data.lat.data))), math.ceil(max(list(lat_lon_data.lat.data))))

        file_time = os.path.split(infile)[1].split('.')[0]
        Fst_time = int(os.path.split(infile)[1].split('.')[1])
        obs_time_dc = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(datetime.strptime(file_time, '%Y%m%d%H'))
        fst_time_dc = '预报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(datetime.strptime(file_time, '%Y%m%d%H') + timedelta(hours=Fst_time))
        forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时'.format(Fst_time)
        png_name = file_time + '.' + os.path.split(infile)[1].split('.')[1] + '.PNG'

        if not os.path.exists(outfile):
            drw = draw_compose.horizontal_compose(title=ini_config[0], description=forcast_info, output_dir=os.path.dirname(outfile),
                                                  add_tag=False, add_city=False,
                                                  map_extent=map_extent, png_name=png_name, is_return_figax=True, add_ticks=True)
            if 'BABJ' in infile:
                ticks_S = ticks_step_BABJ
            else:
                ticks_S = ticks_step
            drw.ax.xaxis.set_major_locator(MultipleLocator(ticks_S))
            drw.ax.yaxis.set_major_locator(MultipleLocator(ticks_S))
            if '降水' in ini_config[2]:
                pcolormesh_2d(drw.ax, lat_lon_data, cb_label=ini_config[2], levels=ini_config[1], cmap=ini_config[3], alpha=1)
            else:
                contourf_method.contourf_2d(drw.ax, lat_lon_data, levels=ini_config[1], cb_label=ini_config[2], cmap=ini_config[3])
            drw.save()
            print('Finished plot')
        else:
            print('文件已存在')
    except:
        print(infile)

def metdig_plot_class(infile, outfile, ini_config):
    try:
        lat_lon_data = meb.read_griddata_from_micaps4(infile)
        map_extent = (int(min(list(lat_lon_data.lon.data))), math.ceil(max(list(lat_lon_data.lon.data))),
                      int(min(list(lat_lon_data.lat.data))), math.ceil(max(list(lat_lon_data.lat.data))))
        data_array = lat_lon_data.data[0][0][0][0]
        data_array[(data_array > 0) & (data_array < 999)] = 2
        data_array[data_array >= 999] = 3
        data_array[data_array <= 0] = np.nan
        lat_lon_data.data = [[[[data_array]]]]

        file_time = os.path.split(infile)[1].split('.')[0]
        Fst_time = int(os.path.split(infile)[1].split('.')[1])
        obs_time_dc = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(datetime.strptime(file_time, '%Y%m%d%H'))
        fst_time_dc = '预报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(datetime.strptime(file_time, '%Y%m%d%H') + timedelta(hours=Fst_time))
        forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时'.format(Fst_time)
        png_name = file_time + '.' + os.path.split(infile)[1].split('.')[1] + '.PNG'

        if not os.path.exists(outfile):
            drw = draw_compose.horizontal_compose(title=ini_config[0], description=forcast_info, output_dir=os.path.dirname(outfile),
                                                  add_tag=False, add_city=False,
                                                  map_extent=map_extent, png_name=png_name, is_return_figax=True, add_ticks=True)
            if 'BABJ' in infile:
                ticks_S = ticks_step_BABJ
            else:
                ticks_S = ticks_step
            drw.ax.xaxis.set_major_locator(MultipleLocator(ticks_S))
            drw.ax.yaxis.set_major_locator(MultipleLocator(ticks_S))
            contourf_method.contourf_2d(drw.ax, lat_lon_data, levels=ini_config[1], cb_label=' ',
                                        extend='neither', cb_ticks=[0.5, 1.5, 2.5], cmap=ini_config[3], alpha=1,
                                        colorbar_kwargs={'pad': 0.04, 'tick_label': ['无', ini_config[2], '缺测']})
            drw.save()
            print('Finished plot')
        else:
            print('文件已存在')
    except:
        print(infile)


if __name__ == '__main__':
    region = sys.argv[1]
    var = sys.argv[2]
    TT = datetime.strptime(sys.argv[3], "%Y%m%d%H")
    cst = int(sys.argv[4])
    infile = infile_format.format(region=region, var=var, TT=TT, cst=cst)
    outfile = outfile_format.format(region=region, var=var, TT=TT, cst=cst)

    ini_TMP = [t2m_title.format(region), t2m_colorbar, t2m_var, cmap_tem]
    ini_TMAX = [t2m_max_title.format(region), t2m_colorbar, t2m_max_var, cmap_tem]
    ini_TMIN = [t2m_min_title.format(region), t2m_colorbar, t2m_min_var, cmap_tem]
    ini_TP = [tp_title.format(region), tp_colorbar, tp_var, cmap_tp_hour]
    ini_RAT = [RAT_title.format(region), RAT_colorbar, RAT_var, cmap_RAT]
    ini_SMG = [SMG_title.format(region), SMG_colorbar, SMG_var, cmap_SMG]

    var_dict = {
        'tmp': [metdig_plot, ini_TMP],
        'tmax': [metdig_plot, ini_TMAX],
        'tmin': [metdig_plot, ini_TMIN],
        'r01': [metdig_plot, ini_TP],
        'rat': [metdig_plot_class, ini_RAT],
        'smg': [metdig_plot_class, ini_SMG],
    }
    var_dict.get(var)[0](infile, outfile, var_dict.get(var)[1])