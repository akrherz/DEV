from geopandas import read_postgis
import psycopg2
from affine import Affine
from rasterstats import zonal_stats
import numpy as np
from tqdm import tqdm
from pyiem.plot import MapPlot
import matplotlib.pyplot as plt

buffr = 5.
griddelta = 0.01
GRIDWEST = -139.2
GRIDEAST = -55.1
GRIDNORTH = 54.51
GRIDSOUTH = 19.47

PRECIP_AFF = Affine(0.01, 0., GRIDWEST, 0., -0.01, GRIDNORTH)
YSZ = (GRIDNORTH - GRIDSOUTH) / 0.01
XSZ = (GRIDEAST - GRIDWEST) / 0.01

ones = np.ones((int(YSZ), int(XSZ)))
# counts = np.load('counts.npy')
lons = np.arange(GRIDWEST, GRIDEAST, griddelta)
lats = np.arange(GRIDSOUTH, GRIDNORTH, griddelta)

day1 = np.load('day1_12z.npy')
day2 = np.load('day1_0z.npy')

YEARS = (2016. - 2003.) + 1.
vals = (day2 - day1) / YEARS
print np.max(vals), np.min(vals)
m = MapPlot(sector='conus',
            title='SPC Convective Day1 Slight Risk: 0z(eve) issuance minus 12z issuance',
            subtitle=("(2003 through 2016) based on unofficial "
                      "archives maintained by the IEM, %sx%s analysis grid"
                      ) % (griddelta, griddelta))
cmap = plt.get_cmap('BrBG')
cmap.set_under('white')
cmap.set_over('black')
lons, lats = np.meshgrid(lons, lats)
rng = np.arange(-10, 11, 2.)
res = m.pcolormesh(lons, lats, vals,
                   rng, cmap=cmap, units='events per year')
res.set_rasterized(True)
m.ax.text(0.01, 0.04, ("Postive values mean higher Day 1 Slight Risk\n"
                       "frequency at 0z than 12z."),
          bbox=dict(color='white'), zorder=100, transform=m.ax.transAxes)
# m.drawcounties()
m.postprocess(filename='diff.png')
m.close()
