"""Make county plots of stuff."""

import datetime

from matplotlib import cm
from pyiem.database import get_dbconn
from pyiem.plot import MapPlot


def main():
    """Go Main Go."""
    pgconn = get_dbconn("postgis")
    pcursor = pgconn.cursor()

    opts = {
        "subtitle": "In Tornado Warning",
        "sdate": datetime.date(1986, 1, 1),
        "edate": datetime.date(2025, 7, 17),
        "normalized": True,
        "dbcols": ("TO",),
    }
    opts["title"] = "Tornado Warning Counts (County Based)"
    opts["years"] = float(opts["edate"].year - opts["sdate"].year)
    opts["units"] = "count"
    bins = [1, 2, 5, 10, 15, 20, 30, 45, 60, 75, 120, 150, 180, 240, 300]
    # bins = [1, 30, 60, 120, 240, 360, 480, 600, 840, 1080, 1320, 1540, 1760]
    # bins = [0.01,0.1,0.25,0.5,0.75,1,2,3,4,5,7,10,15]
    # bins = [0.1,1,2,5,7,10,15,20,25,30,40,50,60,70,80]

    if opts["normalized"]:
        opts["title"] += " (Normalized by County Size)"
        opts["units"] += " / sq km"
        bins = [0.0001, 0.01, 0.03, 0.07, 0.1, 0.15, 0.2, 0.25]

    fn = "%s_%s_%s_%s.png" % (
        opts["sdate"].year,
        opts["edate"].year,
        "-".join(opts["dbcols"]),
        "normalized" if opts["normalized"] else "count",
    )

    # bins = [0.001, 0.003, 0.005, 0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5,0.6,0.8]
    # bins = [1,2,3,4,5,6,7,8,9,10,15,20,30,50,100,125]
    # bins = [0.02,0.5, 1, 2, 4, 5, 6, 7, 8, 9, 10, 13, 16, 20, 24, 30]
    # bins = [1,2,5,10,15,20,25,30,45,60,75,90,120,150,180,240]
    # bins = [1,2,3,4,5,7,10,15,20,25,30,35,40,50,75,100]

    cmap = cm.get_cmap("jet")
    cmap.set_under("#ffffff")
    cmap.set_over("#000000")

    m = MapPlot(
        sector="nws",
        axisbg="#EEEEEE",
        title=opts["title"],
        subtitle=("%s, period: %s up till %s")
        % (
            opts["subtitle"],
            opts["sdate"].strftime("%-d %b %Y"),
            opts["edate"].strftime("%-d %b %Y"),
        ),
        cwas=True,
    )

    # norm = mpcolors.BoundaryNorm(bins, cmap.N)

    pcursor.execute(
        """
        WITH data as (
            SELECT ugc, count(*)  as data from warnings
            WHERE significance = 'W' and phenomena = 'TO'
            GROUP by ugc)
    select d.ugc, d.data / u.area2163 from data d, ugcs u WHERE
    d.ugc = u.ugc and u.end_ts is null
    """
    )
    data = {}
    for row in pcursor:
        data[row[0]] = float(row[1])

    m.fill_ugcs(
        data,
        bins=bins,
        cmap=cmap,
        units=opts["units"],
        spacing="proportional",
        clevstride=2,
    )

    m.postprocess(filename=fn)


if __name__ == "__main__":
    main()
