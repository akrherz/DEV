"""Diagnostic"""

import click
from sqlalchemy import text

import geopandas as gpd
from matplotlib.patches import Rectangle
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import MapPlot
from pyiem.reference import Z_POLITICAL


@click.command()
@click.option("--huc12", help="HUC12 to plot")
@click.option("--fbndid", type=int, help="Field ID to plot")
def main(huc12, fbndid):
    """Go Main Go."""
    params = {
        "huc12": huc12,
        "fbndid": fbndid,
    }
    # fbndsql = "" if fbndid is None else " and fbndid = :fbndid"
    with get_sqlalchemy_conn("idep") as conn:
        huc12df = gpd.read_postgis(
            text(
                """
                select huc12, geom, name from wbd_huc12 where
                huc12 = :huc12
                """
            ),
            conn,
            params=params,
            geom_col="geom",
            index_col="huc12",
        )
        fieldsdf = gpd.read_postgis(
            text(
                """
                select fbndid, geom, isag from fields where scenario = 0
                and huc12 = :huc12
                """
            ),
            conn,
            params=params,
            geom_col="geom",
            index_col="fbndid",
        )
        fpdf = gpd.read_postgis(
            text(
                """
                select fpath, geom from flowpaths where scenario = 0
                and huc_12 = :huc12
                """
            ),
            conn,
            params=params,
            geom_col="geom",
            index_col="fpath",
        )
    minx, miny, maxx, maxy = (
        fieldsdf.loc[[fbndid]].to_crs(4326)["geom"].total_bounds
    )
    buffer = 0.001
    ff = (
        "Fields"
        if fbndid is None
        else f"Centered on Field {fbndid} + Flowpaths"
    )
    mp = MapPlot(
        apctx={"_r": "43"},
        sector="spherical_mercator",
        south=miny - buffer,
        north=maxy + buffer,
        west=minx - buffer,
        east=maxx + buffer,
        title=(f"HUC12 {huc12df.iloc[0]['name']} ({huc12}) {ff}"),
        logo="dep",
        caption="Iowa Daily Erosion Project",
        continentalcolor="white",
        stateborderwidth=3,
    )

    huc12df.to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        ec="k",
        fc="None",
        zorder=Z_POLITICAL,
    )
    fieldsdf[fieldsdf["isag"]].to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        ec="#EEEEEE",
        fc="green",
        zorder=Z_POLITICAL,
    )
    fieldsdf[~fieldsdf["isag"]].to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        ec="#EEEEEE",
        fc="brown",
        zorder=Z_POLITICAL,
    )
    fieldsdf.loc[[fbndid]].to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        ec="yellow",
        lw=3,
        fc="None",
        zorder=Z_POLITICAL + 1,
    )
    fpdf.to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        color="k",
        lw=3,
        zorder=Z_POLITICAL,
    )
    for fp, row in fpdf.to_crs(mp.panels[0].crs).iterrows():
        mp.panels[0].ax.text(
            row.geom.centroid.x + 30,
            row.geom.centroid.y + 30,
            str(fp),
            ha="left",
            va="top",
            color="yellow",
            fontsize=12,
            zorder=Z_POLITICAL + 1,
        )
    # mp.drawcounties()
    mp.panels[0].ax.legend(
        handles=[
            Rectangle((0, 0), 1, 1, fc="brown"),
            Rectangle((0, 0), 1, 1, fc="green"),
        ],
        labels=["Non-AG", "AG"],
    ).set_zorder(Z_POLITICAL + 2)

    mp.fig.savefig(f"/tmp/fields_{huc12}.png")


if __name__ == "__main__":
    main()
