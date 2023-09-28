import eccodes
import numpy as np
from nwpc_data.format.grib.eccodes import load_message_from_file
from scipy.ndimage.filters import uniform_filter
from sklearn import metrics 
from mpl_toolkits.basemap import Basemap
import matplotlib.colors as colors
import matplotlib
import matplotlib.pyplot as plt
import datetime
import os
import sys

starttime=datetime.datetime.strptime(sys.argv[1], "%Y%m%d%H")   # YYYY-MM-DD-HH of starttime
endtime=datetime.datetime.strptime(sys.argv[2], "%Y%m%d%H")     # YYYY-MM-DD-HH of endtime
ld=int(sys.argv[3])
models=sys.argv[4].split(',')
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
startobs=starttime+datetime.timedelta(days=ld)
endobs=endtime+datetime.timedelta(days=ld)

stations_lon=[];stations_lat=[];fcst=[];obs=[]
for mm in range(0,len(models)):
	tt=0
	cdate=starttime
	while cdate<=endtime:
		for ii in range(0,30,6):
			i=(ld-1)*24+ii
			filedata=inputroot+models[mm]+'/frint'+str("%03d"%i)+'.'+str(cdate.strftime("%Y%m%d%H"))
			if os.access(filedata,os.F_OK) and os.path.getsize(filedata):
				print(filedata)
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
stations_lon=np.array(stations_lon).reshape((len(models),tt,5,kk))
stations_lat=np.array(stations_lat).reshape((len(models),tt,5,kk))
fcst=np.array(fcst).reshape((len(models),tt,5,kk))
obs=np.array(obs).reshape((len(models),tt,5,kk))

ed_f=np.full((len(models),tt,kk),0)
ed_o=np.full((len(models),tt,kk),0)
edt_f=np.full((len(models),kk),-999)
edt_o=np.full((len(models),kk),-999)
i_f=(fcst>=0.1).astype(float)
i_o=(obs>=0.1).astype(float)

for mm in range (0,len(models)):
	for tk in range(0,tt):
		for kn in range(0,kk):
			af=[];ao=[]
			if np.all(i_f[mm,tk,:,kn]==0):
				ed_f[mm,tk,kn]=0
			else:
				af=np.where(i_f[mm,tk,:,kn]!=0)[0].tolist()
				bf=len(np.where(i_f[mm,tk,:,kn]!=0)[0].tolist())
				ed_f[mm,tk,kn]=af[bf-1]*6
			if np.all(i_o[mm,tk,:,kn]==0):
				ed_o[mm,tk,kn]=0
			else:
				ao=np.where(i_o[mm,tk,:,kn]!=0)[0].tolist()
				bo=len(np.where(i_o[mm,tk,:,kn]!=0)[0].tolist())
				ed_o[mm,tk,kn]=ao[bo-1]*6

for mm in range (0,len(models)):
	for kn in range(0,kk):
		if np.all(ed_f[mm,:,kn]==0):
			edt_f[mm,kn]=-999
		else:
			edt_f[mm,kn]=np.argmax(np.bincount(ed_f[mm,:,kn][ed_f[mm,:,kn]>0]))
		if np.all(ed_o[mm,:,kn]==0):
			edt_o[mm,kn]=-999
		else:
			edt_o[mm,kn]=np.argmax(np.bincount(ed_o[mm,:,kn][ed_o[mm,:,kn]>0]))
for mm in range (0,len(models)):
	for tk in range(0,tt):
		edt_f[mm,kn]=edt_f[mm,kn]+int(time)+8
		edt_o[mm,kn]=edt_o[mm,kn]+int(time)+8
		if edt_f[mm,kn] > 24:
			edt_f[mm,kn]=edt_f[mm,kn]-24
		if edt_o[mm,kn] > 24:
			edt_o[mm,kn]=edt_o[mm,kn]-24

levels=[6,12,18,24,24]
norm=colors.BoundaryNorm(boundaries=levels,ncolors=256)

fig=plt.figure(figsize=(8,6))
plt.tick_params(labelsize=12)
m= Basemap(lat_0=lat_0, lon_0=lon_0,llcrnrlon=slon,llcrnrlat=slat,urcrnrlon=elon,urcrnrlat=elat)
m.readshapefile("./shp/china",'china',drawbounds=True)
m.readshapefile("./shp/china_nine_dotted_line",'nine_dotted',drawbounds=True)
longitudes, latitudes = m(stations_lon[0,0,1,], stations_lat[0,0,1,])
cs=m.scatter(longitudes, latitudes, marker='.',s=1,c=edt_o[0,],norm=norm,cmap='rainbow')
cbar = m.colorbar(cs, location='bottom', pad='10%')
cbar.set_label("BJS")
m.drawparallels(np.arange(slat,elat+1, 10.), labels=[1,0,0,0], fontsize=10)
m.drawmeridians(np.arange(slon,elon, 10.), labels=[0,0,0,1], fontsize=10)
m.drawcoastlines()
m.drawstates()
m.drawcountries()
plt.title('END Time of RAIN Freq\nOBS'+'\nDate:'+str(startobs.strftime("%Y%m%d"))+'-'+str(endobs.strftime("%Y%m%d")),loc='left',fontsize=9)

left,bottom,width,height=0.75,0.27,0.17,0.2
ax3=fig.add_axes([left,bottom,width,height])
slat=0;elat=25;slon=105;elon=125
lons = np.arange(slon, elon,reso)[:]
lats = np.arange(slat, elat,reso)[:]
lon_0 = lons.mean()
lat_0 = lats.mean()
m= Basemap(lat_0=lat_0, lon_0=lon_0,llcrnrlon=slon,llcrnrlat=slat,urcrnrlon=elon,urcrnrlat=elat)
m.readshapefile("./shp/china",'china',drawbounds=True)
m.readshapefile("./shp/china_nine_dotted_line",'nine_dotted',drawbounds=True)
longitudes, latitudes = m(stations_lon[0,0,1,], stations_lat[0,0,1,])
cs=m.scatter(longitudes, latitudes, marker='.',s=1,c=edt_o[0,],norm=norm,cmap='rainbow')
pngname='ET-freq-OBS-day'+str(ld)+'.png'
plt.savefig(pngname,dpi=120)
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
	m.readshapefile("./shp/china", 'china', drawbounds=True)
	m.readshapefile("./shp/china_nine_dotted_line", 'nine_dotted', drawbounds=True)
	longitudes, latitudes = m(stations_lon[mm,0,1,], stations_lat[mm,0,1,])
	cs=m.scatter(longitudes, latitudes, marker='.',s=1,c=edt_f[mm,],norm=norm,cmap='rainbow')
	cbar = m.colorbar(cs, location='bottom', pad='10%')
	cbar.set_label("BJS")
	m.drawparallels(np.arange(slat,elat+1, 10.), labels=[1,0,0,0], fontsize=10)
	m.drawmeridians(np.arange(slon,elon, 10.), labels=[0,0,0,1], fontsize=10)
	m.drawcoastlines()
	m.drawstates()
	m.drawcountries()
	plt.title('END Time of RAIN Freq\nFCST:'+str("%9s"%models[mm])+'\nDate:'+str(starttime.strftime("%Y%m%d"))+'-'+str(endtime.strftime("%Y%m%d"))+'\nFcst:D+'+str(ld),loc='left',fontsize=9)

	left,bottom,width,height=0.75,0.27,0.17,0.2
	ax3=fig.add_axes([left,bottom,width,height])
	slat=0;elat=25;slon=105;elon=125
	lons = np.arange(slon, elon,reso)[:]
	lats = np.arange(slat, elat,reso)[:]
	lon_0 = lons.mean()
	lat_0 = lats.mean()
	m= Basemap(lat_0=lat_0, lon_0=lon_0,llcrnrlon=slon,llcrnrlat=slat,urcrnrlon=elon,urcrnrlat=elat)
	m.readshapefile("./shp/china", 'china', drawbounds=True)
	m.readshapefile("./shp/china_nine_dotted_line", 'nine_dotted', drawbounds=True)
	longitudes, latitudes = m(stations_lon[0,0,1,], stations_lat[0,0,1,])
	cs=m.scatter(longitudes, latitudes, marker='.',s=1,c=edt_f[mm,],norm=norm,cmap='rainbow')
	pngname='ET-freq-day-'+str(ld)+'-'+str(models[mm])+'.png'
	plt.savefig(pngname,dpi=120)
	plt.close()
