"""Likely outdated now."""
import datetime

import numpy as np
import pytz
from pyiem.util import get_dbconn
from pyiem.plot import MapPlot
from pyiem import reference
from tqdm import tqdm
import matplotlib.pyplot as plt

pgconn = get_dbconn("postgis")
cursor = pgconn.cursor()

dx = 0.25
lons = np.arange(reference.CONUS_WEST, reference.CONUS_EAST, dx)
lats = np.arange(reference.CONUS_SOUTH, reference.CONUS_NORTH, dx)
vals = np.zeros((len(lats), len(lons)))
utcnow = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
for i, lon in enumerate(tqdm(lons)):
    for j, lat in enumerate(lats):
        cursor.execute(
            """
        select distinct date(issue) from spc_outlooks where
        ST_Contains(geom, ST_GeomFromEWKT('SRID=4326;POINT(%s %s)'))
        and threshold = 'MDT' and category = 'CATEGORICAL'
        and outlook_type = 'C' and day = 2
        """,
            (lon, lat),
        )
        val = cursor.rowcount
        vals[j, i] = val

m = MapPlot(
    sector="conus",
    title="Number of Storm Prediction Center Day 2 Moderate Risks",
    subtitle=(
        "(April 2002 - 4 April 2017) based on unofficial "
        "archives maintained by the IEM, %sx%s analysis grid"
    )
    % (dx, dx),
)
cmap = plt.get_cmap("jet")
cmap.set_under("white")
cmap.set_over("black")
lons, lats = np.meshgrid(lons, lats)
rng = np.arange(0, 41, 4)
rng[0] = 1
m.pcolormesh(lons, lats, vals, rng, cmap=cmap, units="count")
m.postprocess(filename="count.png")
m.close()
