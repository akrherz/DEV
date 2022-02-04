"""Plot what we have in myhucs.csv"""

from sqlalchemy import text
from geopandas import read_postgis
from pyiem.plot import MapPlot
from pyiem.reference import Z_POLITICAL
from pyiem.util import get_dbconnstr


def main():
    """Go Main Go."""
    with open("myhucs.txt", encoding="utf-8") as fh:
        myhucs = [x.strip() for x in fh.readlines()]
    df = read_postgis(
        text(
            "SELECT simple_geom from huc12 where scenario = 0 and "
            "huc_12 in :hucs"
        ),
        get_dbconnstr("idep"),
        params={"hucs": tuple(myhucs)},
        geom_col="simple_geom",
    )
    print(len(df.index), len(myhucs), df.crs)
    mp = MapPlot(
        apctx={"_r": "43"},
        sector="midwest",
        title="Orphan HUC12s after 4 Feb 2022 Reprocessing",
        logo="dep",
    )
    df = df.to_crs(mp.panels[0].crs)
    df.plot(
        aspect=None,
        ax=mp.panels[0].ax,
        color="red",
        zorder=Z_POLITICAL,
    )
    mp.fig.savefig("test.png")


if __name__ == "__main__":
    main()
