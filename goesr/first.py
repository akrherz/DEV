import pyproj
import netCDF4
import numpy as np
from pyiem.plot import MapPlot
import matplotlib.pyplot as plt


LCC = pyproj.Proj(("+lon_0=-95. +y_0=0.0 +R=6371200. +proj=lcc +x_0=0.0"
                   " +units=m +lat_2=25 +lat_1=25 +lat_0=25"))

m = MapPlot(sector='iowa', facecolor='white', statecolor='r',
            title="GOES-R 0.64 $\mu$m ABI Channel 2 on 2 March 2017 3:30 PM CST",
            subtitle='Testing dataset provided for evaluation by NOAA')
cmap = plt.get_cmap('gray')

for sector in ['I', 'J', 'C', 'D']:
    nc = netCDF4.Dataset('TIRC02_KNES_022131_PA%s.nc' % (sector, ))
    x = nc.variables['x'][:]
    y = nc.variables['y'][:]
    x, y = np.meshgrid(x, y)
    lon, lat = LCC(x, y, inverse=True)
    vals = nc.variables['Sectorized_CMI'][:]
    m.pcolormesh(lon, lat, vals, np.arange(0.02, 0.78, 0.02), cmap=cmap,
                 clip_on=False, clevstride=5, units='TOA Bidirectional Reflectance')
m.postprocess(filename='170303.png')

