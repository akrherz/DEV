#!/usr/local/python/bin/python
# Generate a WEPP format cli file from NARR analysis
# Daryl Herzmann 1 Oct 2008

import mx.DateTime, math, sys
from Scientific.IO import NetCDF

def figureXY(lon,lat):
  """  Figure out the x,y values of our point of interest :) """
  nc = NetCDF.NetCDFFile("/mnt/nrel/cjames/NARR/air.2m.2006.nc")
  xsz = nc.dimensions['x']
  ysz = nc.dimensions['y']
  lats = nc.variables['lat']
  lons = nc.variables['lon']
  res = 100000
  for i in range(xsz):
    for j in range(ysz):
      delta = math.sqrt( (lats[j,i][0] - lat)**2 + (lons[j,i][0] - lon)**2 )
      if (delta < res):
        res = delta
        minx = i
        miny = j

  return minx, miny

x,y = figureXY(float(sys.argv[2]),float(sys.argv[3]))

#  apcp:add_offset = 50.f ;
#  apcp:scale_factor = 0.001526019f ;
precip = NetCDF.NetCDFFile("/mnt/nrel/cjames/NARR/apcp.%s.nc" % (sys.argv[1],)).variables['apcp'][:,y,x]

def vrmm(a):
  return a * 0.001526019 + 50

print sum( map(vrmm, precip))
