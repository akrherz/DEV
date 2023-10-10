"""Generate a feature plot."""

import cartopy.crs as ccrs
import geopandas as gpd
import matplotlib.colors as mpcolors
from pyiem.plot import MapPlot
from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    df = gpd.read_file("/tmp/iowa.geojson")

    mp = MapPlot(
        sector="custom",
        west=-94.4,
        east=-91.1,
        south=40.4,
        north=41.6,
        title=(
            "NOAA MRMS Max Estimated Size of Hail (MESH) + "
            "NWS Local Storm Reports (LSR)"
        ),
        subtitle=(
            "Valid 12 PM 14 May - 3 AM 15 May 2020, plotted values are LSRs"
        ),
    )
    clevs = [0.1, 0.25, 0.5, 0.75, 1, 1.5, 2, 2.5, 3]
    cmap = plt.get_cmap("tab20c_r")
    norm = mpcolors.BoundaryNorm(clevs, cmap.N)
    for _i, row in df.iterrows():
        inch = row["ssize_mm"] / 25.4
        if inch < 0.1:
            continue
        mp.ax.add_geometries(
            [row["geometry"]],
            ccrs.PlateCarree(),
            facecolor=cmap(norm([inch]))[0],
            edgecolor="None",
        )
    mp.draw_colorbar(
        clevs, cmap, norm, units="inch", extend="max", spacing="proportional"
    )

    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()

    cursor.execute(
        "SELECT ST_x(geom) as lon, ST_y(geom) as lat, magnitude "
        "from lsrs_2020 where type = 'H' and valid > '2020-05-14 12:00' and "
        "valid < '2020-05-16' ORDER by magnitude DESC"
    )
    llons = []
    llats = []
    vals = []
    for row in cursor:
        llons.append(row[0])
        llats.append(row[1])
        vals.append("%.2f" % (row[2],))

    mp.drawcounties()
    mp.drawcities(labelbuffer=25, textsize=10, color="k", outlinecolor="None")
    mp.textmask[:, :] = 0
    mp.plot_values(llons, llats, vals, fmt="%s", labelbuffer=0)
    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
