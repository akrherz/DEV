import pygrib
import pyiem.mrms as mrms2
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from pyiem import reference
from matplotlib.patches import Polygon
import numpy as np
import netCDF4
from PIL import Image
from pyiem.plot import MapPlot, nwsprecip
from pyiem.datatypes import distance
from pyiem import iemre
import datetime

import matplotlib.patheffects as PathEffects
import matplotlib.colors as mpcolors

m = MapPlot(sector='custom', north=42.09, east=-93.55, south=41.97, west=-93.7,
            axisbg='white',
  title='NOAA MRMS Q3: 29 August 2016 RADAR Estimated Precipitation',
  subtitle='Valid: 8 PM 28-29 August 2016, using  RadarOnly Products, Ames Airport Total Plotted')

m.map.readshapefile('high', 'roads', ax=m.ax, drawbounds=False)
for nshape, seg in enumerate(m.map.roads):
     if (m.map.roads_info[nshape]['US1'] in (30,) or
        m.map.roads_info[nshape]['INT1'] in (35, 235, 80)):
         data = np.array( seg )
         m.ax.plot(data[:,0], data[:,1], lw=3, linestyle='-',color='k',
                   zorder=3)
         m.ax.plot(data[:,0], data[:,1], lw=1, linestyle='-',color='w',
                   zorder=4)

m.map.readshapefile('cities', 'cities', ax=m.ax)
for nshape, seg in enumerate(m.map.cities):
     #if m.map.cities_info[nshape]['NAME10'] != 'Ames':
     #    continue
     poly=Polygon(seg, fc='None', ec='k', lw=1.5, zorder=3)
     m.ax.add_patch(poly)

grbs = pygrib.open('RadarOnly_QPE_24H_00.00_20160830-010000.grib2')
g = grbs.message(1)
pcpn = distance(g['values'], 'MM').value('IN')
lats, lons = g.latlons()
lons -= 360.
clevs = [0.01, 0.1, 0.3, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10]
cmap = nwsprecip()

m.pcolormesh(lons, lats, pcpn, clevs, cmap=cmap, latlon=True, units='inch')

xx, yy = m.map(-93.723, 41.731)
txt = m.ax.text(xx, yy, "DMX", zorder=5, ha='center',
          va='center', fontsize=10)
txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground="w")])

xx, yy = m.map(-93.62, 41.99)
txt = m.ax.text(xx, yy, "%.2f" % (3.79,), zorder=5, ha='center',
                va='center', fontsize=20)
txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground="w")])


m.drawcities(labelbuffer=5, minarea=0.2)
m.postprocess(filename='test.png')
