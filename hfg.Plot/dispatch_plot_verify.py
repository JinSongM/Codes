import glob
import os.path
import sys
from datetime import datetime, timedelta
from verify.plot_met import plot_wind_speed, plot_wind
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
        "interval": 12
    },
    "CMA_TYM": {
        "folder": "/data/cpvs/DataBase/MOD/CMA_TYM/t2m/{report_time:%Y}/{report_time:%Y%m%d%H}",
        "interval": 12
    },
    "FNL": {
        "folder": "/data/cpvs/DataBase/OBS/FNL/gh/500/{report_time:%Y}/{report_time:%Y%m%d%H}",
        "interval": 12
    },
    "ERA5": {
        "folder": "/data/cpvs/DataBase/OBS/ERA5/gh/500/{report_time:%Y}/{report_time:%Y%m%d%H}",
        "interval": 12
    }
}

def process_plot(report_time, is_overwrite):
    pool = Pool(processes=10)
    days_limit = {'ERA5': 7, 'FNL': 2}
    if args[1] == 'ERA5' or args[1] == 'FNL':
        args_main = []
        report_time_OBS = report_time - timedelta(days=days_limit.get(args[1]))
        print(report_time_OBS)
        start_hours = report_time_OBS.replace(hour=2)
        while start_hours <= (report_time_OBS + timedelta(hours=3)):
            args_main.append([args[1], start_hours, 0, is_overwrite])
            start_hours += timedelta(hours=3)
        res1 = pool.starmap_async(plot_wind_speed, args_main)
        res2 = pool.starmap_async(plot_wind, args_main)
        res1.get()
        res2.get()
        pool.close()
        pool.join()
    else:
        _file_path = __CONFIG[args[1]]["folder"].format(report_time=report_time)
        print(report_time)
        file_list = glob.glob(_file_path + "/*")
        if len(file_list) > 0:
            args_main = []
            for f in file_list:
                cst = int(os.path.basename(f).split(".")[1])
                if cst % 3 == 0 and cst <= 120:
                    args_main.append([args[1], report_time, cst, is_overwrite])
            res1 = pool.starmap_async(plot_wind_speed, args_main)
            res2 = pool.starmap_async(plot_wind, args_main)
            res1.get()
            res2.get()
        pool.close()
        pool.join()


def process(report_time):
    interval = __CONFIG[args[1]]["interval"]
    report_time = report_time - timedelta(hours=report_time.hour % interval) - timedelta(hours=4)
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
        process_time = report_time - timedelta(hours=interval*idx)
        process_plot(process_time, is_overwrite)

if __name__ == '__main__':
    if len(sys.argv) == 5:
        date_start = datetime.strptime(sys.argv[2], "%Y%m%d%H")
        process(date_start)
    if len(sys.argv) == 2:
        date_time = datetime.now()
        process(date_time)
