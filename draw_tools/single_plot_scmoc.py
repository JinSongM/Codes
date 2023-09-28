import pandas as pd
import meteva.base as meb
import math
from single_config_scmoc import *
from matplotlib.ticker import MultipleLocator
from metdig.graphics.draw_compose import *
from datetime import datetime,timedelta
from metdig.graphics import draw_compose, contourf_method, scatter_method
from matplotlib import font_manager
font_manager.fontManager.addfont(os.path.join(os.path.dirname(__file__), 'simsun.ttc'))
import metdig.graphics.cmap.cm as cm_collected
import metdig.graphics.lib.utility as utl


def scatter_2d(ax, stda, xdim='lon', ydim='lat',
               add_colorbar=True, cb_pos='bottom', cb_ticks=None, cb_label=None,
               levels=np.arange(-40, 40), cmap='ncl/BlueYellowRed', extend='both', isLinear=False,
               transform=ccrs.PlateCarree(), alpha=1,
               colorbar_kwargs={}, s=10, **kwargs):
    """[graphics层绘制scatter平面图通用方法]

    Args:
        ax ([type]): [description]
        stda ([type]): [u矢量 stda标准格式]
        xdim (type, optional): [stda维度名 member, level, time dtime, lat, lon或fcst_time]. Defaults to 'lon'.
        ydim (type, optional): [stda维度名 member, level, time dtime, lat, lon或fcst_time]. Defaults to 'lat'.
        add_colorbar (bool, optional): [是否绘制colorbar]. Defaults to True.
        cb_pos (str, optional): [colorbar的位置]. Defaults to 'bottom'.
        cb_ticks ([type], optional): [colorbar的刻度]. Defaults to None.
        cb_label ([type], optional): [colorbar的label，如果不传则自动进行var_cn_name和var_units拼接]. Defaults to None.
        levels ([list], optional): [description]. Defaults to None.
        cmap (str, optional): [description]. Defaults to 'jet'.
        extend (str, optional): [description]. Defaults to 'both'.
        isLinear ([bool], optional): [是否对colors线性化]. Defaults to False.
        transform ([type], optional): [stda的投影类型，仅在xdim='lon' ydim='lat'时候生效]. Defaults to ccrs.PlateCarree().
        alpha (float, optional): [description]. Defaults to 1.
        s=1 (float, optional): [散点大小]. Defaults to 1.
    Returns:
        [type]: [绘图对象]
    """
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)

    cmap, norm = cm_collected.get_cmap(cmap, extend=extend, levels=levels, isLinear=isLinear)
    if transform is None or (xdim != 'lon' and ydim != 'lat'):
        img = ax.scatter(x, y, marker='.', s=s, norm=norm, cmap=cmap, c=z, alpha=alpha, **kwargs)

    else:
        img = ax.scatter(x, y, marker='.', s=s, norm=norm, cmap=cmap, c=z, transform=transform, alpha=alpha, **kwargs)

    if add_colorbar:
        cb_label = '{}({})'.format(stda.attrs['var_cn_name'], stda.attrs['var_units']) if not cb_label else cb_label
        utl.add_colorbar(ax, img, ticks=cb_ticks, pos=cb_pos, extend=extend, label=cb_label, kwargs=colorbar_kwargs)

    return img

def metdig_plot_s(infile, outfile, ini_config, sta):
    try:
        lat_lon_data = meb.read_griddata_from_micaps4(infile)
        map_extent = (int(min(list(lat_lon_data.lon.data))), math.ceil(max(list(lat_lon_data.lon.data))),
                      int(min(list(lat_lon_data.lat.data))), math.ceil(max(list(lat_lon_data.lat.data))))

        file_time = os.path.split(infile)[1].split('.')[0]
        Fst_time = int(os.path.split(infile)[1].split('.')[1])
        obs_time_dc = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(datetime.strptime(file_time, '%Y%m%d%H'))
        fst_time_dc = '预报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(datetime.strptime(file_time, '%Y%m%d%H') + timedelta(hours=Fst_time))
        forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时'.format(Fst_time)
        forcast_info = None
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
            scatter_2d(drw.ax, sta, xdim='lon', ydim='lat',s=5,
                       add_colorbar=True, cb_pos='bottom', cb_ticks=None, cb_label=ini_config[2],
                       levels=ini_config[1], cmap=ini_config[3], extend='both')

            drw.save()
            print('Finished plot')
        else:
            print('文件已存在')
    except:
        print(infile)

def metdig_plot_c(infile, outfile, ini_config, sta):
    try:
        lat_lon_data = meb.read_griddata_from_micaps4(infile)
        map_extent = (int(min(list(lat_lon_data.lon.data))), math.ceil(max(list(lat_lon_data.lon.data))),
                      int(min(list(lat_lon_data.lat.data))), math.ceil(max(list(lat_lon_data.lat.data))))

        file_time = os.path.split(infile)[1].split('.')[0]
        Fst_time = int(os.path.split(infile)[1].split('.')[1])
        obs_time_dc = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(datetime.strptime(file_time, '%Y%m%d%H'))
        fst_time_dc = '预报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(datetime.strptime(file_time, '%Y%m%d%H') + timedelta(hours=Fst_time))
        forcast_info = obs_time_dc + '\n' + fst_time_dc + '\n' + '预报时效：{}小时'.format(Fst_time)
        # forcast_info = None
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
            contourf_method.contourf_2d(drw.ax, lat_lon_data, levels=ini_config[1], cb_label=ini_config[2], cmap=ini_config[3], extend ='both')

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

def creat_M3_grd(data):

    # 构建站点数据标准格式
    M3_grd = pd.DataFrame(data)
    sta = meb.sta_data(M3_grd, columns=["id", "lon", "lat", 'data0'])
    meb.set_stadata_coords(sta, level=0, time=datetime(2023, 1, 1, 8, 0), dtime=0)
    return sta

def gain_sta(file1, file2):
    with open(file1, 'r', encoding='utf-8') as f1:
        content1 = f1.readlines()
    with open(file2, 'r', encoding='utf-8') as f2:
        content2 = f2.readlines()
    new_content1 = []
    for word in content1:
        tmp = word.strip()
        tmp = tmp.split()
        new_content1.append(tmp)
    new_content2 = []
    for word in content2:
        tmp = word.strip()
        tmp = tmp.split()
        new_content2.append(tmp)

    # DF1 = pd.DataFrame(new_content1, columns=['id', 'lon', 'lat', 'id1', 'local', 'local1']) #2400站
    DF1 = pd.DataFrame(new_content1, columns=['id', 'lon', 'lat', 'id1', 'local'])  #10290站
    DF2 = pd.DataFrame(new_content2, columns=['id', 'tmp_c', 'tmp1', 'tmp2'])
    df_merge = pd.merge(DF1, DF2, on='id')
    df_merge_filter = df_merge[['id', 'lon', 'lat', 'tmp_c']]
    df_merge_filter = df_merge_filter[df_merge_filter['tmp_c'].astype(np.float)<9999.0]
    df_merge_filter['tmp_c'] = df_merge_filter['tmp_c'].astype(float)
    df_merge_filter['lon'] = df_merge_filter['lon'].astype(float)
    df_merge_filter['lat'] = df_merge_filter['lat'].astype(float)
    sta = creat_M3_grd(df_merge_filter)
    return sta

if __name__ == '__main__':
    region = sys.argv[1]
    var = sys.argv[2]
    TT = datetime.strptime(sys.argv[3], "%Y%m%d%H")
    cst = int(sys.argv[4])
    infile = infile_format.format(region=region, var=var, TT=TT, cst=cst)
    outfile = outfile_format.format(region=region, var=var, TT=TT, cst=cst)

    ini_TMP = [t2m_title.format('盘古200hPa'), t2m_colorbar, t2m_var, cmap_tem]
    ini_TMAX = [t2m_max_title.format('BABJ'), t2m_colorbar, t2m_max_var, cmap_tem]
    ini_TMIN = [t2m_min_title.format('BABJ'), t2m_colorbar, t2m_min_var, cmap_tem]
    ini_TP = [tp_title.format('BABJ'), tp_colorbar, tp_var, cmap_tp_hour]
    ini_RAT = [RAT_title.format('BABJ'), RAT_colorbar, RAT_var, cmap_RAT]
    ini_SMG = [SMG_title.format('BABJ'), SMG_colorbar, SMG_var, cmap_SMG]

    var_dict = {
        'tmp': [metdig_plot_c, ini_TMP],
        'tmax': [metdig_plot_c, ini_TMAX],
        'tmin': [metdig_plot_c, ini_TMIN],
        'r01': [metdig_plot_c, ini_TP],
        'rat': [metdig_plot_class, ini_RAT],
        'smg': [metdig_plot_class, ini_SMG],
    }

    file1 = r'C:\Users\wiztek\Documents\WeChat Files\wxid_43vosvk7mvre22\FileStorage\File\2023-08\sta_10290.dat'
    file2 = r'C:\Users\wiztek\Documents\WeChat Files\wxid_43vosvk7mvre22\FileStorage\File\2023-08\2023080108.054'
    # sta = gain_sta(file1, file2)
    sta = None
    var_dict.get(var)[0](infile, outfile, var_dict.get(var)[1], sta)