out_path = r'/data/PRODUCT/FY4B_AGRI_IMAGES_4000M/{Obs_T:%Y}/{Obs_T:%Y%m%d}/CHN_{Obs_T:%Y%m%d%H%M}.png'
out_path_1000M = r'/data/PRODUCT/FY4B_AGRI_IMAGES_1000M/{Obs_T:%Y}/{Obs_T:%Y%m%d}/CHN_{Obs_T:%Y%m%d%H%M}.png'
out_path_2000M = r'/data/PRODUCT/FY4B_AGRI_IMAGES_2000M/{Obs_T:%Y}/{Obs_T:%Y%m%d}/CHN_{Obs_T:%Y%m%d%H%M}.png'
out_path_clt = r'/data/PRODUCT/FY4B_AGRI_IMAGES_4000M/{Obs_T:%Y}/{Obs_T:%Y%m%d}/CHN_{Obs_T:%Y%m%d%H%M}_clt.png'
out_path_ctt = r'/data/PRODUCT/FY4B_AGRI_IMAGES_4000M/{Obs_T:%Y}/{Obs_T:%Y%m%d}/CHN_{Obs_T:%Y%m%d%H%M}_ctt.png'
out_path_cth = r'/data/PRODUCT/FY4B_AGRI_IMAGES_4000M/{Obs_T:%Y}/{Obs_T:%Y%m%d}/CHN_{Obs_T:%Y%m%d%H%M}_cth.png'
out_path_clt_mask = r'/data/PRODUCT/FY4B_AGRI_IMAGES_4000M/{Obs_T:%Y}/{Obs_T:%Y%m%d}/CHN_{Obs_T:%Y%m%d%H%M}_clt.nc'
out_path_ctt_mask = r'/data/PRODUCT/FY4B_AGRI_IMAGES_4000M/{Obs_T:%Y}/{Obs_T:%Y%m%d}/CHN_{Obs_T:%Y%m%d%H%M}_ctt.nc'
out_path_cth_mask = r'/data/PRODUCT/FY4B_AGRI_IMAGES_4000M/{Obs_T:%Y}/{Obs_T:%Y%m%d}/CHN_{Obs_T:%Y%m%d%H%M}_cth.nc'
out_path_radar_mask = r'/data/PRODUCT/FY4B_AGRI_IMAGES_4000M/{Obs_T:%Y}/{Obs_T:%Y%m%d}/CHN_{Obs_T:%Y%m%d%H%M}_radar.nc'
out_path_radar = r'/data/PRODUCT/FY4B_AGRI_IMAGES_4000M/{Obs_T:%Y}/{Obs_T:%Y%m%d}/CHN_{Obs_T:%Y%m%d%H%M}_radar.png'
out_path_cape = r'/data/PRODUCT/FY4B_AGRI_IMAGES_4000M/{Obs_T:%Y}/{Obs_T:%Y%m%d}/CHN_{Obs_T:%Y%m%d%H%M}_cape.png'
out_path_track = r'/data/PRODUCT/FY4B_AGRI_IMAGES_4000M/{Obs_T:%Y}/{Obs_T:%Y%m%d}/CHN_{Obs_T:%Y%m%d%H%M}_track{type}.png'
out_path_pkl = r'/data/PRODUCT/FY4B_AGRI_IMAGES_4000M/{Obs_T:%Y}/{Obs_T:%Y%m%d}/pkl/CHN_{Obs_T:%Y%m%d%H%M}.pkl'
out_path_geojson_4000M = r'/data/PRODUCT/FY4B_AGRI_IMAGES_4000M/{Obs_T:%Y}/{Obs_T:%Y%m%d}/CHN_{Obs_T:%Y%m%d%H%M}.geojson'
out_path_geojson_2000M = r'/data/PRODUCT/FY4B_AGRI_IMAGES_2000M/{Obs_T:%Y}/{Obs_T:%Y%m%d}/CHN_{Obs_T:%Y%m%d%H%M}.geojson'
out_path_geojson_1000M = r'/data/PRODUCT/FY4B_AGRI_IMAGES_1000M/{Obs_T:%Y}/{Obs_T:%Y%m%d}/CHN_{Obs_T:%Y%m%d%H%M}.geojson'

shp_path = r"./venv/shp/china_20220325.shp"
DEM_path = r'./venv/shp/han_G_Static_stmas_new_5km.m4'
input_path = r"/CMADAAS/DATA/SATE/FY4/FY4B/AGRI/L1/FDI/DISK/4000M"
input_path_1000M = r"/CMADAAS/DATA/SATE/FY4/FY4B/AGRI/L1/FDI/DISK/1000M"
input_path_2000M = r"/CMADAAS/DATA/SATE/FY4/FY4B/AGRI/L1/FDI/DISK/2000M"
# radar_format = r'/mnt/radar_data/SWAN/MCR/%Y/%Y%m%d/Z_OTHE_RADAMCR_%Y%m%d%H%M00.bin.bz2'
cape_format = r'/CMADAAS/DATA/NAFP/ECMF/D1D/%Y/%Y%m%d/ECMFD1D_CAPE_1_%Y%m%d%H_GLB_1.grib1'
CLT_format = r'/CMADAAS/DATA/SATE/FY4/FY4A/AGRI/L2/%Y/%Y%m%d/Z_SATE_C_BAWX_*_P_FY4A-_AGRI--_N_DISK_1047E_L2-_CLT-_MULT_NOM_%Y%m%d%H%M*_4000M_V0001.NC'
CTT_format = r'/CMADAAS/DATA/SATE/FY4/FY4B/AGRI/L2/CTT/DISK/NOM/%Y/%Y%m%d/FY4B-_AGRI--_N_DISK_1330E_L2-_CTT-_MULT_NOM_%Y%m%d%H%M*_4000M_V0001.NC'
CTH_format = r'/CMADAAS/DATA/SATE/FY4/FY4B/AGRI/L2/CTH/DISK/NOM/%Y/%Y%m%d/FY4B-_AGRI--_N_DISK_1330E_L2-_CTH-_MULT_NOM_%Y%m%d%H%M*_4000M_V0001.NC'

south_lat = 10
north_lat = 60
west_lon = 70
east_lon = 140
xy_step = 10

time_interval = 30      #外推的时间
M4000_resolution = 0.04  #文件的原始分辨率，不需要修改。
M2000_resolution = 0.02  #文件的原始分辨率，不需要修改。
M1000_resolution = 0.01  #文件的原始分辨率，不需要修改。
CI_mode = '2'           #CI的对流预报方式
EX_mode = '2'           #成熟对流的外推方式
steps = 3               #仿照半拉格朗日的步长外推

color_EX = ['lightgreen', 'limegreen', 'g', 'darkgreen'] #成熟对流云
color_CI = ['dodgerblue', 'royalblue', 'b', 'darkblue'] #初生对流云
color_DP = ['pink', 'hotpink', 'm', 'crimson'] #发展对流云
color_DIS = ['moccasin', 'gold', 'goldenrod', 'orange'] #发展对流云