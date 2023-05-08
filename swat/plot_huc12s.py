"""Plot what we are provided for HUC12s."""

import pandas as pd
from geopandas import read_postgis
from pyiem.plot.geoplot import MapPlot
from pyiem.reference import Z_POLITICAL
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    df = pd.read_csv("match.csv")
    wbd = read_postgis(
        "SELECT huc12::bigint as huc12, simple_geom from wbd_huc12",
        get_dbconn("idep"),
        geom_col="simple_geom",
        index_col="huc12",
    )
    wbd["plotme"] = False
    for huc12 in df["HUC12"].values:
        if huc12 not in wbd.index:
            print(huc12)
            continue
        wbd.at[huc12, "plotme"] = True

    mp = MapPlot(
        sector="midwest",
        logo="dep",
        title=f"{len(df.index)} HUC12s matched to WBD",
        caption="",
    )
    wbd = wbd[wbd["plotme"]].to_crs(mp.panels[0].crs)
    wbd.plot(
        ax=mp.panels[0].ax,
        aspect=None,
        color="r",
        zorder=Z_POLITICAL,
    )
    mp.fig.savefig("test.png")


if __name__ == "__main__":
    main()
