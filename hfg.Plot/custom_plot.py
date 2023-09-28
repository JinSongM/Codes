import logging
import sys
from datetime import datetime, timedelta
from verify.custom_plot_ms import single_plot, plot_wind_speed_single, single_plot_CLDAS, plot_wind_speed_single_CLDAS
from verify.custom_plot_met_sf import plot_wind_speed, plot_wind

Dict = ['tem', 'tem_max', 'tem_change', 'r', 'pre24_hgt', 'pre03', 'pre06', 'pre12', 'sf03', 'sf06', 'sf12',
        'sf24', 'tem_change_48','pre12_cp', 'pre24_cp', 'pre24_lsp', 'pre_sf_class', 'pre_sf24', 'tem_min',
        'tem_exmax', 'gustwind', 'exwind_24']
Dict_wind = ['wind']
Dict_wind_speed_sf = ['gh500_speed']
Dict_wind_sf = ['gh500_wind850_wvfldiv', 'gh500_wind850_wvfl', 'gh500_wind850_q', 'gh500_wind850_r', 'gh500_wind850_t',
             'gh500_wind500_t', 'gh500_wind850_kindex', 'gh500_wind850_msl', 'gh500_wind850_tcwv', 'gh500_wind850_cape',
                'gh500_wind850_rcr', 'rcr', 'gh500_wind850_hpbl', 'gh500_wind700_q', 'gh500_wind850_cth']

def process_plot(argv):
    if argv[0] == 'CLDAS':
        if argv[3] in Dict_wind:
            plot_wind_speed_single_CLDAS(argv)
        elif argv[3] in Dict:
            single_plot_CLDAS(argv)
    else:
        if argv[3] in Dict_wind:
            plot_wind_speed_single(argv)
        elif argv[3] in Dict:
            single_plot(argv)
        elif argv[3] in Dict_wind_speed_sf:
            plot_wind_speed(argv)
        elif argv[3] in Dict_wind_sf:
            plot_wind(argv)

if __name__ == '__main__':
    #argv：模式名称 %Y%m%d%H 时效 要素 区域名称 层级
    agrvs = sys.argv[1:]
    if Dict_wind_speed_sf.__contains__(agrvs[3]) or Dict_wind_sf.__contains__(agrvs[3]):
        try:
            agrvs_obs = agrvs.copy()
            agrvs_obs[2] = '0'
            process_plot(agrvs)
            process_plot(agrvs_obs)
        except Exception as e:
            logging.error(e)
    elif Dict_wind.__contains__(agrvs[3]) or Dict.__contains__(agrvs[3]):
        try:
            agrvs_obs = agrvs.copy()
            obs_time = datetime.strptime(agrvs_obs[1], '%Y%m%d%H') + timedelta(hours=int(agrvs_obs[2]))
            agrvs_obs[0], agrvs_obs[1], agrvs_obs[2] = 'CLDAS', obs_time.strftime('%Y%m%d%H'), str(obs_time.hour)
            process_plot(agrvs)
            process_plot(agrvs_obs)
        except Exception as e:
            logging.error(e)
    else:
        logging.error('要素名称有误')