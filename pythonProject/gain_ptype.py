# -- coding: utf-8 --
# @Time : 2023/5/23 15:46
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : gain_ptype.py
# @Software: PyCharm

import sys
from config import *
from config_parser import *
import meteva.base as meb
from datetime import datetime, timedelta
from parser_ptype_NAFP import proc_obs, proc_nafp
from precipitation_type import ptype

if __name__ == '__main__':
    #参数：OBS 2023051000-2023051100
    argv = sys.argv
    model = argv[1]
    station = meb.read_stadata_from_micaps3(station_file)
    if len(argv) == 2:
        startT, endT = datetime.now().replace(hour=0, minute=0) - timedelta(days=1), datetime.now().replace(hour=12, minute=0)
        print(startT, endT)
        if model == 'OBS':
            proc_obs(startT, endT)
        else:
            proc_nafp(startT, endT, model)
        print('Finished proc')
        ptype(startT, endT, fst_h, model)
        print('Finished ptype')

    else:
        for time_list in argv[2:]:
            startT, endT = [datetime.strptime(i, '%Y%m%d%H') for i in time_list.split('-')]
            print(startT, endT)
            if model == 'OBS':
                proc_obs(startT, endT)
            else:
                proc_nafp(startT, endT, model)
            print('Finished proc')
            ptype(startT, endT, fst_h, model)
            print('Finished ptype')