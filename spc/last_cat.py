import numpy as np
import psycopg2
import datetime
import pytz
import matplotlib.pyplot as plt
from tqdm import tqdm
from pyiem.plot import MapPlot
from pyiem import reference

pgconn = psycopg2.connect(database="postgis")
cursor = pgconn.cursor()

dx = 0.25
lons = np.arange(reference.CONUS_WEST, reference.CONUS_EAST, dx)
lats = np.arange(reference.CONUS_SOUTH, reference.CONUS_NORTH, dx)
years = np.zeros((len(lats), len(lons)))
utcnow = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
for i, lon in enumerate(tqdm(lons)):
    for j, lat in enumerate(lats):
        cursor.execute(
            """
        select issue, expire from spc_outlooks where
        ST_Contains(geom, ST_GeomFromEWKT('SRID=4326;POINT(%s %s)'))
        and threshold = 'HIGH' and category = 'CATEGORICAL'
        and outlook_type = 'C' and day = 1 ORDER by issue DESC LIMIT 1
        """,
            (lon, lat),
        )
        if cursor.rowcount == 0:
            val = 1900
        else:
            val = cursor.fetchone()[0].year
        years[j, i] = val

m = MapPlot(
    sector="conus",
    title="Year of Last Storm Prediction Center Day 1 High Risk",
    subtitle=(
        "(April 2002 - 5 April 2017 12z) based on unofficial "
        "archives maintained by the IEM, %sx%s analysis grid"
    )
    % (dx, dx),
)
cmap = plt.get_cmap("jet")
cmap.set_under("white")
cmap.set_over("black")
lons, lats = np.meshgrid(lons, lats)
m.pcolormesh(lons, lats, years, np.arange(2002, 2019, 1), cmap=cmap)
m.postprocess(filename="test.png")
m.close()
