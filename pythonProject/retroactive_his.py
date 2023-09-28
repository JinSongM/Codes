# -- coding: utf-8 --
# @Time : 2023/5/12 17:43
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : retroactive_his.py
# @Software: PyCharm
import sys
import os
from config import *
import meteva.base as meb
import pandas as pd
from datetime import datetime, timedelta

def read_typeTP(obs, obs6, Ppt1, Ppt2, Ppt2_sta, obs_t):
    land_obs_m3 = meb.read_stadata_from_micaps3(obs)
    land_obs6_m3 = meb.read_stadata_from_micaps3(obs6)
    Ppt2_sta_c1d = meb.read_stadata_from_micaps3(Ppt2_sta)
    Ppt1_c3e = pd.read_csv(Ppt1)
    Ppt2_c1d = pd.read_csv(Ppt2)
    obs_data = pd.DataFrame(land_obs_m3.get(['id', 'lon', 'lat', 'data0']))
    obs6_data = pd.DataFrame(land_obs6_m3.get(['id', 'data0']))
    c1d_sta_data = pd.DataFrame(Ppt2_sta_c1d.get(['id', 'data0']))
    c3e_data = Ppt1_c3e.get(['id', 'prob0', 'prob1', 'prob2', 'prob3', 'prob4'])
    c1d_data = Ppt2_c1d.get(['id', 'prob0', 'prob1', 'prob2', 'prob3', 'prob4'])
    df_merge = pd.merge(obs_data, obs6_data, how='inner', on='id').merge(c1d_sta_data, how='inner', on='id')\
        .merge(c3e_data, how='inner', on='id').merge(c1d_data, how='inner', on='id')
    df_merge.columns = ['ID','lon','lat','Obs','Obs6','Ppt2-sta','Ppt1-0','Ppt1-1',
                        'Ppt1-2','Ppt1-3','Ppt1-4','Ppt2-0','Ppt2-1','Ppt2-2','Ppt2-3','Ppt2-4']
    df_merge.insert(loc=3, column='obs_time', value=obs_t)
    return df_merge

def proc(start_day, end_day, cst, outPATH, rp_T, label):
    out_file = outPATH.format(rp_T=start_day, cst=cst, label=label, HR=rp_T)
    begin_day = start_day
    merge_df = pd.DataFrame()
    while begin_day <= end_day:
        obs_t = begin_day + timedelta(hours=cst)
        land_obs6_file = land_obs6.format(rp_T=obs_t)
        land_obs_file = land_obs.format(rp_T=obs_t)
        c3e_Ppt1_file = c3e_Ppt1.format(rp_T=begin_day, cst=cst)
        c1d_Ppt2_file = c1d_Ppt2.format(rp_T=begin_day, cst=cst)
        c1d_Ppt2_sta_file = c1d_Ppt2_sta.format(rp_T=begin_day, cst=cst)
        begin_day += timedelta(days=1)
        print(os.path.exists(land_obs6_file), os.path.exists(land_obs_file), os.path.exists(c3e_Ppt1_file),
              os.path.exists(c1d_Ppt2_file), os.path.exists(c1d_Ppt2_sta_file))
        if os.path.exists(land_obs6_file) and os.path.exists(land_obs_file) and os.path.exists(c3e_Ppt1_file) and\
                os.path.exists(c1d_Ppt2_file) and os.path.exists(c1d_Ppt2_sta_file):
            sub_df = read_typeTP(land_obs_file, land_obs6_file, c3e_Ppt1_file, c1d_Ppt2_file, c1d_Ppt2_sta_file, obs_t)
            merge_df = pd.concat([merge_df, sub_df])
        else:
            continue
    if not os.path.exists(os.path.dirname(out_file)):
        os.makedirs(os.path.dirname(out_file))
    merge_df.to_csv(out_file)
    print('成功输出至' + out_file)

def main(argv, fst_h, report_time):
    if len(argv) == 1:
        fst_time_list = [datetime.now()]
    else:
        fst_time_list = []
        for time_list in argv[1:]:
            startT, endT = [datetime.strptime(i, '%Y%m%d') for i in time_list.split('-')]
            beginT = startT

            while beginT <= endT:
                if beginT.day < 15:
                    thisMonth_first = datetime(beginT.year, beginT.month, 1) - timedelta(days=1)
                    lastMonth_mid = datetime(thisMonth_first.year, thisMonth_first.month, 16)
                    beginT += timedelta(days=1)
                    if lastMonth_mid not in fst_time_list:
                        fst_time_list.append(lastMonth_mid)
                else:
                    thisMonth_first = datetime(beginT.year, beginT.month, 1)
                    beginT += timedelta(days=1)
                    if thisMonth_first not in fst_time_list:
                        fst_time_list.append(thisMonth_first)
    for fst_time in fst_time_list:
        for rp_T in report_time:
            for cst in fst_h:
                if fst_time.day < 15:
                    start_day = fst_time.replace(hour=rp_T)
                    end_day = start_day.replace(day=15, hour=rp_T)
                    label = 'low'
                else:
                    start_day = fst_time.replace(hour=rp_T)
                    end_day = (datetime(start_day.year + int(start_day.month / 12), (start_day.month % 12) + 1, 1) - timedelta(days=1)).replace(hour=rp_T)
                    label = 'up'
                proc(start_day, end_day, cst, typePP_out, rp_T, label)

if __name__ == '__main__':
    report_time = [8, 20]
    main(sys.argv, fst_h, report_time)