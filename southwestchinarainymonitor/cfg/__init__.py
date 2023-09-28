#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
   @Project   ：Wiztek.MountainTorrent.SouthWestChina.Py 
   
   @File      ：__init__.py.py
   
   @Author    ：yhaoxian
   
   @Date      ：2022/3/23 19:50 
   
   @Describe  : 
   
"""
import configparser


class Parser(configparser.ConfigParser):
    """
    将.ini文件内容转成dict
    """

    def as_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(d[k])
        return d


class Config(object):
    """

    """
    __species = None

    __first_init = True
    cfg_dict = None

    def __new__(cls, *args, **kwargs):
        if cls.__species is None:
            cls.__species = object.__new__(cls)
        return cls.__species

    def __init__(self, config_path):
        if self.__first_init:
            self.__class__.__first_init = False
            # logger.info("首次加载加载配置文件: {}".format(self.config_path))
            self.config_path = config_path
            self._load_ini_config()

    def _load_ini_config(self):
        """
        加载cfg_main.ini主配置文件
        :param ini_path:
        :return:
        """
        cfg = Parser()
        cfg.read(self.config_path, encoding='utf8')
        self.cfg_dict = cfg.as_dict()

    @classmethod
    def get_instance(cls, *args, **kwargs):
        # 利用反射,看看这个类有没有_instance属性
        if not hasattr(Config, '_instance'):
            Config._instance = Config(*args, **kwargs)
        return Config._instance


if __name__ == "__main__":
    cl = Config()
    pass
