"""Generate a MODIS plot.

https://wvs.earthdata.nasa.gov/
"""

import matplotlib.colors as mpcolors
from pandas import read_sql
from pyiem.plot import MapPlot, get_cmap
from pyiem.plot.use_agg import plt
from pyiem.reference import Z_CLIP
from pyiem.util import get_dbconnstr


def main():
    """Go Main Go."""
    mp = MapPlot(
        title=(
            "4 September 2024 :: Terra MODIS Corrected Reflectance True Color"
        ),
        sector="custom",
        apctx={"_r": "96"},
        west=-97.6,
        east=-89.5,
        south=40.1,
        north=42.95,
        stateborderwidth=2,
    )

    img = plt.imread("/tmp/snapshot-2024-09-04.jpg")
    with open("/tmp/snapshot-2024-09-04.jgw", encoding="ascii") as fh:
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
    # mp.drawcounties("tan")
    df = read_sql(
        """
        SELECT st_x(geom) as lon, st_y(geom) as lat, max_tmpf, snowd,
        network from summary_2023 s JOIN stations t on (s.iemid = t.iemid)
        where day = '2023-11-27' and (network ~* 'ASOS' or network ~* 'COOP')
        and id != 'VER'
        """,
        get_dbconnstr("iem"),
        index_col=None,
    )
    df2 = df[df["snowd"] > 0.01]
    mp.plot_values(
        df2["lon"].values,
        df2["lat"].values,
        ["."] * len(df2.index),
        labeltextsize=6,
        color="blue",
        fmt="%s",
        labelbuffer=0,
        outlinecolor="blue",
    )
    df2 = df[df["max_tmpf"] > 0]
    # create a simple color ramp for the temperatures
    cmap = get_cmap("RdYlBu_r")
    cmap.set_under("white")
    cmap.set_over("black")
    norm = mpcolors.BoundaryNorm([25, 30, 32, 35, 40, 50, 60], cmap.N)
    mp.plot_values(
        df2["lon"].values,
        df2["lat"].values,
        df2["max_tmpf"].values,
        labeltextsize=8,
        fmt="%.0f",
        labelbuffer=1,
        color=[x for x in cmap(norm(df2["max_tmpf"].values))],
        outlinecolor="black",
        isolated=True,
    )

    mp.fig.savefig("240905.png")


if __name__ == "__main__":
    main()
