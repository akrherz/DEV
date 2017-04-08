from geopandas import read_postgis
import psycopg2
from affine import Affine
from rasterstats import zonal_stats
import numpy as np
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
#counts = np.zeros((int(YSZ), int(XSZ)))
counts = np.load('counts.npy')
lons = np.arange(GRIDWEST, GRIDEAST, griddelta)
lats = np.arange(GRIDSOUTH, GRIDNORTH, griddelta)

pgconn = psycopg2.connect(database='postgis', host='localhost', port=5555,
                          user='nobody')
# TODO: Figure out which 2017 SVR warning causes segfault!
for year in range(2015, 2017):
    df = read_postgis("""SELECT ST_Forcerhr(geom) as geom, wfo, eventid
     from sbw_""" + str(year) + """ where eventid not in (205, 328, 275, 325) and 
     phenomena = 'SV' and status = 'NEW' and significance = 'W' and eventid not in (76)
     and ST_Within(geom, ST_GeomFromEWKT('SRID=4326;POLYGON((%s %s, %s %s,
     %s %s, %s %s, %s %s))')) and ST_IsValid(geom) ORDER by wfo, eventid
     """, pgconn, params=(GRIDWEST, GRIDSOUTH, GRIDWEST, GRIDNORTH, GRIDEAST,
                          GRIDNORTH, GRIDEAST, GRIDSOUTH, GRIDWEST, GRIDSOUTH),
                      geom_col='geom')
    print year, len(df.index)
    for i, row in df.iterrows():
        print row['wfo'], row['eventid'], row['geom']
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
    np.save('counts', counts)

print np.max(counts) / 15.
m = MapPlot(sector='conus',
            title='Avg Number of Storm Based Severe T\'Storm Warnings per Year',
            subtitle=("(2002 through 2016) based on unofficial "
                      "archives maintained by the IEM, %sx%s analysis grid"
                      ) % (griddelta, griddelta))
cmap = plt.get_cmap('jet')
cmap.set_under('white')
cmap.set_over('black')
lons, lats = np.meshgrid(lons, lats)
rng = np.arange(0, 14.1, 1.)
rng[0] = 0.01
m.pcolormesh(lons, lats, counts / 15.,
             rng, cmap=cmap, units='count')
# m.drawcounties()
m.postprocess(filename='count.png')
m.close()
