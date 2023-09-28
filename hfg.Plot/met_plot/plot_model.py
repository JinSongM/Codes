import os.path
from verify.config import *
from verify.plot_model_single import *
from metdig.graphics.text_method import *
from metdig.graphics.contourf_method import *
from metdig.graphics.barbs_method import *
from metdig.graphics.contour_method import *
from metdig.graphics.pcolormesh_method import *
from metdig.graphics.draw_compose import *


class PlotHgtWindProd:
    def __init__(self, model_name, hgt, u, v):
        """

        :param hgt:
        :param u:
        :param v:
        """
        self.gh = metdig.utl.xrda_to_gridstda(hgt, level_dim='level', time_dim='time', lat_dim='lat',
                                              lon_dim='lon', dtime_dim='dtime',
                                              var_name='gh', np_input_units='hPa')
        self.u = metdig.utl.xrda_to_gridstda(u, level_dim='level', time_dim='time', lat_dim='lat',
                                             lon_dim='lon', dtime_dim='dtime',
                                             var_name='u', np_input_units='m/s')
        self.v = metdig.utl.xrda_to_gridstda(v, level_dim='level', time_dim='time', lat_dim='lat',
                                             lon_dim='lon', dtime_dim='dtime',
                                             var_name='v', np_input_units='m/s')
        self.wind_speed = other.wind_speed(self.u, self.v)
        hgt.close()
        u.close()
        v.close()
        self.model_name = model_name
        if model_name == 'ERA5' or model_name == 'FNL':
            self.path = MODEL_SAVE_OUT_OBS
        else:
            self.path = MODEL_SAVE_OUT

    def plot_hgt_wind_speed(self, report_time, cst, out_name, region_name, region, lev, is_overwrite=False):
        """
        高度场和风场
        :param lev:
        :param report_time:
        :param cst:
        :param out_name:
        :param region_name:
        :param region:
        :return:
        """
        file_path = self.path.format(model=self.model_name, report_time=report_time, cst=cst, lev=lev,
                                     out_name=out_name, region=region_name)
        if os.path.exists(file_path) and is_overwrite==False:
            return
        draw_hgt_uv_wsp_588(self.gh, self.u, self.v, self.wind_speed, map_extent=region, region=region_name, lev=lev,
                            output_dir=os.path.dirname(file_path), is_overwrite=is_overwrite,
                            png_name=os.path.basename(file_path), is_clean_plt=True, add_city=False)

    def plot_hgt_wind_msl(self, msl, report_time, cst, out_name, region_name, region, lev, is_overwrite=False):
        """
        形势场、风场、海平面气压
        :param lev:
        :param msl:
        :param report_time:
        :param cst:
        :param out_name:
        :param region_name:
        :param region:
        :return:
        """
        file_path = self.path.format(model=self.model_name, report_time=report_time, cst=cst, lev=lev,
                                     out_name=out_name, region=region_name)
        if os.path.exists(file_path) and is_overwrite==False:
            return
        std_data = metdig.utl.xrda_to_gridstda(msl, level_dim='level', time_dim='time', lat_dim='lat',
                                               lon_dim='lon', dtime_dim='dtime',
                                               var_name='msl', np_input_units='hPa')
        msl.close()
        draw_hgt_uv_prmsl_588(self.gh, self.u, self.v, std_data, map_extent=region, region=region_name,
                              output_dir=os.path.dirname(file_path),
                              png_name=os.path.basename(file_path), is_clean_plt=True, add_city=False)
        std_data.close()

    def plot_hgt_wind_cape(self, cape, report_time, cst, out_name, region_name, region, lev, is_overwrite=False):
        """
        对流有效位能
        :param lev:
        :param cape:
        :param report_time:
        :param cst:
        :param out_name:
        :param region_name:
        :param region:
        :return:
        """
        file_path = self.path.format(model=self.model_name, report_time=report_time, cst=cst, lev=lev,
                                     out_name=out_name, region=region_name)
        if os.path.exists(file_path) and is_overwrite==False:
            return
        std_data = metdig.utl.xrda_to_gridstda(cape, level_dim='level', time_dim='time', lat_dim='lat',
                                               lon_dim='lon', dtime_dim='dtime',
                                               var_name='msl', np_input_units='g/kg')
        cape.close()
        draw_hgt_uv_cape_588(self.gh, self.u, self.v, std_data, map_extent=region, region=region_name,
                             output_dir=os.path.dirname(file_path),
                             png_name=os.path.basename(file_path), is_clean_plt=True, add_city=False)
        std_data.close()

    def plot_hgt_wind_rcr(self, radar, report_time, cst, out_name, region_name, region, lev, is_overwrite=False):
        """
        雷达组合反射率
        :param lev:
        :param cape:
        :param report_time:
        :param cst:
        :param out_name:
        :param region_name:
        :param region:
        :return:
        """
        file_path = self.path.format(model=self.model_name, report_time=report_time, cst=cst, lev=lev,
                                     out_name=out_name, region=region_name)
        if os.path.exists(file_path) and is_overwrite==False:
            return
        std_data = metdig.utl.xrda_to_gridstda(radar, level_dim='level', time_dim='time', lat_dim='lat',
                                               lon_dim='lon', dtime_dim='dtime',
                                               var_name='cref')
        radar.close()
        draw_hgt_uv_rcr_588(self.gh, self.u, self.v, std_data, map_extent=region, region=region_name,
                            output_dir=os.path.dirname(file_path),
                            png_name=os.path.basename(file_path), is_clean_plt=True, add_city=False)
        std_data.close()

    def plot_rcr(self, radar, report_time, cst, out_name, region_name, region, lev, is_overwrite=False):
        """
        雷达组合反射率
        :param lev:
        :param cape:
        :param report_time:
        :param cst:
        :param out_name:
        :param region_name:
        :param region:
        :return:
        """
        file_path = self.path.format(model=self.model_name, report_time=report_time, cst=cst, lev=lev,
                                     out_name=out_name, region=region_name)
        if os.path.exists(file_path) and is_overwrite==False:
            return
        std_data = metdig.utl.xrda_to_gridstda(radar, level_dim='level', time_dim='time', lat_dim='lat',
                                               lon_dim='lon', dtime_dim='dtime',
                                               var_name='cref')
        radar.close()
        draw_rcr_588(self.gh, self.u, self.v, std_data, map_extent=region, region=region_name,
                     output_dir=os.path.dirname(file_path),
                     png_name=os.path.basename(file_path), is_clean_plt=True, add_city=False)
        std_data.close()

    def plot_hgt_wind_ct(self, ct, report_time, cst, out_name, region_name, region, lev, is_overwrite=False):
        """
        形势场、风场、云顶高度
        :param lev:
        :param msl:
        :param report_time:
        :param cst:
        :param out_name:
        :param region_name:
        :param region:
        :return:
        """
        file_path = self.path.format(model=self.model_name, report_time=report_time, cst=cst, lev=lev,
                                     out_name=out_name, region=region_name)
        if os.path.exists(file_path) and is_overwrite==False:
            return
        std_data = metdig.utl.xrda_to_gridstda(ct, level_dim='level', time_dim='time', lat_dim='lat',
                                               lon_dim='lon', dtime_dim='dtime', np_input_units='km')
        ct.close()
        draw_hgt_uv_ct_588(self.gh, self.u, self.v, std_data, map_extent=region, region=region_name,
                           output_dir=os.path.dirname(file_path),
                           png_name=os.path.basename(file_path), is_clean_plt=True, add_city=False)
        std_data.close()

    def plot_hgt_wind_t(self, t, report_time, cst, out_name, region_name, region, lev, levels, cmap, is_overwrite=False):
        """
        850温度
        :param lev:
        :param t:
        :param report_time:
        :param cst:
        :param out_name:
        :param region_name:
        :param region:
        :return:
        """
        file_path = self.path.format(model=self.model_name, report_time=report_time, cst=cst, lev=lev,
                                     out_name=out_name, region=region_name)
        if os.path.exists(file_path) and is_overwrite==False:
            return
        std_data = metdig.utl.xrda_to_gridstda(t, level_dim='level', time_dim='time', lat_dim='lat',
                                               lon_dim='lon', dtime_dim='dtime',
                                               var_name='tmp', np_input_units='degC')
        t.close()
        draw_hgt_uv_t_588(self.gh, self.u, self.v, std_data, map_extent=region, levels=levels, region=region_name,
                          output_dir=os.path.dirname(file_path), cmap=cmap,
                          png_name=os.path.basename(file_path), is_clean_plt=True, add_city=False)
        std_data.close()

    def plot_hgt_wind_k(self, k, report_time, cst, out_name, region_name, region, lev, is_overwrite=False):
        """
        k指数
        :param lev:
        :param k:
        :param report_time:
        :param cst:
        :param out_name:
        :param region_name:
        :param region:
        :return:
        """
        file_path = self.path.format(model=self.model_name, report_time=report_time, cst=cst, lev=lev,
                                     out_name=out_name, region=region_name)
        if os.path.exists(file_path) and is_overwrite==False:
            return
        std_data = metdig.utl.xrda_to_gridstda(k, level_dim='level', time_dim='time', lat_dim='lat',
                                               lon_dim='lon', dtime_dim='dtime',
                                               var_name='k_idx', np_input_units='K')
        k.close()
        draw_hgt_uv_k_588(self.gh, self.u, self.v, std_data, map_extent=region, region=region_name,
                          output_dir=os.path.dirname(file_path),
                          png_name=os.path.basename(file_path), is_clean_plt=True, add_city=False)
        std_data.close()

    def plot_hgt_wind_hpbl(self, hpbl, report_time, cst, out_name, region_name, region, lev, is_overwrite=False):
        """
        边界层高度
        :param lev:
        :param hpbl:
        :param report_time:
        :param cst:
        :param out_name:
        :param region_name:
        :param region:
        :return:
        """
        file_path = self.path.format(model=self.model_name, report_time=report_time, cst=cst, lev=lev,
                                     out_name=out_name, region=region_name)
        if os.path.exists(file_path) and is_overwrite==False:
            return
        std_data = metdig.utl.xrda_to_gridstda(hpbl, level_dim='level', time_dim='time', lat_dim='lat',
                                               lon_dim='lon', dtime_dim='dtime', np_input_units='m')
        hpbl.close()
        draw_hgt_uv_hpbl_588(self.gh, self.u, self.v, std_data, map_extent=region, region=region_name,
                             output_dir=os.path.dirname(file_path),
                             png_name=os.path.basename(file_path), is_clean_plt=True, add_city=False)
        std_data.close()

    def plot_hgt_wind_spfh(self, q, report_time, cst, out_name, region_name, region, lev, is_overwrite=False):
        """
        形势场、风场、比湿
        :param lev:
        :param q:
        :param report_time:
        :param cst:
        :param out_name:
        :param region_name:
        :param region:
        :return:
        """
        file_path = self.path.format(model=self.model_name, report_time=report_time, cst=cst, lev=lev,
                                     out_name=out_name, region=region_name)
        if os.path.exists(file_path) and is_overwrite==False:
            return
        std_data = metdig.utl.xrda_to_gridstda(q, level_dim='level', time_dim='time', lat_dim='lat',
                                               lon_dim='lon', dtime_dim='dtime',
                                               var_name='q', np_input_units='%')
        q.close()
        draw_hgt_uv_spfh_588(self.gh, self.u, self.v, std_data, map_extent=region, region=region_name,
                             output_dir=os.path.dirname(file_path),
                             png_name=os.path.basename(file_path), is_clean_plt=True, add_city=False)
        std_data.close()

    def plot_hgt_wind_rh(self, rh, report_time, cst, out_name, region_name, region, lev, is_overwrite=False):
        """
        高度场、风场、相对湿度
        :param lev:
        :param rh:
        :param report_time:
        :param cst:
        :param out_name:
        :param region_name:
        :param region:
        :return:
        """

        file_path = self.path.format(model=self.model_name, report_time=report_time, cst=cst, lev=lev,
                                     out_name=out_name, region=region_name)
        if os.path.exists(file_path) and is_overwrite==False:
            return
        std_data = metdig.utl.xrda_to_gridstda(rh, level_dim='level', time_dim='time', lat_dim='lat',
                                               lon_dim='lon', dtime_dim='dtime',
                                               var_name='rh', np_input_units='%')
        rh.close()
        draw_hgt_uv_rh_588(self.gh, self.u, self.v, std_data, map_extent=region, region=region_name,
                           output_dir=os.path.dirname(file_path),
                           png_name=os.path.basename(file_path), is_clean_plt=True, add_city=False)
        std_data.close()

    def plot_hgt_wind_wvfl(self, q, report_time, cst, out_name, region_name, region, lev, is_overwrite=False):
        """
        形势场风场和水汽通量
        :param lev:
        :param q:
        :param report_time:
        :param cst:
        :param out_name:
        :param region_name:
        :param region:
        :return:
        """
        file_path = self.path.format(model=self.model_name, report_time=report_time, cst=cst, lev=lev,
                                     out_name=out_name, region=region_name)
        if os.path.exists(file_path) and is_overwrite==False:
            return
        q_std_data = metdig.utl.xrda_to_gridstda(q, level_dim='level', time_dim='time', lat_dim='lat',
                                                 lon_dim='lon', dtime_dim='dtime',
                                                 var_name='spfh', np_input_units='g/kg')
        q.close()
        wvf1 = metdig.cal.moisture.cal_ivt_singlelevel(q_std_data, self.wind_speed)
        draw_hgt_uv_wvfl_588(self.gh, self.u, self.v, wvf1, map_extent=region, region=region_name,
                             output_dir=os.path.dirname(file_path),
                             png_name=os.path.basename(file_path), is_clean_plt=True, add_city=False)
        wvf1.close()

    def plot_hgt_wind_wvfldiv(self, q, report_time, cst, out_name, region_name, region, lev, is_overwrite=False):
        """
        形势场风场和水汽通量散度
        :param lev:
        :param q:
        :param report_time:
        :param cst:
        :param out_name:
        :param region_name:
        :param region:
        :return:
        """
        file_path = self.path.format(model=self.model_name, report_time=report_time, cst=cst, lev=lev,
                                     out_name=out_name, region=region_name)
        if os.path.exists(file_path) and is_overwrite==False:
            return
        q_std_data = metdig.utl.xrda_to_gridstda(q, level_dim='level', time_dim='time', lat_dim='lat',
                                                 lon_dim='lon', dtime_dim='dtime',
                                                 var_name='spfh', np_input_units='g/kg')
        q.close()
        wvfldiv = metdig.cal.moisture.water_wapor_flux_divergence(self.u, self.v, q_std_data)
        draw_hgt_uv_wvfldiv_588(self.gh, self.u, self.v, wvfldiv, map_extent=region, region=region_name,
                                output_dir=os.path.dirname(file_path),
                                png_name=os.path.basename(file_path), is_clean_plt=True, add_city=False)
        wvfldiv.close()

    def plot_hgt_wind_tcwv(self, tcwv, report_time, cst, out_name, region_name, region, lev, is_overwrite=False):
        """
        形势场风场和整层可降水量
        :param lev:
        :param q:
        :param report_time:
        :param cst:
        :param out_name:
        :param region_name:
        :param region:
        :return:
        """
        file_path = self.path.format(model=self.model_name, report_time=report_time, cst=cst, lev=lev,
                                     out_name=out_name, region=region_name)
        if os.path.exists(file_path) and is_overwrite==False:
            return
        tcwv_std_data = metdig.utl.xrda_to_gridstda(tcwv, level_dim='level', time_dim='time', lat_dim='lat',
                                                    lon_dim='lon', dtime_dim='dtime',
                                                    var_name='q', np_input_units='%')
        tcwv.close()
        draw_hgt_uv_tcwv_588(self.gh, self.u, self.v, tcwv_std_data, map_extent=region, region=region_name,
                             output_dir=os.path.dirname(file_path),
                             png_name=os.path.basename(file_path), is_clean_plt=True, add_city=False)
        tcwv_std_data.close()

    def __del__(self):
        try:
            self.u.close()
            self.v.close()
            self.gh.close()
            self.wind_speed.close()
        except BaseException:
            pass


def draw_hgt_uv_wsp_588(hgt, u, v, wsp, map_extent=(60, 145, 15, 55), region=None, lev=None,
                        wsp_pcolormesh_kwargs={}, uv_barbs_kwargs={}, hgt_contour_kwargs={},
                        **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    data_name = str(hgt['member'].values[0])
    title = '[{}] {}hPa 位势高度场, {}hPa 风场, 风速'.format(
        data_name.upper(),
        hgt['level'].values[0],
        u['level'].values[0])

    forcast_info = hgt.stda.description()
    png_name = '{2}_位势高度场_风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.jpg'.format(init_time, fhour,
                                                                                        data_name.upper())
    # if region == 'NH':
    #     central_longitude = 120
    #     step = 30
    # else:
    #     central_longitude = 0
    #     step = 10
    fig, ax = horizontal_pallete_test(map_extent=map_extent, crs=ccrs.PlateCarree(central_longitude=0),
                                      forcast_info=forcast_info)
    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent,
                             add_tag=False, fig=fig, ax=ax, kwargs=pallete_kwargs)
    obj.ax.tick_params(labelsize=16)

    if (lev == 100) | (lev == 200):
        levels = [30, 31, 32, 33, 34, 35, 36, 37, 38, 39]
    else:
        levels = [4, 8, 12, 16, 20, 24, 28, 32, 36, 40]

    wsp_pcolormesh(obj.ax, wsp, levels=levels,
                   colorbar_kwargs={'pad': 0.05, 'extend': 'both'}, alpha=1, cmap='ncl/wind_17lev')
    if region == 'NW':
        regrid_shape = 10
    else:
        regrid_shape = 20
    uv_barbs(obj.ax, u, v, regrid_shape=regrid_shape, sizes=dict(emptybarb=0), kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, levels=contour_levels, kwargs=hgt_contour_kwargs)
    hgt_contour_588(obj.ax, hgt)
    obj.save()


def draw_hgt_uv_prmsl_588(hgt, u, v, prmsl, map_extent=(60, 145, 15, 55), marke_hl=True, region=None,
                          prmsl_contourf_kwargs={}, uv_barbs_kwargs={}, hgt_contour_kwargs={},
                          **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    data_name = str(hgt['member'].values[0])
    title = '[{}] {}hPa 位势高度场, {}hPa 风场, 海平面气压场'.format(
        data_name.upper(),
        hgt['level'].values[0],
        u['level'].values[0])

    forcast_info = hgt.stda.description()
    png_name = '{2}_位势高度场_风场_海平面气压场_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour,
                                                                                                data_name.upper())
    # if region == 'NH':
    #     central_longitude = 120
    #     step = 30
    # else:
    #     central_longitude = 0
    #     step = 10
    fig, ax = horizontal_pallete_test(map_extent=map_extent, crs=ccrs.PlateCarree(central_longitude=0),
                                      forcast_info=forcast_info)
    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent,
                             add_tag=False, fig=fig, ax=ax, kwargs=pallete_kwargs)
    obj.ax.tick_params(labelsize=16)
    prmsl_contourf(obj.ax, prmsl, cmap='PiYG', alpha=1, colorbar_kwargs={'pad': 0.05}, kwargs=prmsl_contourf_kwargs)
    if region == 'NW':
        regrid_shape = 10
    else:
        regrid_shape = 20
    uv_barbs(obj.ax, u, v, regrid_shape=regrid_shape, sizes=dict(emptybarb=0), kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, levels=contour_levels, kwargs=hgt_contour_kwargs)
    hgt_contour_588(obj.ax, hgt)
    if (marke_hl):
        mslp_highlower_center_text(obj.ax, prmsl, map_extent)
    obj.save()


def draw_hgt_uv_cape_588(hgt, u, v, cape, map_extent=(60, 145, 15, 55), region=None,
                         cape_pcolormesh_kwargs={}, uv_barbs_kwargs={}, hgt_contour_kwargs={},
                         **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    data_name = str(hgt['member'].values[0])

    title = '[{}] {}hPa 位势高度, {}hPa 风, 对流有效位能'.format(
        data_name.upper(),
        hgt['level'].values[0],
        u['level'].values[0],
    )
    forcast_info = hgt.stda.description()
    png_name = '{2}_位势高度_风_对流有效位能_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour,
                                                                                              data_name.upper())
    # if region == 'NH':
    #     central_longitude = 120
    #     step = 30
    # else:
    #     central_longitude = 0
    #     step = 10
    fig, ax = horizontal_pallete_test(map_extent=map_extent, crs=ccrs.PlateCarree(central_longitude=0),
                                      forcast_info=forcast_info)
    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent,
                             add_tag=False, fig=fig, ax=ax,
                             kwargs=pallete_kwargs)
    obj.ax.tick_params(labelsize=16)
    cape_pcolormesh(obj.ax, cape, levels=[200, 400, 600, 800, 1000, 1500, 2000, 2500, 3000, 3500, 4000],
                    cmap=cmap_cape_850, alpha=1, colorbar_kwargs={'pad': 0.05, 'extend': 'max'})
    if region == 'NW':
        regrid_shape = 10
    else:
        regrid_shape = 20
    uv_barbs(obj.ax, u, v, regrid_shape=regrid_shape, sizes=dict(emptybarb=0), kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, levels=contour_levels, kwargs=hgt_contour_kwargs)
    hgt_contour_588(obj.ax, hgt)
    obj.save()


def draw_hgt_uv_rcr_588(hgt, u, v, radar, map_extent=(60, 145, 15, 55), region=None,
                        cape_pcolormesh_kwargs={}, uv_barbs_kwargs={}, hgt_contour_kwargs={},
                        **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    data_name = str(hgt['member'].values[0])
    title = '[{}] {}hPa 位势高度, {}hPa 风, 雷达组合反射率'.format(
        data_name.upper(),
        hgt['level'].values[0],
        u['level'].values[0],
    )
    forcast_info = hgt.stda.description()
    png_name = '{2}_位势高度_风_雷达组合反射率_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour,
                                                                                               data_name.upper())
    # if region == 'NH':
    #     central_longitude = 120
    #     step = 30
    # else:
    #     central_longitude = 0
    #     step = 10
    fig, ax = horizontal_pallete_test(map_extent=map_extent, crs=ccrs.PlateCarree(central_longitude=0),
                                      forcast_info=forcast_info)
    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent,
                             add_tag=False, fig=fig, ax=ax,
                             kwargs=pallete_kwargs)

    obj.ax.tick_params(labelsize=16)
    if region == 'NW':
        regrid_shape = 10
    else:
        regrid_shape = 20
    cref_pcolormesh(obj.ax, radar, colorbar_kwargs={'pad': 0.05}, kwargs=cape_pcolormesh_kwargs)
    uv_barbs(obj.ax, u, v, regrid_shape=regrid_shape, sizes=dict(emptybarb=0), kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, levels=contour_levels, kwargs=hgt_contour_kwargs)
    hgt_contour_588(obj.ax, hgt)
    obj.save()


def draw_rcr_588(hgt, u, v, radar, map_extent=(60, 145, 15, 55), region=None,
                 cape_pcolormesh_kwargs={}, uv_barbs_kwargs={}, hgt_contour_kwargs={},
                 **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    data_name = str(hgt['member'].values[0])
    title = '[{}] 雷达组合反射率'.format(
        data_name.upper(),
    )
    forcast_info = hgt.stda.description()
    png_name = '{2}_雷达组合反射率_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour,
                                                                                        data_name.upper())
    # if region == 'NH':
    #     central_longitude = 120
    #     step = 30
    # else:
    #     central_longitude = 0
    #     step = 10
    fig, ax = horizontal_pallete_test(map_extent=map_extent, crs=ccrs.PlateCarree(central_longitude=0),
                                      forcast_info=forcast_info)
    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent,
                             add_tag=False, fig=fig, ax=ax,
                             kwargs=pallete_kwargs)

    obj.ax.tick_params(labelsize=16)
    cref_pcolormesh(obj.ax, radar, colorbar_kwargs={'pad': 0.05}, kwargs=cape_pcolormesh_kwargs)
    obj.save()


def draw_hgt_uv_k_588(hgt, u, v, k, map_extent=(60, 145, 15, 55), region=None,
                      **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    data_name = str(hgt['member'].values[0])

    title = '[{}] {}hPa 位势高度, {}hPa 风, k指数'.format(
        data_name.upper(),
        hgt['level'].values[0],
        u['level'].values[0],
    )
    forcast_info = hgt.stda.description()
    png_name = '{2}_位势高度_风_k指数_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour,
                                                                                           data_name.upper())
    # if region == 'NH':
    #     central_longitude = 120
    #     step = 30
    # else:
    #     central_longitude = 0
    #     step = 10
    fig, ax = horizontal_pallete_test(map_extent=map_extent, crs=ccrs.PlateCarree(central_longitude=0),
                                      forcast_info=forcast_info)
    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent,
                             add_tag=False, fig=fig, ax=ax,
                             kwargs=pallete_kwargs)
    obj.ax.tick_params(labelsize=16)
    cb_label = 'K Index'
    levels = list(np.arange(25, 41, 1))
    cmap = 'ncl/precip2_17lev'
    pcolormesh_2d(obj.ax, k, colorbar_kwargs={'pad': 0.05}, cb_label=cb_label, levels=levels, cmap=cmap, alpha=0.9)
    if region == 'NW':
        regrid_shape = 10
    else:
        regrid_shape = 20
    uv_barbs(obj.ax, u, v, regrid_shape=regrid_shape, sizes=dict(emptybarb=0))
    hgt_contour(obj.ax, hgt, levels=contour_levels)
    hgt_contour_588(obj.ax, hgt)
    obj.save()


def draw_hgt_uv_hpbl_588(hgt, u, v, hpbl, map_extent=(60, 145, 15, 55), region=None,
                         **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    data_name = str(hgt['member'].values[0])

    title = '[{}] {}hPa 位势高度, {}hPa 风, 边界层高度'.format(
        data_name.upper(),
        hgt['level'].values[0],
        u['level'].values[0],
    )
    forcast_info = hgt.stda.description()
    png_name = '{2}_位势高度_风_边界层高度_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour,
                                                                                             data_name.upper())
    # if region == 'NH':
    #     central_longitude = 120
    #     step = 30
    # else:
    #     central_longitude = 0
    #     step = 10
    fig, ax = horizontal_pallete_test(map_extent=map_extent, crs=ccrs.PlateCarree(central_longitude=0),
                                      forcast_info=forcast_info)
    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent,
                             add_tag=False, fig=fig, ax=ax,
                             kwargs=pallete_kwargs)
    obj.ax.tick_params(labelsize=16)
    cb_label = '边界层高度(m)'
    levels = [0, 100, 200, 300, 500, 700, 900, 1100, 1300, 1700, 1900, 3000]
    cmap = ['#{:02x}{:02x}{:02x}'.format(*tuple(i)) for i in cmap_hpbl]
    contourf_2d(obj.ax, hpbl, colorbar_kwargs={'pad': 0.05}, cb_label=cb_label, levels=levels, cb_ticks=levels,
                cmap=cmap, extend='neither', alpha=1)
    if region == 'NW':
        regrid_shape = 10
    else:
        regrid_shape = 20
    uv_barbs(obj.ax, u, v, regrid_shape=regrid_shape, sizes=dict(emptybarb=0))
    hgt_contour(obj.ax, hgt, levels=contour_levels)
    hgt_contour_588(obj.ax, hgt)
    obj.save()


def draw_hgt_uv_t_588(hgt, u, v, t, map_extent=(60, 145, 15, 55), levels=np.arange(-32, 34, 4), cmap='guide/cs36',
                      region=None, **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    data_name = str(hgt['member'].values[0])

    title = '[{}] {}hPa 位势高度, {}hPa 风, {}hPa 温度'.format(
        data_name.upper(),
        hgt['level'].values[0],
        u['level'].values[0],
        t['level'].values[0]
    )
    forcast_info = hgt.stda.description()
    png_name = '{2}_位势高度_风_温度_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour,
                                                                                          data_name.upper())
    # if region == 'NH':
    #     central_longitude = 120
    #     step = 30
    # else:
    #     central_longitude = 0
    #     step = 10
    fig, ax = horizontal_pallete_test(map_extent=map_extent, crs=ccrs.PlateCarree(central_longitude=0),
                                      forcast_info=forcast_info)
    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent,
                             add_tag=False, fig=fig, ax=ax,
                             kwargs=pallete_kwargs)
    obj.ax.tick_params(labelsize=16)
    cb_label = '温度（℃）'
    # levels = list(np.arange(-32, 34, 4))
    # cmap = 'guide/cs36'
    pcolormesh_2d(obj.ax, t, colorbar_kwargs={'pad': 0.05}, cb_label=cb_label, levels=list(levels), cmap=cmap,
                  alpha=0.9)
    if region == 'NW':
        regrid_shape = 10
    else:
        regrid_shape = 20
    uv_barbs(obj.ax, u, v, regrid_shape=regrid_shape, sizes=dict(emptybarb=0))
    hgt_contour(obj.ax, hgt, levels=contour_levels)
    hgt_contour_588(obj.ax, hgt)
    obj.save()


def draw_hgt_uv_spfh_588(hgt, u, v, spfh, map_extent=(60, 145, 15, 55), region=None,
                         spfh_pcolormesh_kwargs={}, uv_barbs_kwargs={}, hgt_contour_kwargs={},
                         **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    data_name = str(hgt['member'].values[0])
    title = '[{}] {}hPa 位势高度, {}hPa 风, {}hPa 比湿'.format(data_name.upper(), hgt['level'].values[0], u['level'].values[0],
                                                        spfh['level'].values[0])

    forcast_info = hgt.stda.description()
    png_name = '{2}_位势高度_风_比湿_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour,
                                                                                          data_name.upper())
    # if region == 'NH':
    #     central_longitude = 120
    #     step = 30
    # else:
    #     central_longitude = 0
    #     step = 10
    fig, ax = horizontal_pallete_test(map_extent=map_extent, crs=ccrs.PlateCarree(central_longitude=0),
                                      forcast_info=forcast_info)
    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent,
                             add_tag=False, fig=fig, ax=ax, kwargs=pallete_kwargs)
    obj.ax.tick_params(labelsize=16)
    spfh_pcolormesh(obj.ax, spfh, colorbar_kwargs={'pad': 0.05}, kwargs=spfh_pcolormesh_kwargs)
    if region == 'NW':
        regrid_shape = 10
    else:
        regrid_shape = 20
    uv_barbs(obj.ax, u, v, regrid_shape=regrid_shape, sizes=dict(emptybarb=0), kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, levels=contour_levels, kwargs=hgt_contour_kwargs)
    hgt_contour_588(obj.ax, hgt)
    obj.save()


def draw_hgt_uv_rh_588(hgt, u, v, rh, map_extent=(60, 145, 15, 55), region=None,
                       rh_pcolormesh_kwargs={}, uv_barbs_kwargs={}, hgt_contour_kwargs={},
                       **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    data_name = str(hgt['member'].values[0])
    title = '[{}] {}hPa 位势高度场, {}hPa 风场, {}hPa 相对湿度'.format(data_name.upper(), hgt['level'].values[0],
                                                            u['level'].values[0], rh['level'].values[0])

    forcast_info = hgt.stda.description()
    png_name = '{2}_位势高度场_风场_相对湿度_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour,
                                                                                              data_name.upper())
    # if region == 'NH':
    #     central_longitude = 120
    #     step = 30
    # else:
    #     central_longitude = 0
    #     step = 10
    fig, ax = horizontal_pallete_test(map_extent=map_extent, crs=ccrs.PlateCarree(central_longitude=0),
                                      forcast_info=forcast_info)
    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent,
                             add_tag=False, fig=fig, ax=ax, kwargs=pallete_kwargs)
    obj.ax.tick_params(labelsize=16)
    cmap_r = ['#{:02x}{:02x}{:02x}'.format(*tuple(i)) for i in r_color]
    rh_pcolormesh(obj.ax, rh, colorbar_kwargs={'pad': 0.05}, kwargs=rh_pcolormesh_kwargs, cmap=cmap_r, alpha=0.9)
    if region == 'NW':
        regrid_shape = 10
    else:
        regrid_shape = 20
    uv_barbs(obj.ax, u, v, regrid_shape=regrid_shape, sizes=dict(emptybarb=0), kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, levels=contour_levels, kwargs=hgt_contour_kwargs)
    hgt_contour_588(obj.ax, hgt)
    obj.save()


def draw_hgt_uv_wvfl_588(hgt, u, v, wvfl, map_extent=(60, 145, 15, 55), region=None,
                         wvfl_pcolormesh_kwargs={}, uv_barbs_kwargs={}, hgt_contour_kwargs={},
                         **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    data_name = str(hgt['member'].values[0])
    title = '[{}] {}hPa 位势高度, {}hPa 风, {}hPa 水汽通量'.format(data_name.upper(), hgt['level'].values[0],
                                                          u['level'].values[0], wvfl['level'].values[0])

    forcast_info = hgt.stda.description()
    png_name = '{2}_位势高度场_风场_水汽通量_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour,
                                                                                              data_name.upper())
    # if region == 'NH':
    #     central_longitude = 120
    #     step = 30
    # else:
    #     central_longitude = 0
    #     step = 10
    fig, ax = horizontal_pallete_test(map_extent=map_extent, crs=ccrs.PlateCarree(central_longitude=0),
                                      forcast_info=forcast_info)
    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent,
                             add_tag=False, fig=fig, ax=ax, kwargs=pallete_kwargs)
    obj.ax.tick_params(labelsize=16)
    wvfl_pcolormesh(obj.ax, wvfl, colorbar_kwargs={'pad': 0.05}, kwargs=wvfl_pcolormesh_kwargs)
    if region == 'NW':
        regrid_shape = 10
    else:
        regrid_shape = 20
    uv_barbs(obj.ax, u, v, regrid_shape=regrid_shape, sizes=dict(emptybarb=0), kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, levels=contour_levels, kwargs=hgt_contour_kwargs)
    hgt_contour_588(obj.ax, hgt)
    obj.save()


def draw_hgt_uv_wvfldiv_588(hgt, u, v, wvfldiv, map_extent=(60, 145, 15, 55), region=None,
                            wvfldiv_countourf_kwargs={}, uv_barbs_kwargs={}, hgt_contour_kwargs={},
                            **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    data_name = str(hgt['member'].values[0])
    title = '[{}] {}hPa 位势高度, {}hPa 风, {}hPa 水汽通量散度'.format(data_name.upper(), hgt['level'].values[0],
                                                            u['level'].values[0], wvfldiv['level'].values[0])

    forcast_info = hgt.stda.description()
    png_name = '{2}_位势高度场_风场_水汽通量散度_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour,
                                                                                                data_name.upper())
    # if region == 'NH':
    #     central_longitude = 120
    #     step = 30
    # else:
    #     central_longitude = 0
    #     step = 10
    fig, ax = horizontal_pallete_test(map_extent=map_extent, crs=ccrs.PlateCarree(central_longitude=0),
                                      forcast_info=forcast_info)
    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent,
                             add_tag=False, fig=fig, ax=ax, kwargs=pallete_kwargs)
    obj.ax.tick_params(labelsize=16)
    wvfldiv_contourf(obj.ax, wvfldiv, colorbar_kwargs={'pad': 0.05}, kwargs=wvfldiv_countourf_kwargs)
    if region == 'NW':
        regrid_shape = 10
    else:
        regrid_shape = 20
    uv_barbs(obj.ax, u, v, regrid_shape=regrid_shape, sizes=dict(emptybarb=0), kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, levels=contour_levels, kwargs=hgt_contour_kwargs)
    hgt_contour_588(obj.ax, hgt)
    obj.save()


def draw_hgt_uv_ct_588(hgt, u, v, ct, map_extent=(60, 145, 15, 55), region=None,
                       uv_barbs_kwargs={}, hgt_contour_kwargs={}, **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    data_name = str(hgt['member'].values[0])

    title = '[{}] {}hPa 位势高度, {}hPa 风, 云顶高度'.format(
        data_name.upper(),
        hgt['level'].values[0],
        u['level'].values[0],
    )
    forcast_info = hgt.stda.description()
    png_name = '{2}_位势高度_风_云顶高度_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour,
                                                                                            data_name.upper())
    # if region == 'NH':
    #     central_longitude = 120
    #     step = 30
    # else:
    #     central_longitude = 0
    #     step = 10
    fig, ax = horizontal_pallete_test(map_extent=map_extent, crs=ccrs.PlateCarree(central_longitude=0),
                                      forcast_info=forcast_info)
    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent,
                             add_tag=False, fig=fig, ax=ax,
                             kwargs=pallete_kwargs)
    obj.ax.tick_params(labelsize=16)
    cb_label = 'Cloud Top(km)'
    cmap = 'rainbow'
    levels = list(np.arange(0, 10200, 1000))
    pcolormesh_2d(obj.ax, ct, colorbar_kwargs={'pad': 0.05, 'tick_label': [int(i / 100) for i in levels]}, cmap=cmap,
                  cb_label=cb_label, levels=levels, alpha=0.9)
    if region == 'NW':
        regrid_shape = 10
    else:
        regrid_shape = 20
    uv_barbs(obj.ax, u, v, regrid_shape=regrid_shape, sizes=dict(emptybarb=0), kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, levels=contour_levels, kwargs=hgt_contour_kwargs)
    hgt_contour_588(obj.ax, hgt)
    obj.save()


def draw_hgt_uv_tcwv_588(hgt, u, v, tcwv, map_extent=(60, 145, 15, 55), region=None,
                         tcwv_pcolormesh_kwargs={}, uv_barbs_kwargs={}, hgt_contour_kwargs={},
                         **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    data_name = str(hgt['member'].values[0])
    title = '[{}] {}hPa 位势高度场, {}hPa 风场, 整层可降水量'.format(data_name.upper(), hgt['level'].values[0], u['level'].values[0])

    forcast_info = hgt.stda.description()
    png_name = '{2}_位势高度场_风场_整层可降水量_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour,
                                                                                                data_name.upper())
    # if region == 'NH':
    #     central_longitude = 120
    #     step = 30
    # else:
    #     central_longitude = 0
    #     step = 10
    fig, ax = horizontal_pallete_test(map_extent=map_extent, crs=ccrs.PlateCarree(central_longitude=0),
                                      forcast_info=forcast_info)
    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent,
                             add_tag=False, fig=fig, ax=ax, kwargs=pallete_kwargs)
    obj.ax.tick_params(labelsize=16)
    tcwv_pcolormesh(obj.ax, tcwv, cmap='guide/cs26',  alpha=1, colorbar_kwargs={'pad': 0.05}, kwargs=tcwv_pcolormesh_kwargs)
    if region == 'NW':
        regrid_shape = 10
    else:
        regrid_shape = 20
    uv_barbs(obj.ax, u, v, regrid_shape=regrid_shape, sizes=dict(emptybarb=0), kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, levels=contour_levels, kwargs=hgt_contour_kwargs)
    hgt_contour_588(obj.ax, hgt)
    obj.save()


def hgt_contour_588(ax, stda, xdim='lon', ydim='lat',
                    add_clabel=True,
                    levels=np.arange(588, 592, 4), colors='red',
                    transform=ccrs.PlateCarree(), linewidths=3,
                    **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # dagpm

    img = ax.contour(x, y, z, levels=levels, transform=transform, colors=colors, linewidths=linewidths, **kwargs)
    if add_clabel:
        plt.clabel(img, inline=1, fontsize=20, fmt='%.0f', colors='red')
    return img
