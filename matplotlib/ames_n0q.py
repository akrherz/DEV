import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from pyiem import reference
from matplotlib.patches import Polygon
import numpy as np
import pygrib
import Image
from pyiem.plot import MapPlot
import matplotlib.patheffects as PathEffects

m = MapPlot('ames',
  title='Des Moines One Hour Stage IV Precipitation Estimate',
  subtitle='Valid: 26 Jun 2010 12:00 AM CDT')

m.map.readshapefile('high', 'roads', ax=m.ax, drawbounds=False)
for nshape, seg in enumerate(m.map.roads):
     if (m.map.roads_info[nshape]['US1'] in (69,30) or
        m.map.roads_info[nshape]['INT1'] == 35):
         data = np.array( seg )
         m.ax.plot(data[:,0], data[:,1], lw=2, linestyle='--',color='k',
                   zorder=3)

m.map.readshapefile('cities', 'cities', ax=m.ax)
for nshape, seg in enumerate(m.map.cities):
     if m.map.cities_info[nshape]['NAME10'] != 'Ames':
         continue
     poly=Polygon(seg, fc='None', ec='k', lw=1.5, zorder=3)
     m.ax.add_patch(poly)

img = Image.open('DMX_N0Q_201006260441.png')
data = np.copy( np.asarray(img) )
data = data.astype(np.float32)


n1p = np.arange(-32,70,0.5)
for i,v in enumerate(n1p):
  data[data==i] = v

ramp = [-10,0,10,15,20,25,30,35,40,45,50,55,60,65,70]

lons1x = np.arange(-99.280259, -99.280259 + 0.011115*1000.0, 0.011115)
lats1x = np.arange(47.288259, 47.288259 -  0.011115*1000.0, - 0.011115)

lons, lats = np.meshgrid( lons1x, lats1x)
res = m.pcolormesh(lons, lats, data, ramp, latlon=True, units='dbZ')

m.postprocess(filename='test.png')
