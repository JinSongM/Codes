import re
import numpy as np
from utils import MICAPS4 as M4

p_s = re.compile("\\s+")


def openMicaps14File(file):
    lats = []
    lons = []
    data = []
    # config_data = M4.open_m4("./mask2.result")
    with open(file, "r", encoding="gbk") as content:
        lines = content.readlines()

    startIndex = 0
    endIndex = 0
    for index in range(0, len(lines)):
        if "CLOSED_CONTOURS" in lines[index]:
            startIndex = index + 1
        if "STATION_SITUATION" in lines[index]:
            endIndex = index + 1

    newLines = lines[startIndex: endIndex]
    oneLat = []
    oneLon = []
    for index in range(1, len(newLines) - 1):
        lineArrayTop = p_s.split(newLines[index - 1][0:len(newLines[index - 1]) - 1].strip())
        # lineArrayBottom = p.split(newLines[index + 1][0:len(newLines[index + 1]) - 1].strip())
        lineArray = p_s.split(newLines[index][0:len(newLines[index]) - 1].strip())

        if len(lineArray) == 3 and len(lineArrayTop) == 2:
            # if config_data.get_data(lat=float(lineArray[1]), lon=float(lineArray[0]), bilinear=True) < 50:
            oneLat.append(lineArray[1])
            oneLon.append(lineArray[0])

            data.append(lineArrayTop[0])
            lats.append(oneLat)
            lons.append(oneLon)
            oneLat = []
            oneLon = []
        elif len(lineArray) >= 3:
            for dIdx in range(0, len(lineArray), 3):
                # if config_data.get_data(lat=float(lineArray[dIdx + 1]), lon=float(lineArray[dIdx]),
                #                         bilinear=True) > 50:
                #     continue
                oneLon.append(lineArray[dIdx])
                oneLat.append(lineArray[dIdx + 1])
    return lats, lons, data


def openMicaps3File(file):
    with open(file, "r", encoding="utf8") as content:
        lines = content.readlines()

    data = [p_s.split(line.strip()) for line in lines if len(p_s.split(line.strip())) == 5]

    return data


def openMicaps3FileAsDataframe(file, encoding="utf8"):
    import pandas as pd
    with open(file, "r", encoding=encoding) as content:
        lines = content.readlines()

    data = [p_s.split(line.strip()) for line in lines if len(p_s.split(line.strip())) == 5]
    data = np.array(data, dtype=object)
    df_data = pd.DataFrame({
        "STATION_ID": np.array(data[:, 0], dtype=int),
        "LON": np.array(data[:, 1], dtype=float),
        "LAT": np.array(data[:, 2], dtype=float),
        "ALTI": np.array(data[:, 3], dtype=float),
        "VALUE": np.array(data[:, 4], dtype=float),
    })

    return df_data


def open_Micaps3_as_dict(file, encoding="utf8"):
    """

    Args:
        file:
        encoding:

    Returns:

    """
    with open(file, "r", encoding=encoding) as content:
        lines = content.readlines()
    datas = [p_s.split(line.strip()) for line in lines if len(p_s.split(line.strip())) == 5]
    kv = {}
    for data in datas:
        if data[0] not in kv.keys():
            kv[data[0]] = data[4]
        else:
            continue
    return kv


def openMicaps12File(file):
    with open(file, "r", encoding="utf8") as content:
        lines = content.readlines()
    data = [p_s.split(line.strip()) for line in lines if len(p_s.split(line.strip())) == 12]

    return data


def open_stastic_file(text_file, length=6):
    with open(text_file, "r", encoding="utf8") as content:
        lines = content.readlines()

    data = [p_s.split(line.strip()) for line in lines if
            (len(p_s.split(line.strip())) == length or len(p_s.split(line.strip())) == 2) and ',' not in line]
    new_data = {}
    for dad in data:
        new_data[dad[0]] = dad[1:]
    return new_data

def save_nc(data, lons, lats, filename):
    import netCDF4 as nc
    if data is None:
        raise ValueError("no data")
    da = nc.Dataset(filename, "w")
    da.createDimension("lon", len(lons))
    da.createDimension("lat", len(lats))
    da.createVariable("lon", "f", ("lon",), zlib=True)
    da.createVariable("lat", "f", ("lat",), zlib=True)
    da.variables["lon"][:] = lons
    da.variables["lat"][:] = lats
    da.createVariable("time", "f", ("lat", "lon"), zlib=True)
    da.variables["time"][:] = data
    da.close()