import sys
from verify.plot_ms_DF import single_plot_CLDAS

Dict = ['tem', 'tem_max', 'tem_change', 'r', 'pre24_hgt', 'pre03', 'pre06', 'pre12',
        'sf24', 'tem_change_48','pre12_cp', 'pre24_cp', 'pre24_lsp']

def process_plot(argv):
    if argv[4] in Dict:
        single_plot_CLDAS(argv[1:])
    else:
        print('error1')

if __name__ == '__main__':
    #argv：模式名称 实况时间：%Y%m%d%H 时效 要素 区域名称
    process_plot(sys.argv)