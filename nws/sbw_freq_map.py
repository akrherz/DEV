"""Note, this does things the old and slow way"""

import matplotlib.pyplot as plt
import numpy as np
from pyiem import reference
from pyiem.plot import MapPlot
from pyiem.util import get_dbconn
from tqdm import tqdm


def main():
    """Go Main Go."""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()

    dx = 0.01
    lons = np.arange(reference.IA_WEST, reference.IA_EAST, dx)
    lats = np.arange(reference.IA_SOUTH, reference.IA_NORTH, dx)
    vals = np.zeros((len(lats), len(lons)))
    for i, lon in enumerate(tqdm(lons)):
        for j, lat in enumerate(lats):
            cursor.execute(
                """
            select eventid from sbw where
            ST_Covers(geom, ST_GeomFromEWKT('SRID=4326;POINT(%s %s)'))
            and status = 'NEW' and phenomena = 'TO' and significance = 'W'
            and issue < '2017-01-01' and issue > '2002-01-01'
            """,
                (lon, lat),
            )
            val = cursor.rowcount
            vals[j, i] = val / 15.0  # Number of years 2002-2016

    print("Maximum is: %.1f" % (np.max(vals),))

    m = MapPlot(
        sector="iowa",
        title="Avg Number of Storm Based Tornado Warnings per Year",
        subtitle=(
            "(2003 through 2016) based on unofficial "
            "archives maintained by the IEM, %sx%s analysis grid"
        )
        % (dx, dx),
    )
    cmap = plt.get_cmap("jet")
    cmap.set_under("white")
    cmap.set_over("black")
    lons, lats = np.meshgrid(lons, lats)
    rng = np.arange(0, 2.1, 0.2)
    rng[0] = 0.01
    m.pcolormesh(lons, lats, vals, rng, cmap=cmap, units="count")
    m.drawcounties()
    m.postprocess(filename="count.png")
    m.close()


if __name__ == "__main__":
    main()
