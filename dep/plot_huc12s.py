"""Plot what we have in myhucs.csv"""

from sqlalchemy import text
from geopandas import read_postgis
from pyiem.plot import MapPlot
from pyiem.reference import Z_POLITICAL
from pyiem.util import get_dbconnstr


def main():
    """Go Main Go."""
    with open("/tmp/myhucs.txt", encoding="utf-8") as fh:
        myhucs = [x.strip() for x in fh.readlines()]
    df = read_postgis(
        text(
            "SELECT simple_geom, huc_12 from huc12 where scenario = 0 and "
            "states ~* 'IA'"
        ),
        get_dbconnstr("idep"),
        geom_col="simple_geom",
    )
    print(len(df.index), len(myhucs), df.crs)
    mp = MapPlot(
        apctx={"_r": "43"},
        sector="iowa",
        title="30 HUC12s Selected For Climate Change Scenarios",
        logo="dep",
        nocaption=True,
        continentalcolor="white",
        stateborderwidth=3,
    )
    df.to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        facecolor="None",
        edgecolor="k",
        zorder=Z_POLITICAL,
    )
    df2 = df[df["huc_12"].isin(myhucs)]
    df2.to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        color="red",
        zorder=Z_POLITICAL,
    )
    mp.fig.savefig("test.png")


if __name__ == "__main__":
    main()
