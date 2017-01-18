import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
from scipy.interpolate import NearestNDInterpolator

m = Basemap(llcrnrlon=-100, llcrnrlat=38,
            urcrnrlon=-86, urcrnrlat=46)

m.drawstates()

lons = np.arange(-110, -80, 1)
lats = np.arange(30, 60, 1)
vals = np.arange(30)
xi = np.linspace(-120, -60, 100)
yi = np.linspace(23, 50, 100)
xi, yi = np.meshgrid(xi, yi)
nn = NearestNDInterpolator((lons, lats), vals)
vals = nn(xi, yi)
m.contourf(xi, yi, vals, 20, zorder=2)
m.drawstates(zorder=3)
plt.savefig('test.png')
