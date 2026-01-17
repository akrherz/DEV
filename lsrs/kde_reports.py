"""Legacy."""

import matplotlib.pyplot as plt
import numpy
from pyiem import reference
from pyiem.database import get_dbconn
from pyiem.plot import MapPlot
from scipy import stats


def main():
    """Go Main Go."""
    POSTGIS = get_dbconn("postgis")
    cursor = POSTGIS.cursor()

    lons = []
    lats = []
    cursor.execute(
        """
    SELECT x(geom), y(geom), valid,
    x(ST_Transform(geom,2163)), y(ST_Transform(geom,2163)) from lsrs
    where  typetext = 'HAIL'
    and x(geom) between %s and %s and y(geom) between %s and %s
    and magnitude >= 1 ORDER by valid ASC
    """,
        (
            reference.MW_WEST - 3,
            reference.MW_EAST + 3,
            reference.MW_SOUTH - 3,
            reference.MW_NORTH + 3,
        ),
    )
    recent = []
    for row in cursor:
        valid = row[2]
        dup = False
        for r in recent:
            tdelta = (valid - r[0]).days * 86400.0 + (valid - r[0]).seconds
            if tdelta > 15 * 60:
                recent.remove(r)
                continue
            ddelta = ((row[3] - r[1]) ** 2 + (row[4] - r[2]) ** 2) ** 0.5
            if ddelta < 15000 and tdelta < 15 * 60:
                dup = True
        if dup:
            # print 'DUP', row
            continue
        recent.append([valid, row[3], row[4]])
        lons.append(row[0])
        lats.append(row[1])

    X, Y = numpy.mgrid[
        reference.MW_WEST : reference.MW_EAST : 50j,
        reference.MW_SOUTH : reference.MW_NORTH : 50j,
    ]
    positions = numpy.vstack([X.ravel(), Y.ravel()])
    values = numpy.vstack([lons, lats])
    kernel = stats.gaussian_kde(values)
    Z = numpy.reshape(kernel(positions).T, X.shape)

    m = MapPlot(
        sector="midwest",
        title='Local Storm Reports of Hail (1+") :: Kernel Density Estimate',
        subtitle=(
            "2003 - May 2013, gaussian kernel, 15min/15km duplicate "
            "rule applied"
        ),
    )

    m.pcolormesh(
        X,
        Y,
        Z,
        numpy.arange(0, 0.006, 0.0003),
        cmap=plt.cm.gist_earth_r,
        latlon=True,
    )

    m.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
