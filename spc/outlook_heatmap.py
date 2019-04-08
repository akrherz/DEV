"""Heatmap of outlooks."""

from geopandas import read_postgis
from affine import Affine
from rasterstats import zonal_stats
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from pyiem.plot import MapPlot
from pyiem.util import get_dbconn

buffr = 5.
# 0.01 crashes my laptop, FYI
griddelta = 0.05
GRIDWEST = -139.2
GRIDEAST = -55.1
GRIDNORTH = 54.51
GRIDSOUTH = 19.47

PRECIP_AFF = Affine(griddelta, 0., GRIDWEST, 0., griddelta * -1, GRIDNORTH)
YSZ = (GRIDNORTH - GRIDSOUTH) / griddelta
XSZ = (GRIDEAST - GRIDWEST) / griddelta


def main():
    """Go Main Go."""
    ones = np.ones((int(YSZ), int(XSZ)))
    counts = np.zeros((int(YSZ), int(XSZ)))
    # counts = np.load('counts.npy')
    lons = np.arange(GRIDWEST, GRIDEAST, griddelta)
    lats = np.arange(GRIDSOUTH, GRIDNORTH, griddelta)

    pgconn = get_dbconn('postgis')
    df = read_postgis("""
        select valid, issue, expire, geom from spc_outlooks where
        outlook_type = 'C' and day = 1 and threshold = 'MRGL' and
        category = 'CATEGORICAL' and
        ST_Within(geom, ST_GeomFromEWKT('SRID=4326;POLYGON((%s %s, %s %s,
        %s %s, %s %s, %s %s))'))
        and extract(hour from valid at time zone 'UTC') in (15, 16)
        and valid < '2019-01-01' and valid > '2015-01-01'
        and ST_Area(geom) < 10000
    """, pgconn, params=(
        GRIDWEST, GRIDSOUTH, GRIDWEST, GRIDNORTH, GRIDEAST,
        GRIDNORTH, GRIDEAST, GRIDSOUTH, GRIDWEST, GRIDSOUTH),
                      geom_col='geom')
    for _, row in tqdm(df.iterrows(), total=len(df.index)):
        zs = zonal_stats(row['geom'], ones, affine=PRECIP_AFF, nodata=-1,
                         all_touched=True, raster_out=True)

        for z in zs:
            aff = z['mini_raster_affine']
            west = aff.c
            north = aff.f
            raster = np.flipud(z['mini_raster_array'])
            x0 = int((west - GRIDWEST) / griddelta)
            y1 = int((north - GRIDSOUTH) / griddelta)
            dy, dx = np.shape(raster)
            x1 = x0 + dx
            y0 = y1 - dy
            counts[y0:y1, x0:x1] += np.where(raster.mask, 0, 1)

    np.save('day1_0z', counts)

    YEARS = (2018. - 2015.) + 1.
    m = MapPlot(
        sector='conus',
        title='Avg Number of Day 1 (@16z) Categorical Marginal Risks per year',
        subtitle=("(2015 through 2018) based on unofficial "
                  "archives maintained by the IEM, %sx%s analysis grid"
                  ) % (griddelta, griddelta))
    cmap = plt.get_cmap('jet')
    cmap.set_under('white')
    cmap.set_over('black')
    lons, lats = np.meshgrid(lons, lats)
    # rng = np.arange(0., 3.1, 0.3)
    # rng[0] = 0.01
    data = counts / YEARS
    rng = [0.01, 0.5, 1, 3, 5, 7, 10, 15, 20, 25, 30, 40, 50]
    res = m.pcolormesh(
        lons, lats, data, rng, cmap=cmap, units='count')
    res.set_rasterized(True)
    # m.drawcounties()
    m.postprocess(filename='count.png')
    m.close()


if __name__ == '__main__':
    main()
