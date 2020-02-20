"""Make a plot of all the bot warnings"""

from geopandas import read_postgis
from pyiem.plot import MapPlot
from pyiem.util import get_dbconn
import cartopy.crs as ccrs


def main():
    """Go Main"""
    pgconn = get_dbconn("postgis")
    df = read_postgis(
        """
    select geom, issue from bot_warnings where wfo = 'DMX'
    """,
        pgconn,
        geom_col="geom",
        crs={"init": "epsg:4326", "no_defs": True},
    )

    bounds = df["geom"].total_bounds
    # bounds = [-102.90293903,   40.08745967,  -97.75622311,   43.35172981]
    bbuf = 0.25
    mp = MapPlot(
        sector="custom",
        west=bounds[0] - bbuf,
        south=bounds[1] - bbuf,
        east=bounds[2] + bbuf,
        north=bounds[3] + bbuf,
        continentalcolor="white",
        title="Bot Issued Tornado Warnings [2008-2019] for DMX",
        subtitle="%s warnings plotted" % (len(df.index),),
    )
    crs_new = ccrs.Mercator()
    crs = ccrs.PlateCarree()
    new_geometries = [
        crs_new.project_geometry(ii, src_crs=crs) for ii in df["geom"].values
    ]
    mp.draw_cwas()
    mp.ax.add_geometries(
        new_geometries,
        crs=crs_new,
        edgecolor="r",
        facecolor="None",
        alpha=1.0,
        lw=0.5,
        zorder=10,
    )
    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
