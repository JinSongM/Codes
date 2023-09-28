import math
import metdig
import sys, os
import pandas as pd
import meteva.base as meb
from metdig.cal import other
import matplotlib.pyplot as plt
from verify.config_single  import *
from datetime import datetime, timedelta
from matplotlib.ticker import MultipleLocator


colors = ['k','r','b','g','c','m','y']
model_name = ['OBS','CMA_GFS','CMA_MESO','CMA_TYM','NCEP','ECMWF']

def creat_file_path(file_path):
    dir_name = os.path.dirname(file_path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

def sta_grd(sta_id):
    m3_file = './fonts/station_id.m3'
    sta_array = meb.read_sta_alt_from_micaps3(m3_file)
    M3_df = pd.DataFrame({
        'id': list(sta_array.id),
        "lon": list(sta_array.lon),
        "lat": list(sta_array.lat),
    })
    M3_df_sub = M3_df[M3_df['id'] == int(sta_id)]

    # 构建站点数据标准格式
    M3_grd = {
        'id': [sta_id],
        "lon": [M3_df_sub.lon.values[0]],
        "lat": [M3_df_sub.lat.values[0]],
    }
    sta = meb.sta_data(pd.DataFrame(M3_grd), columns=["id", "lon", "lat"])
    meb.set_stadata_coords(sta, level=0, time=datetime(2000, 1, 1, 8, 0), dtime=0)
    return sta

def gain_sta_name(sta_id):
    sta_file = './fonts/sta_2410.dat'
    # sta_df = pd.DataFrame(open(sta_file, encoding='utf-8'))
    with open(sta_file, encoding='utf-8') as f:
        for file in f:
            file_split = file.split()
            if file_split[0] == sta_id:
                sta = file_split[-1]
    return sta

def gain_BJ_obs(file_list):
    TMP, windV, windD, DPT = [], [], [], []
    for file in file_list:
        if os.path.exists(file):
            with open(file, encoding='utf-8') as f:
                for file_line in f:
                    if len(file_line) == 202:
                        notes = file_line.strip().split()
                        if int(float(notes[0])) == 54511:
                            TMP.append(float(notes[4]))
                            windV.append(float(notes[8]))
                            windD.append(float(notes[7]))
                            DPT.append(float(notes[6]))
        else:
            TMP.append(None)
            windV.append(None)
            windD.append(None)
            DPT.append(None)
    TMP = [None if i is not None and i >= 9999 else i for i in TMP]
    windV = [None if i is not None and i >= 9999 else i for i in windV]
    windD = [None if i is not None and i >= 9999 else i for i in windD]
    DPT = [None if i is not None and i >= 9999 else i for i in DPT]
    return TMP, windV, windD, DPT

def gain_BJ_fst(file_list, sta):
    value_list = []
    for file in file_list:
        if os.path.exists(file):
            sta_grd = meb.read_griddata_from_micaps4(file)
            inter_grd = meb.interp_gs_nearest(sta_grd, sta)
            value_list.append(inter_grd.data0[0])
        else:
            value_list.append(None)
    return value_list

def gain_BJ_fst_VD(file_list_u, file_list_v, sta):
    WV_list, WD_list = [], []
    for i in range(len(file_list_u)):
        if os.path.exists(file_list_u[i]) and os.path.exists(file_list_v[i]):
            u, v = meb.read_griddata_from_micaps4(file_list_u[i]), meb.read_griddata_from_micaps4(file_list_v[i])
            u_array = metdig.utl.xrda_to_gridstda(u, level_dim='level', time_dim='time', lat_dim='lat',
                                                 lon_dim='lon', dtime_dim='dtime',
                                                 var_name='u', np_input_units='m/s')
            v_array = metdig.utl.xrda_to_gridstda(v, level_dim='level', time_dim='time', lat_dim='lat',
                                                 lon_dim='lon', dtime_dim='dtime',
                                                 var_name='v', np_input_units='m/s')

            wind_speed = other.wind_speed(u_array, v_array)
            wind_direction = other.wind_direction(u_array, v_array)
            inter_speed, inter_direction  = meb.interp_gs_nearest(wind_speed, sta), meb.interp_gs_nearest(wind_direction, sta)
            WV_list.append(inter_speed.data0[0])
            WD_list.append(inter_direction.data0[0])
        else:
            WV_list.append(None)
            WD_list.append(None)
    return WV_list, WD_list

def gain_BJ_fst_uv(file_list_u, file_list_v, sta):
    u_list, v_list = [], []
    for i in range(len(file_list_u)):
        if os.path.exists(file_list_u[i]) and os.path.exists(file_list_v[i]):
            u, v = meb.read_griddata_from_micaps4(file_list_u[i]), meb.read_griddata_from_micaps4(file_list_v[i])
            inter_u, inter_v  = meb.interp_gs_nearest(u, sta), meb.interp_gs_nearest(v, sta)
            u_list.append(inter_u.data0[0])
            v_list.append(inter_v.data0[0])
        else:
            u_list.append(None)
            v_list.append(None)
    return u_list, v_list

def gain_BJ_obs_uv(file_list_windv, file_list_windD):
    U, V = [], []
    rad = np.pi / 180.0
    for i in range(len(file_list_windD)):
        if file_list_windv[i] is not None and file_list_windD[i] is not None:
            U_value = -file_list_windv[i] * np.sin(file_list_windD[i] * rad)
            V_value = -file_list_windv[i] * np.cos(file_list_windD[i] * rad)
            U.append(U_value)
            V.append(V_value)
        else:
            U.append(None)
            V.append(None)
    return U, V


def plot_station_TMP(report_time, sta, lev, fst_hours, model_list, sta_name):
    obs_hour = []
    obs_time = report_time + timedelta(hours=fst_hours)
    if report_time.hour == 8 or report_time.hour == 20:
        star_obs_time_tmp = report_time

        while star_obs_time_tmp <= obs_time:
            obs_hour.append(star_obs_time_tmp)
            star_obs_time_tmp += timedelta(hours=1)

        cst = [i for i in range(0, fst_hours+3, 3)]
        TMP_series = STATION_SAVE_OUT.format(model='RAWSH', report_time=report_time, out_name='gh_tem_series', lev=lev, region=str(sta.id.values[0]), cst=fst_hours)
        creat_file_path(TMP_series)
        forcast_info = '{}站_{}年{}月{}日{}时-{}日{}时_{}hpa气温'.format(sta_name, report_time.year, report_time.month,
                                                         report_time.day, report_time.hour, obs_time.day, obs_time.hour, lev)
        station_files = [STATION_PATH.format(obs_t=i) for i in obs_hour]
        X_labels = [i.strftime('%H')+'时' if i.hour != 8 and i.hour != 0 else i.strftime('%H')+'时'+'\n'+i.strftime('%m-%d') for i in obs_hour]
        xlabels = np.array([i for i in range(len(obs_hour))])
        TMP, windV, windD, DPT = gain_BJ_obs(station_files)

        #温度
        plt.figure(figsize=(16, 6))
        TMP_mask = np.isfinite(np.array(TMP).astype(np.double))
        TMP_y = np.array(TMP)[TMP_mask]
        TMP_x = np.array(xlabels)[TMP_mask]
        plt.plot(TMP_x, TMP_y, label='OBS', linewidth=1.5, color='k', marker='o', markersize='4',
                 markerfacecolor='none')
        for model in model_list:
            index_model = model_name.index(model)
            model_TMP_files = [
                MODEL_ROOT.format(model=model, report_time=report_time, cst=i, element='t', lev=lev) for i in cst]
            model_TMP = gain_BJ_fst(model_TMP_files, sta)
            model_TMP_mask = np.isfinite(np.array(model_TMP).astype(np.double))
            model_TMP_y = np.array(model_TMP)[model_TMP_mask]
            model_TMP_x = np.array(cst)[model_TMP_mask]
            plt.plot(model_TMP_x, model_TMP_y, label=model, linewidth=1.5, color=colors[index_model], marker='o', markersize='4', markerfacecolor='none')

        ax = plt.gca()
        plt.yticks(size=16)
        plt.xticks(xlabels, X_labels, fontproperties='SimHei', size=16)
        plt.grid(True, linestyle="--", alpha=0.5, axis='x')
        ax.xaxis.set_major_locator(MultipleLocator(4))
        plt.title(forcast_info, loc='center', fontproperties='SimHei', fontsize=22)
        ax.set_ylabel('温度(℃)', fontsize=18, fontproperties='SimHei')
        plt.legend(fontsize=18, bbox_to_anchor=(0.5, -0.1), loc=9, ncol=len(model_list)+1, frameon=False)
        plt.savefig(TMP_series, bbox_inches='tight', dpi=100)
        plt.close()

def plot_station_RH(report_time, sta, lev, fst_hours, model_list, sta_name):
    obs_hour = []
    obs_time = report_time + timedelta(hours=fst_hours)
    if report_time.hour == 8 or report_time.hour == 20:
        star_obs_time_tmp = report_time

        while star_obs_time_tmp <= obs_time:
            obs_hour.append(star_obs_time_tmp)
            star_obs_time_tmp += timedelta(hours=1)

        cst = [i for i in range(0, fst_hours+3, 3)]
        RH_series = STATION_SAVE_OUT.format(model='RAWSH', report_time=report_time, out_name='gh_r_series', lev=lev, region=str(sta.id.values[0]), cst=fst_hours)
        creat_file_path(RH_series)
        forcast_info = '{}站_{}年{}月{}日{}时-{}日{}时_{}hpa相对湿度'.format(sta_name, report_time.year, report_time.month,
                                                         report_time.day, report_time.hour, obs_time.day, obs_time.hour, lev)
        station_files = [STATION_PATH.format(obs_t=i) for i in obs_hour]
        X_labels = [i.strftime('%H')+'时' if i.hour != 8 and i.hour != 0 else i.strftime('%H')+'时'+'\n'+i.strftime('%m-%d') for i in obs_hour]
        xlabels = np.array([i for i in range(len(obs_hour))])
        TMP, windV, windD, DPT = gain_BJ_obs(station_files)

        #相对湿度
        plt.figure(figsize=(16, 6))
        TMP_mask = np.isfinite(np.array(TMP).astype(np.double))
        DPT_mask = np.isfinite(np.array(DPT).astype(np.double))
        mask_TMP_DPT = TMP_mask & DPT_mask
        TMP_RH, DPT_RH = np.array(TMP)[mask_TMP_DPT], np.array(DPT)[mask_TMP_DPT]
        temp = [(1 - (TMP_RH[i] + 235) / (DPT_RH[i] + 235))/(TMP_RH[i] + 235)  for i in range(len(TMP_RH))]
        RH = [100 * math.exp(4030 * i) for i in temp]
        RH_x = np.array(xlabels)[mask_TMP_DPT]
        plt.plot(RH_x, RH, label='OBS', linewidth=1.5, color='k', marker='o', markersize='4', markerfacecolor='none')
        for model in model_list:
            index_model = model_name.index(model)
            model_RH_files = [
                MODEL_ROOT.format(model=model, report_time=report_time, cst=i, element='r', lev=lev) for i in cst]
            model_RH = gain_BJ_fst(model_RH_files, sta)
            model_RH_mask = np.isfinite(np.array(model_RH).astype(np.double))
            model_RH_y = np.array(model_RH)[model_RH_mask]
            model_RH_x = np.array(cst)[model_RH_mask]
            plt.plot(model_RH_x, model_RH_y, label=model, linewidth=1.5, color=colors[index_model], marker='o', markersize='4', markerfacecolor='none')

        ax = plt.gca()
        plt.yticks(size=16)
        plt.xticks(xlabels, X_labels, fontproperties='SimHei', size=16)
        plt.grid(True, linestyle="--", alpha=0.5, axis='x')
        plt.ylim(0, 100)
        ax.xaxis.set_major_locator(MultipleLocator(4))
        ax.yaxis.set_major_locator(MultipleLocator(20))
        plt.title(forcast_info, loc='center', fontproperties='SimHei', fontsize=22)
        ax.set_ylabel('相对湿度(%)', fontsize=18, fontproperties='SimHei')
        plt.legend(fontsize=18, bbox_to_anchor=(0.5, -0.1), loc=9, ncol=len(model_list)+1, frameon=False)
        plt.savefig(RH_series, bbox_inches='tight', dpi=100)
        plt.close()

def plot_station_WV(report_time, sta, lev, fst_hours, model_list, sta_name):
    obs_hour = []
    obs_time = report_time + timedelta(hours=fst_hours)
    if report_time.hour == 8 or report_time.hour == 20:
        star_obs_time_tmp = report_time

        while star_obs_time_tmp <= obs_time:
            obs_hour.append(star_obs_time_tmp)
            star_obs_time_tmp += timedelta(hours=1)

        cst = [i for i in range(0, fst_hours+3, 3)]
        windV_series = STATION_SAVE_OUT.format(model='RAWSH', report_time=report_time, out_name='gh_windv', lev=lev, region=str(sta.id.values[0]), cst=fst_hours)
        creat_file_path(windV_series)
        forcast_info = '{}站_{}年{}月{}日{}时-{}日{}时_{}hpa风速风向'.format(sta_name, report_time.year, report_time.month,
                                                         report_time.day, report_time.hour, obs_time.day, obs_time.hour, lev)
        station_files = [STATION_PATH.format(obs_t=i) for i in obs_hour]
        X_labels = [i.strftime('%H')+'时' if i.hour != 8 and i.hour != 0 else i.strftime('%H')+'时'+'\n'+i.strftime('%m-%d') for i in obs_hour]
        xlabels = np.array([i for i in range(len(obs_hour))])
        TMP, windV, windD, DPT = gain_BJ_obs(station_files)
        U, V = gain_BJ_obs_uv(windV, windD)

        #风速
        plt.figure(figsize=(16, 6))
        windV_mask = np.isfinite(np.array(windV).astype(np.double))
        windV_y = np.array(windV)[windV_mask]
        windV_x = np.array(xlabels)[windV_mask]
        U_mask = np.isfinite(np.array(U).astype(np.double))
        bars_y = windV_y[U_mask[windV_mask]]
        U_y = np.array(U)[U_mask]
        U_x = np.array(xlabels)[U_mask]
        V_mask = np.isfinite(np.array(V).astype(np.double))
        V_y = np.array(V)[V_mask]
        plt.plot(windV_x, windV_y, label='OBS', linewidth=1.5, color='k', marker='o', markersize='4', markerfacecolor='none')
        plt.barbs(U_x, list(bars_y), list(U_y), list(V_y), flagcolor='k', alpha=0.8, sizes=dict(emptybarb=0), length=6.5)

        for model in model_list:
            index_model = model_name.index(model)
            model_U_files = [
                MODEL_ROOT.format(model=model, report_time=report_time, cst=i, element='u', lev=lev) for i in cst]
            model_V_files = [
                MODEL_ROOT.format(model=model, report_time=report_time, cst=i, element='v', lev=lev) for i in cst]

            model_WV, model_WD = gain_BJ_fst_VD(model_U_files, model_V_files, sta)
            model_U, model_V = gain_BJ_fst_uv(model_U_files, model_V_files, sta)

            model_windV_mask = np.isfinite(np.array(model_WV).astype(np.double))
            model_windV_y = np.array(model_WV)[model_windV_mask]
            model_windV_x = np.array(cst)[model_windV_mask]
            model_U_mask = np.isfinite(np.array(model_U).astype(np.double))
            model_U_y = np.array(model_U)[model_U_mask]
            model_U_x = np.array(cst)[model_U_mask]
            model_V_mask = np.isfinite(np.array(model_V).astype(np.double))
            model_V_y = np.array(model_V)[model_V_mask]

            plt.plot(model_windV_x, model_windV_y, label=model, linewidth=1.5, color=colors[index_model], marker='o', markersize='4', markerfacecolor='none')
            plt.barbs(model_U_x, list(model_windV_y), list(model_U_y), list(model_V_y), flagcolor=colors[index_model], alpha=0.8, sizes=dict(emptybarb=0), length=6.5)

        ax = plt.gca()
        plt.yticks(size=16)
        plt.xticks(xlabels, X_labels, fontproperties='SimHei', size=16)
        ax.xaxis.set_major_locator(MultipleLocator(4))
        plt.title(forcast_info, loc='center', fontproperties='SimHei', fontsize=22)
        ax.set_ylabel('风速(m/s)', fontsize=18, fontproperties='SimHei', labelpad=10)
        plt.legend(fontsize=18, bbox_to_anchor=(0.5, -0.1), loc=9, ncol=len(model_list)+1, frameon=False)
        plt.grid(True, linestyle="--", alpha=0.5, axis='x')
        plt.savefig(windV_series, bbox_inches='tight', dpi=100)
        plt.close()

if __name__ == '__main__':
    #argv：%Y%m%d%H 要素 站点ID lev 预报小时 模式名
    report_time = datetime.strptime(sys.argv[1], "%Y%m%d%H")
    sta = sta_grd(sys.argv[3])
    sta_name = gain_sta_name(sys.argv[3])
    lev = sys.argv[4]
    fst_hours = int(sys.argv[5])
    model_list = sys.argv[6].split(',')

    var_dict = {
        'gh_tem_series': plot_station_TMP,
        'gh_r_series': plot_station_RH,
        'gh_windv': plot_station_WV
    }
    var_dict.get(sys.argv[2])(report_time, sta, lev, fst_hours, model_list, sta_name)