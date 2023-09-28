
def calc(v00, v01, v10, v11, y, x):
    v0x = (v01 - v00) * x + v00
    v1x = (v11 - v10) * x + v10
    vyx = (v1x - v0x) * y + v0x
    return vyx