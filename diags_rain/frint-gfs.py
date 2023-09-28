############### THE SKILL SCORE FOR PRECIPITATION BINARY VERIFICATION WITH GAUAGES########################
############### Edit by zhao b##in from chinese NWPC #####################################################
############### Email: zhao###b@cma.gov.cn################################################################
##########################################################################################################
import numpy as np
import eccodes
import datetime
import os
import sys
########################dirroot##################################
obsroot='/g1/u/nwp_vfy/MUVOS/obs/station/sl/rainnew/rain_03/'
##################################################################
fcstroot='/g1/u/nwp_vfy/houtai/operation/GRAPES/rain'
outputroot='/g3/vfy_xp/diags_rain/CMA-GFS/frint'
###################################################################
starttime=datetime.datetime.strptime(sys.argv[1], "%Y%m%d%H")   # YYYY-MM-DD-HH of starttime
endtime=datetime.datetime.strptime(sys.argv[2], "%Y%m%d%H")     # YYYY-MM-DD-HH of endtime
##########################################################################################
cdate=starttime
while cdate<=endtime:
	for i in range(3,72+3,3):
		obsdate=cdate+datetime.timedelta(hours=i)
#######################read fcst in the first time step#######################
		fcstdate1=fcstroot+str("%03d"%(i-3))+".grapes."+str(cdate.strftime("%Y%m%d%H"))
		print(fcstdate1)		        		
		if os.access(fcstdate1,os.F_OK) and os.path.getsize(fcstdate1):
			f = open(fcstdate1, "rb")
			gid = eccodes.codes_grib_new_from_file(f)
			if gid is None:
				print("create handler error")
		# load matrix
			ni = eccodes.codes_get(gid, "Ni")
			nj = eccodes.codes_get(gid, "Nj")
			print(ni, nj)
			values = eccodes.codes_get_values(gid)
			fcst1 = np.reshape(values, (nj, ni))	

			resolution = eccodes.codes_get(gid, 'iDirectionIncrementInDegrees')
##############################################################################

########### read fcst in the second time step#######################
			fcstdate2=fcstroot+str("%03d"%i)+".grapes."+str(cdate.strftime("%Y%m%d%H"))
			print(fcstdate2)
			if os.access(fcstdate2,os.F_OK) and os.path.getsize(fcstdate2):			
				f = open(fcstdate2, "rb")
				gid = eccodes.codes_grib_new_from_file(f)
				if gid is None:
					print("create handler error")
				values = eccodes.codes_get_values(gid)
				fcst2 = np.reshape(values, (nj, ni))
				fcst=fcst2-fcst1
########### read obs ####################################################
				obsfile=obsroot+str(obsdate.strftime("%Y%m"))+'/rain03_'+str(obsdate.strftime("%Y%m%d%H"))+'.dat'
				print(obsfile)
				if os.access(obsfile,os.F_OK) and os.path.getsize(obsfile):
					outputdate=outputroot+str("%03d"%i)+"."+str(cdate.strftime("%Y%m%d%H"))
					f = open(outputdate, "w")
					infile = open(obsfile, 'r')
					lat=np.arange(-89.875,89.875,resolution)
					lon=np.arange(0,360-resolution,resolution)
					for line in infile:
						words = line.split()
						station=float(words[0])
						obslat=float(words[1])
						obslon=float(words[2])
						obsrain=float(words[3])
						tx=int((obslat+89.875)/resolution)
						ty=int((obslon)/resolution)
						for jjk in range(tx-4,tx+4):
							if (obslat-lat[jjk])*(obslat-lat[jjk+1])<=0:
								jj=jjk
						for iik in range(ty-4,ty+4):
							if (obslon-lon[iik])*(obslon-lon[iik+1])<=0:
								ii=iik
						l1=abs(obslat-lat[jj]);l2=abs(obslat-lat[jj+1]);l3=abs(obslon-lon[ii]);l4=abs(obslon-lon[ii+1])
						if l1<=0.5*resolution and l3<=0.5*resolution:
							raintmp=fcst[jj,ii]
						if l1<=0.5*resolution and l4<=0.5*resolution:
							raintmp=fcst[jj,ii+1]
						if l2<=0.5*resolution and l3<=0.5*resolution:
							raintmp=fcst[jj+1,ii]
						if l2<=0.5*resolution and l4<=0.5*resolution:
							raintmp=fcst[jj+1,ii+1]
						if l1==0.5*resolution and l3==0.5*resolution:
							raintmp=max(fcst[jj,ii],fcst[jj+1,ii],fcst[jj,ii+1],fcst[jj+1,ii+1])					
						f.write(str("%10.1f"%station)+str("%10.2f"%obslat)+str("%10.2f"%obslon)+str("%10.3f"%obsrain)+str("%10.3f"%raintmp))
						f.write(' \r\n')
	cdate=cdate+datetime.timedelta(days=1)
	
