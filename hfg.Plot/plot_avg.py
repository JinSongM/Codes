# -- coding: utf-8 --
# @Time : 2023/7/5 14:11
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : plot_avg.py
# @Software: PyCharm
import sys
from datetime import datetime
from verify import plot_met_single_avg

Dict_single = ['tem', 'tem_max', 'tem_change', 'r', 'pre24_hgt', 'pre03', 'pre06', 'pre12', 'sf03', 'sf06', 'sf12',
            'sf24', 'tem_change_48','pre12_cp', 'pre24_cp', 'pre24_lsp', 'pre_sf_class', 'pre_sf24', 'tem_min',
            'gustwind', 'exwind_24', 'tem_exmax', 'wind']
Dict_situation = ['gh500_wind850_wvfldiv', 'gh500_wind850_wvfl', 'gh500_wind850_q', 'gh500_wind850_r', 'rcr', 'gh500_speed',
                'gh500_wind850_t', 'gh500_wind850_rcr', 'gh500_wind500_t', 'gh500_wind850_kindex',  'gh500_wind850_cth',
                'gh500_wind850_msl', 'gh500_wind850_tcwv', 'gh500_wind850_cape', 'gh500_wind700_q', 'gh500_wind850_hpbl']

if __name__ == '__main__':
    model_name = sys.argv[1]
    report_time = datetime.strptime(sys.argv[2], "%Y%m%d%H")
    report_time2 = datetime.strptime(sys.argv[3], "%Y%m%d%H")
    cst = int(sys.argv[4])
    var = sys.argv[5]
    if var in Dict_single:
        plot_met_single_avg.single_plot(model_name, report_time, report_time2, cst, var)
    else:
        print(1)