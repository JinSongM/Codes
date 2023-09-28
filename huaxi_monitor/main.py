#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import shutil
import sys
from datetime import datetime, timedelta
import multiprocessing as mp
import cfg
from utils import log_configure as log, MICAPS
from utils import MICAPS4 as M4
import sta_info
import draw
import FileTools
logger = log.Logger(log_path="./log/main_process")
os.environ['NUMEXPR_MAX_THREADS'] = '16'
cfg_dict = cfg.Config("./config/basic_cfg.ini").cfg_dict
ids, lons, lats, Loc = FileTools.read_station_information("./file/huaxi_stations_south_info.txt", "./file/huaxi_stations_north_info.txt")

obs_data_days = int(cfg_dict["MAIN"]["obs_data_days"])
fst_data_days = int(cfg_dict["MAIN"]["fst_data_days"])

obs_data_path = cfg_dict["INPUT_PATH"]["obs_data_path"]
fst_data_path = cfg_dict["INPUT_PATH"]["fst_data_path"]
collect_fst_path = cfg_dict["INPUT_PATH"]["collect_fst_path"]

obs_data_handle_path = cfg_dict["MIDDLE_PATH"]["obs_data_handle_path"]
fst_data_handle_path = cfg_dict["MIDDLE_PATH"]["fst_data_handle_path"]

obs_fst_data_path = cfg_dict["OUTPUT_PATH"]["obs_fst_data_path"]

pic_output_path = cfg_dict["PIC_OUTPUT_PATH"]["pic_output_path"]


class PathTool:

    def __init__(self, date_time: datetime, start_h: str):
        self.date_time = date_time
        self.start_h = start_h

    def config_obs_path(self):
        """
        配置是实况数据路径
        Returns:

        """
        input_path = ""
        output_path = ""
        if "08" == self.start_h:
            input_path = obs_data_path.format("r24-8")
            output_path = obs_data_handle_path.format("obs_08", self.date_time.year)
        if "20" == self.start_h:
            input_path = obs_data_path.format("r24-20")
            output_path = obs_data_handle_path.format("obs_20", self.date_time.year)
        if not os.path.exists(input_path):
            logger.error("输入目录obs：{} 不存在，程序退出".format(input_path))
            exit(1)
        return input_path, output_path

    def config_fst_path(self):
        """
        配置预报数据路径
        Returns:

        """
        input_path = ""
        output_path = ""
        if "08" == self.start_h:
            input_path = fst_data_path
            output_path = fst_data_handle_path.format("fst_08", self.date_time.year)
        if "20" == self.start_h:
            input_path = fst_data_path
            output_path = fst_data_handle_path.format("fst_20", self.date_time.year)

        if not os.path.exists(input_path):
            logger.error("输入目录fst： {} 不存在，程序退出".format(input_path))
            exit(1)
        return input_path, output_path

    def config_merge_path(self):
        """

        Returns:

        """
        input_path_obs = ""
        input_path_fst = ""
        output_path = ""
        if "08" == self.start_h:
            input_path_obs = obs_data_handle_path.format("obs_08", self.date_time.year)
            input_path_fst = fst_data_handle_path.format("fst_08", self.date_time.year)
            output_path = obs_fst_data_path.format(self.date_time.year, "08")
        if "20" == self.start_h:
            input_path_obs = obs_data_handle_path.format("obs_20", self.date_time.year)
            input_path_fst = fst_data_handle_path.format("fst_20", self.date_time.year)
            output_path = obs_fst_data_path.format(self.date_time.year, "20")

        # if (not os.path.exists(input_path_obs)) or (not os.path.exists(input_path_fst)):
        #     logger.error("输入目录： {} 或者 {} 不存在，程序退出".format(input_path_obs, input_path_fst))
        #     exit(1)

        if os.path.exists(output_path):
            shutil.rmtree(output_path)
            os.makedirs(output_path)
        else:
            os.makedirs(output_path)
        return input_path_obs, input_path_fst, output_path


class MergeStationData:

    def __init__(self, path_obj: PathTool):
        self.path_obj = path_obj
        self.date_time = path_obj.date_time
        self.start_h = path_obj.start_h
        self.sta_data = self._merge_station_obs_and_fst_data()
        # self._writer_data_to_file()

    def _read_obs_data(self):
        logger.info("开始处理实况数据：" + self.date_time.strftime("%Y-%m-%d"))
        input_path, output_path = self.path_obj.config_obs_path()

        obs_end_time = self.date_time - timedelta(days=1)
        logger.info('当前设定计算时间为： ' + obs_end_time.strftime("%Y-%m-%d"))

        station_result = {}
        pool = mp.Pool()
        for sta_id in ids:
            results = []
            # logger.info("处理{}实况数据，站点数据处理进度： ".format(self.start_h) + sta_id + ' %d' % id_num + '/' + '%d' % len(ids))
            tmp_date = obs_end_time.replace(month=7, day=20)
            while tmp_date <= obs_end_time:
                res = pool.apply_async(self._read_obs_data_mp, args=(tmp_date,input_path,sta_id,))
                #res = pool.starmap_async(self._read_obs_data_mp, [tmp_date,input_path,sta_id])
                results.append(res)
                tmp_date += timedelta(days=1)
            Result = [i.get() for i in results]
            station_result[sta_id] = Result
        pool.close()
        pool.join()
        return station_result

    def _read_obs_data_mp(self,tmp_date,input_path,sta_id):
        key = tmp_date.strftime("%y%m%d")
        file_name = key + self.start_h + ".000"
        file_path = os.path.join(input_path, file_name)
        #logger.info(file_name)
        if os.path.exists(file_path):
            try:
                sta_data_dict = MICAPS.open_Micaps3_as_dict(file_path, encoding="gbk")
                if sta_id in sta_data_dict.keys():
                    result = key + '\t' + sta_data_dict.get(sta_id) + '\n'
                else:
                    result = key + "\t" + '0.0' + '\n'
                return result
            except Exception as ex:
                logger.error("读取文件报错", ex)
                exit(1)
        else:
            result = key + '\t' + '0.0' + '\n'
            return result
    # def _read_fst_data(self):
    #     logger.info("开始处理是预报数据：" + self.date_time.strftime("%Y-%m-%d"))
    #     input_path, output_path = self.path_obj.config_fst_path()
    #     fst_begin_time = self.date_time - timedelta(days=0)
    #     # logger.info('当前设定计算时间为： ' + fst_begin_time.strftime("%Y-%m-%d"))
    #
    #     results = {}
    #     for i in range(0, fst_data_days):
    #         fst_time = (fst_begin_time + timedelta(days=i)).strftime("%y%m%d")
    #         fst_time2 = fst_begin_time.strftime("%Y%m%d")
    #         file_name = "grid24_" + fst_time2 + self.start_h + ".{cst:03d}".format(cst = 24 * (i+1))
    #         logger.info(fst_time + "   " + file_name)
    #         file_path = os.path.join(input_path, file_name)
    #         sta_tp = {}
    #         if not os.path.exists(file_path):
    #             for idx in range(0, len(ids)):
    #                 sta_id = ids[idx]
    #                 sta_tp[sta_id] = 0
    #         else:
    #             lat_lon_data = M4.open_m4(file_path, encoding="utf8")
    #             for idx in range(0, len(ids)):
    #                 sta_id = ids[idx]
    #                 sta_tp[sta_id] = lat_lon_data.get_data(lats[idx], lons[idx], bilinear=False)
    #         results[fst_time] = sta_tp
    #
    #     station_result = {}
    #     for sta_id in ids:
    #         fst_result = []
    #         for i in range(0, fst_data_days):
    #             fst_time = (fst_begin_time + timedelta(days=i)).strftime("%y%m%d")
    #             fst_result.append(fst_time + '\t' + str(results[fst_time][sta_id]) + '\n')
    #         station_result[sta_id] = fst_result
    #     return station_result

    #多线程跑预报数据
    def _read_fst_data(self):
        logger.info("开始处理预报数据：" + self.date_time.strftime("%Y-%m-%d"))
        input_path, output_path = self.path_obj.config_fst_path()
        fst_begin_time = self.date_time - timedelta(days=0)
        # logger.info('当前设定计算时间为： ' + fst_begin_time.strftime("%Y-%m-%d"))
        results = []
        results_mp = {}

        pool = mp.Pool()
        for i in range(0, fst_data_days):
            res = pool.apply_async(self._read_fst_data_mp, args=(i, fst_begin_time, input_path,))
            results.append(res)

        Result = [i.get() for i in results]
        for i in Result:
            results_mp[i[0]] = i[1]

        pool.close()
        pool.join()

        station_result = {}
        for sta_id in ids:
            fst_result = []
            for i in range(0, fst_data_days):
                fst_time = (fst_begin_time + timedelta(days=i)).strftime("%y%m%d")
                fst_result.append(fst_time + '\t' + str(results_mp[fst_time][sta_id]) + '\n')
            station_result[sta_id] = fst_result
        return station_result

    def _read_fst_data_mp(self, i, fst_begin_time, input_path):
        fst_time = (fst_begin_time + timedelta(days=i)).strftime("%y%m%d")
        fst_time2 = fst_begin_time.strftime("%Y%m%d")
        file_name = "grid24_" + fst_time2 + self.start_h + ".{cst:03d}".format(cst = 24 * (i+1))
        file_path = os.path.join(input_path, file_name)
        sta_tp = {}
        if not os.path.exists(file_path):
            for idx in range(0, len(ids)):
                sta_id = ids[idx]
                sta_tp[sta_id] = 0
        else:
            lat_lon_data = M4.open_m4(file_path, encoding="utf8")
            for idx in range(0, len(ids)):
                sta_id = ids[idx]
                sta_tp[sta_id] = lat_lon_data.get_data(lats[idx], lons[idx], bilinear=False)
        return fst_time, sta_tp


    def _merge_station_obs_and_fst_data(self):
        obs_data = self._read_obs_data()
        fst_data = self._read_fst_data()
        sta_data = {}
        for sta_id in ids:
            sta_data[sta_id] = obs_data[sta_id] + fst_data[sta_id]
        return sta_data


    def _writer_data_to_file(self):
        _, _, output_path = self.path_obj.config_merge_path()
        for sta_id in ids:
            f = open(output_path + str(sta_id) + ".txt", "w")
            f.writelines(self.sta_data[sta_id])
            f.close()


def prepare_station_obs_and_fst_data(date_time: datetime, start_h: str):
    """
    根据日期准备站点数据：  前n天的实况数据，后10天的智能网格数据
    Args:
        date_time:
        start_h:

    Returns:

    """
    path_obj = PathTool(date_time, start_h)
    sta_infomation = MergeStationData(path_obj)

    sta_obj_list = []
    sta_obj_dict = {}
    for i in range(0, len(ids)):

        sta_obj = sta_info.StationInfo(ids[i], lons[i], lats[i], Loc[i], date_time, start_h, sta_infomation.sta_data[ids[i]])
        sta_obj_list.append(sta_obj.data)

    for k in sta_obj_list[0].keys():
        sta_value = []
        for sta_obj_sub in sta_obj_list:
            sta_value.append(sta_obj_sub[k])
        sta_obj_dict[k] = sta_value

    sta_08_obj = sta_info.StationInfo_08(sta_obj_dict, date_time, start_h, collect_fst_path)
    return sta_08_obj


def process(date_time: datetime):
    """
    程序运行流程： 准备数据->计算站点的预计
    Args:
        date_time:

    Returns:

    """
    try:
        # 准备实况数据08时起报时间
        sta_obj_list_08 = prepare_station_obs_and_fst_data(date_time, "08")
        pic_task_obj_08 = draw.PictureDrawTask(sta_obj_list_08, date_time, "08", pic_output_path)
        pic_task_obj_08.pic_draw_1()
        pic_task_obj_08.pic_draw_2()
        pic_task_obj_08.pic_draw_3()
        pic_task_obj_08.pic_draw_4()
        pic_task_obj_08.pic_draw_5()
        pic_task_obj_08.pic_draw_6()
        pic_task_obj_08.pic_draw_7()

        # # 准备预报数据20时起报时间
        # sta_obj_list_20 = prepare_station_obs_and_fst_data(date_time, "20")
        # pic_task_obj_20 = draw.PictureDrawTask(sta_obj_list_20, date_time, "20", pic_output_path)
        # pic_task_obj_20.pic_draw_1()
        # pic_task_obj_20.pic_draw_2()
        # pic_task_obj_20.pic_draw_3()
        # pic_task_obj_20.pic_draw_4()
        # pic_task_obj_20.pic_draw_5()
        # pic_task_obj_20.pic_draw_6()
        # pic_task_obj_20.pic_draw_7()
    except Exception as ex:
        logger.error(ex)


if __name__ == '__main__':
    if len(sys.argv) == 3:
        date_start = datetime.strptime(sys.argv[1], "%Y%m%d")
        date_end = datetime.strptime(sys.argv[2], "%Y%m%d")
        while date_start <= date_end:
            process(date_start)
            date_start += timedelta(days=1)
    if len(sys.argv) == 2:
        date_start = datetime.strptime(sys.argv[1], "%Y%m%d")
        date_end = datetime.strptime(sys.argv[1], "%Y%m%d")
        while date_start <= date_end:
            process(date_start)
            date_start += timedelta(days=1)
    if len(sys.argv) == 1:
        date_time = datetime(datetime.now().year, datetime.now().month, datetime.now().day)
        process(date_time)