"""Generate a plot of MESH."""

import shapefile
from shapely.geometry import shape
import cartopy.crs as ccrs
import rasterio
import numpy as np
from pyiem.util import mm2inch, get_dbconn
from pyiem.plot import MapPlot, get_cmap


def main():
    """Go Main Go."""
    with rasterio.open("mesh.tif") as rio:
        arr = rio.read(1)
    print(arr.shape)
    # 130W 55N
    mp = MapPlot(
        twitter=True,
        sector="custom",
        south=41.4,
        east=-93.3,
        north=42.3,
        west=-94.4,
        title=(
            "9 July 2021 :: MRMS Max Estimated Hail Size + NWS Local Storm "
            "Reports of Hail (inch)"
        ),
        subtitle=(
            "MRMS 6 Hour MESH ending 3 PM 9 July 2021 CDT, "
            "Plotted for region including Des Moines"
        ),
    )
    shp = shapefile.Reader("../matplotlib/high.shp")
    for record in shp.shapeRecords():
        geo = shape(record.shape)
        mp.ax.add_geometries(
            [geo],
            ccrs.PlateCarree(),
            edgecolor="tan",
            facecolor="None",
            lw=1,
            zorder=5,
        )

    cmap = get_cmap("jet")
    cmap.set_under("white")
    mp.pcolormesh(
        np.arange(-100, -90, 0.01),
        np.arange(45, 35, -0.01),
        mm2inch(arr[1000:2000, 3000:4000]),
        np.arange(0.25, 3.26, 0.25),
        units="inch",
        cmap=cmap,
        extend="neither",
    )
    mp.drawcounties()

    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()

    cursor.execute(
        """SELECT ST_x(geom) as lon, ST_y(geom) as lat,
    max(magnitude) from lsrs_2021
    where wfo in ('DMX') and typetext = 'HAIL' and
    valid > '2021-07-09' GROUP by lon, lat ORDER by max DESC"""
    )
    llons = []
    llats = []
    vals = []
    for row in cursor:
        llons.append(row[0])
        llats.append(row[1])
        vals.append("%.2f" % (row[2],))
    mp.plot_values(
        llons, llats, vals, fmt="%s", textsize=13, color="k", labelbuffer=1
    )
    mp.drawcities(labelbuffer=5, minpop=1000)

    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
