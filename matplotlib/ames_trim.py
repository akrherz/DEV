import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from pyiem import reference
from matplotlib.patches import Polygon
import numpy as np
import netCDF4
from PIL import Image
from pyiem.plot import MapPlot
import matplotlib.patheffects as PathEffects

m = MapPlot(sector='custom', north=42.5, east=-92., south=40.9, west=-94.,
  title='NASA TRMM 3 Hour Total Precipitation',
  subtitle='Valid: 25 Jun 2010 10 PM to 26 Jun 2010 1 AM CDT')

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

nc = netCDF4.Dataset('3B42.100626.6.6A.nc')

lats = nc.variables['lat'][:]
lons = nc.variables['lon'][:]
lons, lats = np.meshgrid(lons, lats)
pcpn = nc.variables['precipitation'][:,:] / 24.5 * 3
n1p = [0,0.01,0.1,0.3,0.5,0.8,1.0,1.3,1.5,1.8,2.0,2.5,3.0,4.0,6.0,8.0]
m.pcolormesh(lons, lats, pcpn, n1p, latlon=True)

xx, yy = m.map(-93.6, 42.02)
txt = m.ax.text(xx, yy, "%.2f" % (0.65,) , zorder=5, ha='center',
          va='center', fontsize=20)
txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground="w")])

xx, yy = m.map(-93.64, 42.02)
txt = m.ax.text(xx, yy, "%.2f" % (0.39,) , zorder=5, ha='center',
          va='center', fontsize=20)
txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground="w")])



m.postprocess(filename='test.png')
