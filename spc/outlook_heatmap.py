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
counts = np.zeros((int(YSZ), int(XSZ)))
# counts = np.load('counts.npy')
lons = np.arange(GRIDWEST, GRIDEAST, griddelta)
lats = np.arange(GRIDSOUTH, GRIDNORTH, griddelta)

pgconn = psycopg2.connect(database='postgis', host='localhost', port=5555,
                          user='nobody')
df = read_postgis("""select valid, issue, expire, geom from spc_outlooks where
 outlook_type = 'C' and day = 1 and threshold = 'SLGT' and
 category = 'CATEGORICAL' and
 ST_Within(geom, ST_GeomFromEWKT('SRID=4326;POLYGON((%s %s, %s %s,
 %s %s, %s %s, %s %s))'))
 and extract(hour from valid at time zone 'UTC') in (0, 1)
 and valid < '2017-01-01' and valid > '2003-01-01'
 """, pgconn, params=(GRIDWEST, GRIDSOUTH, GRIDWEST, GRIDNORTH, GRIDEAST,
                      GRIDNORTH, GRIDEAST, GRIDSOUTH, GRIDWEST, GRIDSOUTH),
                  geom_col='geom')
for i, row in tqdm(df.iterrows(), total=len(df.index)):
    zs = zonal_stats(row['geom'], ones, affine=PRECIP_AFF, nodata=-1,
                     all_touched=True, raster_out=True)

    for z in zs:
        aff = z['mini_raster_affine']
        west = aff.c
        north = aff.f
        raster = np.flipud(z['mini_raster_array'])
        x0 = int((west - GRIDWEST) / 0.01)
        y1 = int((north - GRIDSOUTH) / 0.01)
        dy, dx = np.shape(raster)
        x1 = x0 + dx
        y0 = y1 - dy
        # print np.shape(raster.mask), west, x0, x1, XSZ, north, y0, y1, YSZ
        counts[y0:y1, x0:x1] += np.where(raster.mask, 0, 1)

np.save('day1_0z', counts)

YEARS = (2016. - 2003.) + 1.
print np.max(counts) / YEARS
m = MapPlot(sector='conus',
            title='Avg Number of Day 1 (@16z) Convective Slight Risks per year',
            subtitle=("(2003 through 2016) based on unofficial "
                      "archives maintained by the IEM, %sx%s analysis grid"
                      ) % (griddelta, griddelta))
cmap = plt.get_cmap('jet')
cmap.set_under('white')
cmap.set_over('black')
lons, lats = np.meshgrid(lons, lats)
# rng = np.arange(0., 2.8, 0.3)
# rng[0] = 0.01
rng = [0.01, 0.5, 1, 3, 5, 7, 10, 15, 20, 25, 28, 29, 30]
res = m.pcolormesh(lons, lats, counts / YEARS,
                   rng, cmap=cmap, units='count')
res.set_rasterized(True)
# m.drawcounties()
m.postprocess(filename='count.png')
m.close()
