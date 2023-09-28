import xarray as xr


class GridData(object):
    def __init__(self, latitudes, longitudes, grid_data):
        self.latitudes = latitudes
        self.longitudes = longitudes
        self.grid_data = grid_data
        self.xr_data = xr.DataArray(self.grid_data, coords=[latitudes, longitudes], dims=["latitudes", "longitudes"])

    def interp(self, new_latitudes, new_longitudes):
        return self.xr_data.interp(latitudes=new_latitudes, longitudes=new_longitudes).values
