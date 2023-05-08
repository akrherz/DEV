"""Generate a MODIS plot.

https://wvs.earthdata.nasa.gov/
"""

import numpy as np

import matplotlib.image as mpimg
from pandas import read_sql
from pyiem.plot import MapPlot
from pyiem.plot.use_agg import plt
from pyiem.reference import Z_CLIP
from pyiem.util import get_dbconnstr
from shapely.wkb import loads


def main():
    """Go Main Go."""
    mp = MapPlot(
        title="7 February 2023 :: Aqua MODIS True Color",
        subtitle="with Iowa COOP morning snow depth [inch] reports",
        sector="custom",
        apctx={"_r": "43"},
        west=-97.0,
        east=-90.132,
        south=39.775,
        north=44.15,
        stateborderwidth=2,
    )

    img = plt.imread("/tmp/snapshot-2023-02-07.jpg")
    with open("/tmp/snapshot-2023-02-07.jgw", encoding="ascii") as fh:
        res = [float(x) for x in fh.readlines()]
    ulx = res[4]
    lrx = ulx + res[0] * img.shape[1]
    uly = res[5]
    lry = res[5] + res[3] * img.shape[0]
    mp.panels[0].ax.imshow(
        img,
        extent=(ulx, lrx, lry, uly),
        origin="upper",
        zorder=Z_CLIP,
    )
    mp.drawcounties("tan")
    df = read_sql(
        "SELECT st_x(geom) as lon, st_y(geom) as lat, snowd from "
        "summary_2023 s JOIN stations t on (s.iemid = t.iemid) "
        "where day = '2023-02-07' and network in ('IA_COOP') "
        "and snowd is not null ORDER by snowd ASC",
        get_dbconnstr("iem"),
        index_col=None,
    )
    print(df)
    mp.plot_values(
        df["lon"].values,
        df["lat"].values,
        df["snowd"].values,
        labeltextsize=8,
        fmt="%.0f",
        labelbuffer=1,
        color="white",
        outlinecolor="black",
    )

    mp.fig.savefig("230208.png")


def main2():
    """GO."""
    cursor.execute(
        """select ST_asEWKB(ST_Transform(simple_geom,4326)) from roads_base
    WHERE segid in (select distinct segid from roads_2014_log where cond_code = 51 and valid > '2014-01-26')"""
    )
    for row in cursor:
        if row[0] is None:
            continue
        line = loads(str(row[0]))
        for geo in line.geoms:
            (lons, lats) = geo.xy
            x, y = m.map(lons, lats)
            m.ax.plot(x, y, color="orange", lw=2)

    cursor.execute(
        """
    SELECT ST_asEWKB(ST_Buffer(ST_Collect(geom),0)) from warnings_2014 where phenomena = 'BZ'
    and significance = 'W' and issue > '2014-01-26' and wfo in ('DMX','DVN', 'ARX') and substr(ugc, 1,2) = 'IA'
    """
    )
    row = cursor.fetchone()
    geom = loads(str(row[0]))
    a = np.asarray(geom.exterior)
    x, y = m.map(a[:, 0], a[:, 1])
    m.ax.plot(x, y, color="red", lw=2.5, zorder=2)

    (fig, ax) = plt.subplots(2, 1)

    m = Basemap(
        projection="cea",
        llcrnrlat=40,
        urcrnrlat=44,
        llcrnrlon=-99,
        urcrnrlon=-89,
        resolution="i",
        ax=ax[0],
        fix_aspect=False,
    )
    m2 = Basemap(
        projection="cea",
        llcrnrlat=40,
        urcrnrlat=44,
        llcrnrlon=-99,
        urcrnrlon=-89,
        resolution="i",
        ax=ax[1],
        fix_aspect=False,
    )

    x, y = m(-99.4023, 38.7753)
    x2, y2 = m(-88.1321, 45.2504)

    img = mpimg.imread("aug22.jpg")
    ax[0].imshow(img, extent=(x, x2, y, y2))
    ax[0].set_title("22 August 2016 :: Terra MODIS True Color")

    img = mpimg.imread("oct23.jpg")
    ax[1].imshow(img, extent=(x, x2, y, y2))
    ax[1].set_title("23 October 2016 :: Aqua MODIS True Color")

    m.drawstates(linewidth=2.5)
    m2.drawstates(linewidth=2.5)
    plt.savefig("test.png")


if __name__ == "__main__":
    main()
