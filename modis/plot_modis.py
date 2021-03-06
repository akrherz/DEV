"""Generate a MODIS plot.

https://wvs.earthdata.nasa.gov/
"""

from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn
from pandas.io.sql import read_sql
import matplotlib.image as mpimg
from pyiem.plot import MapPlot
from shapely.wkb import loads
import psycopg2
import numpy as np
import cartopy.crs as ccrs


def main():
    """Go Main Go."""
    mp = MapPlot(
        title="11 August 2020 :: Aqua MODIS True Color",
        subtitle="10 August NWS Local Storm Report Wind Gusts [MPH] overlain",
        sector="custom",
        west=-96.40,
        east=-89.132,
        south=39.775,
        north=44.15,
        projection=ccrs.PlateCarree(),
    )

    img = plt.imread("snapshot-2020-08-11.jpg")
    mp.ax.imshow(
        img,
        extent=(-99.1495, -86.049, 36.7965, 46.5584),
        origin="upper",
        transform=ccrs.PlateCarree(),
        zorder=1,
    )
    mp.drawcounties("tan")
    df = read_sql(
        "SELECT distinct st_x(geom) as lon, st_y(geom) as lat, magnitude from "
        "lsrs_2020 where valid > '2020-08-10' and valid < '2020-08-11' and "
        "type = 'G' ORDER by magnitude DESC",
        get_dbconn("postgis"),
        index_col=None,
    )
    print(df)
    mp.plot_values(
        df["lon"].values,
        df["lat"].values,
        df["magnitude"].values,
        labeltextsize=8,
        fmt="%.0f",
        labelbuffer=1,
        color="white",
        outlinecolor="black",
    )

    mp.postprocess(filename="test.png")

    """
    cursor.execute('''select ST_asEWKB(ST_Transform(simple_geom,4326)) from roads_base
    WHERE segid in (select distinct segid from roads_2014_log where cond_code = 51 and valid > '2014-01-26')''')
    for row in cursor:
        if row[0] is None:
            continue
        line = loads( str(row[0]) )
        for geo in line.geoms:
            (lons, lats) = geo.xy
            x,y = m.map(lons, lats)
            m.ax.plot(x,y, color='orange', lw=2)

    cursor.execute('''
    SELECT ST_asEWKB(ST_Buffer(ST_Collect(geom),0)) from warnings_2014 where phenomena = 'BZ'
    and significance = 'W' and issue > '2014-01-26' and wfo in ('DMX','DVN', 'ARX') and substr(ugc, 1,2) = 'IA'
    ''')
    row = cursor.fetchone()
    geom = loads(str(row[0]))
    a = np.asarray(geom.exterior)
    x,y = m.map(a[:,0], a[:,1])
    m.ax.plot(x,y, color='red', lw=2.5, zorder=2)

    (fig, ax) = plt.subplots(2, 1)

    m = Basemap(projection='cea', llcrnrlat=40, urcrnrlat=44,
                llcrnrlon=-99, urcrnrlon=-89, resolution='i',
                ax=ax[0], fix_aspect=False)
    m2 = Basemap(projection='cea', llcrnrlat=40, urcrnrlat=44,
                llcrnrlon=-99, urcrnrlon=-89, resolution='i',
                ax=ax[1], fix_aspect=False)

    x, y = m(-99.4023, 38.7753)
    x2, y2 = m(-88.1321, 45.2504)

    img = mpimg.imread('aug22.jpg')
    ax[0].imshow(img, extent=(x, x2, y, y2))
    ax[0].set_title("22 August 2016 :: Terra MODIS True Color")

    img = mpimg.imread('oct23.jpg')
    ax[1].imshow(img, extent=(x, x2, y, y2))
    ax[1].set_title("23 October 2016 :: Aqua MODIS True Color")

    m.drawstates(linewidth=2.5)
    m2.drawstates(linewidth=2.5)
    plt.savefig('test.png')

    """


if __name__ == "__main__":
    main()
