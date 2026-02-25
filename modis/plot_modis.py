"""Generate a MODIS plot.

https://wvs.earthdata.nasa.gov/
"""

import matplotlib.colors as mpcolors
import pandas as pd
from matplotlib.image import imread
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.plot import MapPlot, get_cmap
from pyiem.reference import Z_CLIP


def main():
    """Go Main Go."""
    mp = MapPlot(
        title=(
            "22 February 2026 :: Terra MODIS Corrected Reflectance True Color"
        ),
        subtitle="24 February 2026 ASOS Max Temperature (°F)",
        sector="custom",
        apctx={"_r": "96"},
        west=-97.6,
        east=-89.5,
        south=40.1,
        north=42.95,
        stateborderwidth=2,
    )

    img = imread("/tmp/snapshot-2026-02-22.jpg")
    with open("/tmp/snapshot-2026-02-22.jgw", encoding="ascii") as fh:
        res = [float(x) for x in fh.readlines()]
    a, _d, _b, e, c, f = res
    nrows, ncols = img.shape[:2]

    left = c - a / 2.0
    right = left + a * ncols
    top = f - e / 2.0
    bottom = top + e * nrows

    xmin, xmax = sorted((left, right))
    ymin, ymax = sorted((bottom, top))
    mp.panels[0].ax.imshow(
        img,
        extent=(xmin, xmax, ymin, ymax),
        origin="upper" if e < 0 else "lower",
        zorder=Z_CLIP,
    )
    # mp.drawcounties("tan")
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            sql_helper("""
            SELECT st_x(geom) as lon, st_y(geom) as lat, max_tmpf, snowd,
            network from summary_2026 s JOIN stations t on (s.iemid = t.iemid)
            where day = '2026-02-24' and (network ~* 'ASOS')
            and max_tmpf > 0
            """),
            conn,
            index_col=None,
        )
    # create a simple color ramp for the temperatures
    cmap = get_cmap("RdBu_r")
    cmap.set_under("white")
    cmap.set_over("black")
    norm = mpcolors.BoundaryNorm([25, 32, 40, 50, 60], cmap.N)
    mp.plot_values(
        df["lon"].to_numpy(),
        df["lat"].to_numpy(),
        df["max_tmpf"].to_numpy(),
        labeltextsize=12,
        fmt="%.0f",
        labelbuffer=1,
        color="white",
        outlinecolor="black",
        backgroundcolor=[x for x in cmap(norm(df["max_tmpf"].to_numpy()))],
        isolated=True,
    )

    mp.fig.savefig("260225.png")


if __name__ == "__main__":
    main()
