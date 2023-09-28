import glob
import os.path
import sys
from datetime import datetime, timedelta
from verify.plot_met_single import single_plot, plot_wind_speed_single, single_plot_CLDAS, plot_wind_speed_single_CLDAS, plot_station
from multiprocessing import Pool

args = sys.argv
__CONFIG = {
    "CMA_GFS": {
        "folder": "/data/cpvs/DataBase/MOD/CMA_GFS/t2m/{report_time:%Y}/{report_time:%Y%m%d%H}",
        "interval": 12
    },
    "ECMWF": {
        "folder": "/data/cpvs/DataBase/MOD/ECMWF/t2m/{report_time:%Y}/{report_time:%Y%m%d%H}",
        "interval": 12
    },
    "NCEP": {
        "folder": "/data/cpvs/DataBase/MOD/NCEP/t2m/{report_time:%Y}/{report_time:%Y%m%d%H}",
        "interval": 12
    },
    "CMA_MESO": {
        "folder": "/data/cpvs/DataBase/MOD/CMA_MESO/t2m/{report_time:%Y}/{report_time:%Y%m%d%H}",
        "his_count": 3,
        "interval": 12
    },
    "CMA_TYM": {
        "folder": "/data/cpvs/DataBase/MOD/CMA_TYM/t2m/{report_time:%Y}/{report_time:%Y%m%d%H}",
        "interval": 12
    },
    "CLDAS": {
        "folder": "/cpvs/mnt/205/data/model_cldas/CLDAS/TMP/2M_ABOVE_GROUND/{report_time:%Y}/{report_time:%Y%m%d}",
        "interval": 12
    },
    "RAWSH": {
        "folder": "/data/cpvs/DownLoad/OBS/SURF/{report_time:%Y}/{report_time:%Y%m%d}",
        "interval": 12
    }
}

def process_plot(report_time, report_time_cldas, is_overwrite):

    pool = Pool(processes=8)
    _file_path = __CONFIG[args[1]]["folder"].format(report_time=report_time)
    file_list = glob.glob(os.path.join(_file_path, '*'))
    print(len(file_list))
    args_main = []
    if args[1] == 'CLDAS':
        for i in range(2, int(report_time_cldas.hour + 3), 3):
            args_main.append([args[1], report_time, i, is_overwrite])
        res1 = pool.starmap_async(single_plot_CLDAS, args_main)
        res2 = pool.starmap_async(plot_wind_speed_single_CLDAS, args_main)
        res1.get()
        res2.get()
    elif args[1] == 'RAWSH':
        plot_station(report_time-timedelta(hours=12), report_time_cldas-timedelta(hours=12))
    else:
        if len(file_list) > 0:
            for f in file_list:
                cst = int(os.path.basename(f).split(".")[1])
                if cst % 3 == 0 and cst <= 120:
                    args_main.append([args[1], report_time, cst, is_overwrite])
            res1 = pool.starmap_async(plot_wind_speed_single, args_main)
            res2 = pool.starmap_async(single_plot, args_main)
            res1.get()
            res2.get()
    pool.close()
    pool.join()

def process(report_time):
    interval = __CONFIG[args[1]]["interval"]
    report_time_tmp = report_time - timedelta(hours=report_time.hour % interval) - timedelta(hours=4)
    is_overwrite = False
    if len(args) == 5:
        his_count = int(args[3])
        if args[4] == '1':
            is_overwrite = True
    else:
        if "his_count" in __CONFIG[args[1]].keys():
            his_count = __CONFIG[args[1]]["his_count"]
        else:
            his_count = 3
    for idx in range(his_count):
        process_time = report_time_tmp - timedelta(hours=interval*idx)
        process_time_report = report_time - timedelta(hours=interval*idx)
        print(process_time, process_time_report)
        process_plot(process_time, process_time_report, is_overwrite)

if __name__ == '__main__':
    if len(sys.argv) == 5:
        date_start = datetime.strptime(sys.argv[2], "%Y%m%d%H")
        process(date_start)
    if len(sys.argv) == 2:
        date_time = datetime.now()
        process(date_time)