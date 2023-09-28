import eccodes
import numpy as np
#from nwpc_data.format.grib.eccodes import load_message_from_file
from scipy.ndimage.filters import uniform_filter
from sklearn import metrics
from mpl_toolkits.basemap import Basemap
import matplotlib
import matplotlib.pyplot as plt
import datetime
import os
import sys
matplotlib.use('Agg')
plt.rcParams['font.family'] = 'serif'  # 下面代码不行，在加上这一行
starttime=datetime.datetime.strptime(sys.argv[1], "%Y%m%d%H")   # YYYY-MM-DD-HH of starttime
endtime=datetime.datetime.strptime(sys.argv[2], "%Y%m%d%H")     # YYYY-MM-DD-HH of endtime
ld=int(sys.argv[3])
models=['ECMWF','CMA-GFS','CMA-MESO','CMA-TYM']
inputroot='/data2/cpvs/DownLoad/TP/'

time=starttime.hour
domain=[15,55,70,145]
reso=0.25
slat=domain[0];elat=domain[1]-reso;slon=domain[2];elon=domain[3]-reso
lons = np.arange(slon, elon+reso,reso)[:]
lats = np.arange(slat, elat+reso,reso)[:]
lon_0 = lons.mean()
lat_0 = lats.mean()
kk=10796
startobs=starttime
endobs=endtime+datetime.timedelta(days=1)

stations_lon=[];stations_lat=[];fcst=[];obs=[]
for mm in range(0,len(models)):
	tt=0
	cdate=starttime
	while cdate<=endtime:
		ccdate=cdate-datetime.timedelta(hours=time)
		i1=time+(ld-1)*24+3
		i2=i1+24
		for i in range(i1,i2,3):
			filedata=inputroot+models[mm]+'/frint'+str("%03d"%i)+'.'+str(ccdate.strftime("%Y%m%d%H"))
			if os.access(filedata,os.F_OK) and os.path.getsize(filedata):
				f = open(filedata, 'r')
				lonr=[];latr=[];fcstr=[];obsr=[]
				for line in f:
					words = line.split()
					lonr.append(float(words[2]))
					latr.append(float(words[1]))
					fcstr.append(float(words[4]))
					obsr.append(float(words[3]))
				lonr=np.reshape(lonr, (kk))
				latr=np.reshape(latr, (kk))
				fcstr=np.reshape(fcstr, (kk))
				obsr==np.reshape(obsr, (kk))
			else:
				lonr=np.full((kk),np.nan)
				latr=np.full((kk),np.nan)
				fcstr=np.full((kk),np.nan)
				obsr=np.full((kk),np.nan)
			stations_lon.append(lonr);stations_lat.append(latr);fcst.append(fcstr);obs.append(obsr)
		tt+=1
		cdate=cdate+datetime.timedelta(days=1)
stations_lon=np.array(stations_lon).reshape((len(models),tt,8,kk))
stations_lat=np.array(stations_lat).reshape((len(models),tt,8,kk))
fcst=np.array(fcst).reshape((len(models),tt,8,kk))
obs=np.array(obs).reshape((len(models),tt,8,kk))

i_f=(fcst>=0.1).astype(float)
i_o=(obs>=0.1).astype(float)
f_f=(fcst>=0.0).astype(float)
f_o=(obs>=0.0).astype(float)
a_f=fcst;a_o=obs
a_f[a_f<0.1]=np.nan
a_o[a_o<0.1]=np.nan

p_f=np.nansum(np.nansum(i_f,axis=1),axis=1)/np.nansum(np.nansum(f_f,axis=1),axis=1)*100
p_o=np.nansum(np.nansum(i_o,axis=1),axis=1)/np.nansum(np.nansum(f_o,axis=1),axis=1)*100

int_f=np.nansum(np.nansum(a_f,axis=1),axis=1)/np.nansum(np.nansum(i_f,axis=1),axis=1)
int_o=np.nansum(np.nansum(a_o,axis=1),axis=1)/np.nansum(np.nansum(i_o,axis=1),axis=1)

fig=plt.figure(figsize=(8,6))
plt.tick_params(labelsize=12)
m= Basemap(lat_0=lat_0, lon_0=lon_0,llcrnrlon=slon,llcrnrlat=slat,urcrnrlon=elon,urcrnrlat=elat)
m.readshapefile("/data2/cpvs/diags_ZB/TP/shp/china",'china',drawbounds=True)
m.readshapefile("/data2/cpvs/diags_ZB/TP/shp/china_nine_dotted_line",'nine_dotted',drawbounds=True)
longitudes, latitudes = m(stations_lon[0,0,0,], stations_lat[0,0,0,])
cs=m.scatter(longitudes, latitudes, marker='.',s=1,c=p_o[0,],vmin=5,vmax=65,cmap='rainbow')
cbar = m.colorbar(cs, location='bottom', pad='10%')
cbar.set_label("Percent(%)")
m.drawparallels(np.arange(slat,elat+1, 10.), labels=[1,0,0,0], fontsize=10)
m.drawmeridians(np.arange(slon,elon, 10.), labels=[0,0,0,1], fontsize=10)
m.drawcoastlines()
m.drawstates()
m.drawcountries()
plt.title('Freq of RAIN\nOBS'+'\nDate:'+str(startobs.strftime("%Y%m%d"))+'-'+str(endobs.strftime("%Y%m%d")),loc='left',fontsize=9)

left,bottom,width,height=0.75,0.27,0.17,0.2
ax3=fig.add_axes([left,bottom,width,height])
slat=0;elat=25;slon=105;elon=125
lons = np.arange(slon, elon,reso)[:]
lats = np.arange(slat, elat,reso)[:]
lon_0 = lons.mean()
lat_0 = lats.mean()
m= Basemap(lat_0=lat_0, lon_0=lon_0,llcrnrlon=slon,llcrnrlat=slat,urcrnrlon=elon,urcrnrlat=elat)
m.readshapefile("/data2/cpvs/diags_ZB/TP/shp/china",'china',drawbounds=True)
m.readshapefile("/data2/cpvs/diags_ZB/TP/shp/china_nine_dotted_line",'nine_dotted',drawbounds=True)
longitudes, latitudes = m(stations_lon[0,0,0,], stations_lat[0,0,0,])
cs=m.scatter(longitudes, latitudes, marker='.',s=1,c=p_o[0,],vmin=5,vmax=65,cmap='rainbow')
pngname='/data2/cpvs/Product/synoptic/TP_ZD/freq-OBS-day'+str(ld)+'.png'
plt.savefig(pngname,dpi=120, bbox_inches='tight')
plt.close()


fig=plt.figure(figsize=(8,6))
plt.tick_params(labelsize=12)
slat=domain[0];elat=domain[1]-reso;slon=domain[2];elon=domain[3]-reso
lons = np.arange(slon, elon+reso,reso)[:]
lats = np.arange(slat, elat+reso,reso)[:]
lon_0 = lons.mean()
lat_0 = lats.mean()
m= Basemap(lat_0=lat_0, lon_0=lon_0,llcrnrlon=slon,llcrnrlat=slat,urcrnrlon=elon,urcrnrlat=elat)
m.readshapefile("/data2/cpvs/diags_ZB/TP/shp/china",'china',drawbounds=True)
m.readshapefile("/data2/cpvs/diags_ZB/TP/shp/china_nine_dotted_line",'nine_dotted',drawbounds=True)
longitudes, latitudes = m(stations_lon[0,0,0,], stations_lat[0,0,0,])
cs=m.scatter(longitudes, latitudes, marker='.',s=1,c=int_o[0,],vmin=0,vmax=12,cmap='rainbow')
cbar = m.colorbar(cs, location='bottom', pad='10%')
cbar.set_label("mm/3h")
m.drawparallels(np.arange(slat,elat+1, 10.), labels=[1,0,0,0], fontsize=10)
m.drawmeridians(np.arange(slon,elon, 10.), labels=[0,0,0,1], fontsize=10)
m.drawcoastlines()
m.drawstates()
m.drawcountries()
plt.title('Int of RAIN\nOBS'+'\nDate:'+str(startobs.strftime("%Y%m%d"))+'-'+str(endobs.strftime("%Y%m%d")),loc='left',fontsize=9)
left,bottom,width,height=0.75,0.27,0.17,0.2
ax3=fig.add_axes([left,bottom,width,height])
slat=0;elat=25;slon=105;elon=125
lons = np.arange(slon, elon,reso)[:]
lats = np.arange(slat, elat,reso)[:]
lon_0 = lons.mean()
lat_0 = lats.mean()
m= Basemap(lat_0=lat_0, lon_0=lon_0,llcrnrlon=slon,llcrnrlat=slat,urcrnrlon=elon,urcrnrlat=elat)
m.readshapefile("/data2/cpvs/diags_ZB/TP/shp/china",'china',drawbounds=True)
m.readshapefile("/data2/cpvs/diags_ZB/TP/shp/china_nine_dotted_line",'nine_dotted',drawbounds=True)
longitudes, latitudes = m(stations_lon[0,0,0,], stations_lat[0,0,0,])
cs=m.scatter(longitudes, latitudes, marker='.',s=1,c=int_o[0,],vmin=0,vmax=12,cmap='rainbow')
pngname='/data2/cpvs/Product/synoptic/TP_ZD/int-OBS-day'+str(ld)+'.png'
plt.savefig(pngname,dpi=120, bbox_inches='tight')
plt.close()


for mm in range(0,len(models)):
	fig=plt.figure(figsize=(8,6))
	plt.tick_params(labelsize=12)
	slat=domain[0];elat=domain[1]-reso;slon=domain[2];elon=domain[3]-reso
	lons = np.arange(slon, elon+reso,reso)[:]
	lats = np.arange(slat, elat+reso,reso)[:]
	lon_0 = lons.mean()
	lat_0 = lats.mean()
	m= Basemap(lat_0=lat_0, lon_0=lon_0,llcrnrlon=slon,llcrnrlat=slat,urcrnrlon=elon,urcrnrlat=elat)
	m.readshapefile("/data2/cpvs/diags_ZB/TP/shp/china",'china',drawbounds=True)
	m.readshapefile("/data2/cpvs/diags_ZB/TP/shp/china_nine_dotted_line",'nine_dotted',drawbounds=True)
	longitudes, latitudes = m(stations_lon[mm,0,0,], stations_lat[mm,0,0,])
	cs=m.scatter(longitudes, latitudes, marker='.',s=1,c=p_f[mm,],vmin=5,vmax=65,cmap='rainbow')
	cbar = m.colorbar(cs, location='bottom', pad='10%')
	cbar.set_label("Percent(%)")
	m.drawparallels(np.arange(slat,elat+1, 10.), labels=[1,0,0,0], fontsize=10)
	m.drawmeridians(np.arange(slon,elon, 10.), labels=[0,0,0,1], fontsize=10)
	m.drawcoastlines()
	m.drawstates()
	m.drawcountries()
	plt.title('Freq of RAIN\nFCST:'+str("%9s"%models[mm])+'\nDate:'+str(starttime.strftime("%Y%m%d"))+'-'+str(endobs.strftime("%Y%m%d"))+'\nFcst:D+'+str(ld),loc='left',fontsize=9)

	left,bottom,width,height=0.75,0.27,0.17,0.2
	ax3=fig.add_axes([left,bottom,width,height])
	slat=0;elat=25;slon=105;elon=125
	lons = np.arange(slon, elon,reso)[:]
	lats = np.arange(slat, elat,reso)[:]
	lon_0 = lons.mean()
	lat_0 = lats.mean()
	m= Basemap(lat_0=lat_0, lon_0=lon_0,llcrnrlon=slon,llcrnrlat=slat,urcrnrlon=elon,urcrnrlat=elat)
	m.readshapefile("/data2/cpvs/diags_ZB/TP/shp/china",'china',drawbounds=True)
	m.readshapefile("/data2/cpvs/diags_ZB/TP/shp/china_nine_dotted_line",'nine_dotted',drawbounds=True)
	longitudes, latitudes = m(stations_lon[0,0,0,], stations_lat[0,0,0,])
	cs=m.scatter(longitudes, latitudes, marker='.',s=1,c=p_f[mm,],vmin=5,vmax=65,cmap='rainbow')
	pngname='/data2/cpvs/Product/synoptic/TP_ZD/freq-day-'+str(ld)+'-'+str(models[mm])+'.png'
	plt.savefig(pngname,dpi=120, bbox_inches='tight')
	plt.close()

	fig=plt.figure(figsize=(8,6))
	plt.tick_params(labelsize=12)
	slat=domain[0];elat=domain[1]-reso;slon=domain[2];elon=domain[3]-reso
	lons = np.arange(slon, elon+reso,reso)[:]
	lats = np.arange(slat, elat+reso,reso)[:]
	lon_0 = lons.mean()
	lat_0 = lats.mean()
	m= Basemap(lat_0=lat_0, lon_0=lon_0,llcrnrlon=slon,llcrnrlat=slat,urcrnrlon=elon,urcrnrlat=elat)
	m.readshapefile("/data2/cpvs/diags_ZB/TP/shp/china",'china',drawbounds=True)
	m.readshapefile("/data2/cpvs/diags_ZB/TP/shp/china_nine_dotted_line",'nine_dotted',drawbounds=True)
	longitudes, latitudes = m(stations_lon[0,0,0,], stations_lat[0,0,0,])
	cs=m.scatter(longitudes, latitudes, marker='.',s=1,c=int_f[mm,],vmin=0,vmax=12,cmap='rainbow')
	cbar = m.colorbar(cs, location='bottom', pad='10%')
	cbar.set_label("mm/3h")
	m.drawparallels(np.arange(slat,elat+1, 10.), labels=[1,0,0,0], fontsize=10)
	m.drawmeridians(np.arange(slon,elon, 10.), labels=[0,0,0,1], fontsize=10)
	m.drawcoastlines()
	m.drawstates()
	m.drawcountries()
	plt.title('Int of RAIN\nFCST:'+str("%9s"%models[mm])+'\nDate:'+str(starttime.strftime("%Y%m%d"))+'-'+str(endobs.strftime("%Y%m%d"))+'\nFcst:D+'+str(ld),loc='left',fontsize=9)
	left,bottom,width,height=0.75,0.27,0.17,0.2
	ax3=fig.add_axes([left,bottom,width,height])
	slat=0;elat=25;slon=105;elon=125
	lons = np.arange(slon, elon,reso)[:]
	lats = np.arange(slat, elat,reso)[:]
	lon_0 = lons.mean()
	lat_0 = lats.mean()
	m= Basemap(lat_0=lat_0, lon_0=lon_0,llcrnrlon=slon,llcrnrlat=slat,urcrnrlon=elon,urcrnrlat=elat)
	m.readshapefile("/data2/cpvs/diags_ZB/TP/shp/china",'china',drawbounds=True)
	m.readshapefile("/data2/cpvs/diags_ZB/TP/shp/china_nine_dotted_line",'nine_dotted',drawbounds=True)
	longitudes, latitudes = m(stations_lon[0,0,0,], stations_lat[0,0,0,])
	cs=m.scatter(longitudes, latitudes, marker='.',s=1,c=int_f[mm,],vmin=0,vmax=12,cmap='rainbow')
	pngname='/data2/cpvs/Product/synoptic/TP_ZD/int-day-'+str(ld)+'-'+str(models[mm])+'.png'
	plt.savefig(pngname,dpi=120, bbox_inches='tight')
	plt.close()

