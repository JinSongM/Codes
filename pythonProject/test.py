# -- coding: utf-8 --
# @Time : 2023/7/12 15:59
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : test.py
# @Software: PyCharm
from meteva.base.io import CMADaasAccess
import meteva.base as meb
import cv2, numpy as np

array = np.array([
    [1,2,3,4,5,6],
    [3,2,5,4,6,7],
    [4,5,8,3,4,8],
    [6,7,9,4,3,4],
    [3, 2, 5, 4, 6,5],
])
kernel = np.ones((3, 3), np.uint8)
a = cv2.dilate(np.array(array), kernel)