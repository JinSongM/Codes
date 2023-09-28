import numpy as np
from metpy import calc as mp_calc
from metpy.units import units


def calc_wind_dir_and_wind_speed(u_data, v_data):
    u = u_data * units("m/s")
    v = v_data * units("m/s")
    return np.array(mp_calc.wind_direction(u, v),dtype=float), np.array(mp_calc.wind_speed(u, v),dtype=float)


def calc_relative_humidity(t_data, d_data):
    """

    :param t_data: 单位：℃
    :param d_data:单位：℃
    :return:
    """
    return np.array(mp_calc.relative_humidity_from_dewpoint(t_data * units.degC, d_data * units.degC),dtype=float)


def calc_change_temperature(t_data, t_data_pre):
    return t_data - t_data_pre


def calc_pre(tp_data, tp_data_pre):
    return tp_data - tp_data_pre
