import sys
from verify.plot_ms_Filter import single_plot, plot_wind_speed_single, single_plot_CLDAS, plot_wind_speed_single_CLDAS
from verify.plot_met_sf import plot_wind_speed, plot_wind

Dict = ['tem', 'tem_max', 'tem_change', 'r', 'pre24_hgt', 'pre03', 'pre06', 'pre12',
        'sf24', 'tem_change_48','pre12_cp', 'pre24_cp', 'pre24_lsp']
Dict_wind = ['wind']
Dict_wind_speed_sf = ['gh500_speed']
Dict_wind_sf = ['gh500_wind850_wvfldiv', 'gh500_wind850_wvfl', 'gh500_wind850_q', 'gh500_wind850_r', 'gh500_wind850_t',
             'gh500_wind500_t', 'gh500_wind850_kindex', 'gh500_wind850_msl', 'gh500_wind850_tcwv', 'gh500_wind850_cape',
                'gh500_wind850_rcr']

def process_plot(argv):
    if argv[1] == 'CLDAS':
        if argv[4] in Dict_wind:
            plot_wind_speed_single_CLDAS(argv[1:])
        elif argv[4] in Dict:
            single_plot_CLDAS(argv[1:])
    else:
        if argv[4] in Dict_wind:
            plot_wind_speed_single(argv[1:])
        elif argv[4] in Dict:
            single_plot(argv[1:])
        elif argv[4] in Dict_wind_speed_sf:
            plot_wind_speed(argv[1:])
        elif argv[4] in Dict_wind_sf:
            plot_wind(argv[1:])
        else:
            print('error1')


if __name__ == '__main__':
    #argv：模式名称 %Y%m%d%H 时效 要素 区域名称 层级
    process_plot(sys.argv)
