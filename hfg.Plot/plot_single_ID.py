# -- coding: utf-8 --
# @Time : 2022/12/26 9:45
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : plot_single_ID.py
# @Software: PyCharm
import sys
from multiprocessing import Pool, Process
from datetime import datetime, timedelta
from verify.plot_ms_ID import single_plot, plot_wind_speed_single, single_plot_CLDAS, plot_wind_speed_single_CLDAS
from verify.plot_met_sf_ID import plot_wind_speed, plot_wind

Dict = ['tem', 'tem_max', 'tem_change', 'r', 'pre24_hgt', 'pre03', 'pre06', 'pre12', 'sf03', 'sf06', 'sf12',
        'sf24', 'tem_change_48','pre12_cp', 'pre24_cp', 'pre24_lsp', 'pre_sf_class', 'pre_sf24', 'tem_min',
        'gustwind', 'exwind_24', 'tem_exmax']
Dict_wind = ['wind']
Dict_wind_speed_sf = ['gh500_speed']
Dict_wind_sf = ['gh500_wind850_wvfldiv', 'gh500_wind850_wvfl', 'gh500_wind850_q', 'gh500_wind850_r', 'rcr',
                'gh500_wind850_t', 'gh500_wind850_rcr', 'gh500_wind500_t', 'gh500_wind850_kindex',  'gh500_wind850_cth',
                'gh500_wind850_msl', 'gh500_wind850_tcwv', 'gh500_wind850_cape', 'gh500_wind700_q', 'gh500_wind850_hpbl']

def multi_plot(argv_base, var, _argv, is_overwrite):
    if argv_base[0] == 'CLDAS':
        if var in Dict_wind:
            plot_wind_speed_single_CLDAS(_argv, is_overwrite)
        elif var in Dict:
            single_plot_CLDAS(_argv, is_overwrite)
    else:
        if var in Dict_wind:
            plot_wind_speed_single(_argv, is_overwrite)
        elif var in Dict:
            single_plot(_argv, is_overwrite)
        elif var in Dict_wind_speed_sf:
            plot_wind_speed(_argv, is_overwrite)
        elif var in Dict_wind_sf:
            plot_wind(_argv, is_overwrite)

def process_plot(argv):
    argv_base, argv_vars = argv[1:4], argv[4:]
    date_start = datetime.strptime(argv_base[1], "%Y%m%d%H")
    argvs_res = []
    for idx in range(int(argv_base[2])):
        report_time = date_start - timedelta(hours = 12 * idx)
        for var in argv_vars:
            _argv = [argv_base[0], report_time, var]
            p = Process(target=multi_plot, args=(argv_base, var, _argv,), daemon=True)
            p.start()
            argvs_res.append(p)
    for p in argvs_res:
        p.join()


def pool_plot(argv):
    pool = Pool(processes=8)
    argv_base, argv_vars = argv[1:4], argv[4].split(',')
    date_start = datetime.strptime(argv_base[1], "%Y%m%d%H")
    is_overwrite = False
    if argv[5] == '1':
        is_overwrite = True

    argvs_list = []
    for idx in range(int(argv_base[2])):
        report_time = date_start - timedelta(hours = 12 * idx)
        for var in argv_vars:
            _argv = [argv_base[0], report_time, var]
            #argvs_list.append([argv_base, var, _argv])
            res = pool.starmap_async(multi_plot, [[argv_base, var, _argv, is_overwrite]])
            argvs_list.append(res)
    for i in argvs_list:
        i.get()
    pool.close()
    pool.join()


if __name__ == '__main__':
    #argv：模式名称 %Y%m%d%H 回算时次 要素
    pool_plot(sys.argv)