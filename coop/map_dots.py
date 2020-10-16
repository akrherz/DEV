"""A map of dots!"""
from pyiem.plot import MapPlot
from pyiem.reference import Z_OVERLAY
from pyiem.util import get_dbconn
import cartopy.crs as ccrs
from pandas.io.sql import read_sql


def main():
    """Go Main Go."""
    pgconn = get_dbconn("iem")

    df = read_sql(
        """SELECT ST_x(geom) as x, ST_y(geom) as y,
    min(min_tmpf) as val, state, count(*) from
    summary s JOIN stations t on (t.iemid = s.iemid) WHERE
    s.day > '2020-09-01' and min_tmpf is not null and t.country = 'US' and
    t.network ~* 'COOP' and t.state in ('IA', 'MN', 'ND', 'SD', 'NE',
    'KS', 'MO', 'WI', 'IL', 'IN', 'OH', 'MI', 'KY') GROUP by y, x, state
    ORDER by val ASC""",
        pgconn,
        index_col=None,
    )
    df = df[(df["count"] > 30)]

    x3 = df[(df.val < 40) & (df.val >= 32)]
    x2 = df[(df.val < 32) & (df.val >= 29)]
    x1 = df[(df.val < 29) & (df.val >= 20)]
    x0 = df[df.val < 20]

    mp = MapPlot(
        title="Fall 2020 Minimum Temperature Reports",
        axisbg="white",
        subtitle=("Based on NWS Cooperative Observer Data, thru 27 Dec 2016"),
        sector="midwest",
    )
    mp.ax.scatter(
        x3.x,
        x3.y,
        marker="o",
        color="g",
        s=50,
        zorder=Z_OVERLAY,
        label=r"32 to 40$^\circ$F",
        transform=ccrs.PlateCarree(),
    )
    mp.ax.scatter(
        x2.x,
        x2.y,
        marker="s",
        color="b",
        zorder=Z_OVERLAY,
        s=50,
        label=r"29 to 31$^\circ$F",
        transform=ccrs.PlateCarree(),
    )
    mp.ax.scatter(
        x1.x,
        x1.y,
        marker="+",
        color="r",
        s=50,
        zorder=Z_OVERLAY + 1,
        label=r"20 to 28$^\circ$F",
        transform=ccrs.PlateCarree(),
    )
    mp.ax.scatter(
        x0.x,
        x0.y,
        marker="v",
        facecolor="w",
        edgecolor="k",
        s=50,
        zorder=Z_OVERLAY + 2,
        label=r"Sub 20$^\circ$F",
        transform=ccrs.PlateCarree(),
    )

    mp.ax.legend(loc=4, scatterpoints=1, ncol=4)

    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
