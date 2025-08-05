"""Create a map of where we have climate files!"""

import click
import geopandas as gpd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.plot import MapPlot
from pyiem.reference import Z_OVERLAY


@click.command()
@click.option("--domain", required=True)
def main(domain: str):
    """make maps, not war."""
    dbname = "idep" if domain == "" else f"dep_{domain}"
    print(f"Using database {dbname}")
    with get_sqlalchemy_conn(dbname) as pgconn:
        pts = gpd.read_postgis(
            sql_helper("""
    select geom from climate_files where scenario = 0
"""),
            pgconn,
            geom_col="geom",
        )  # type: ignore
    bounds = pts.total_bounds
    mp = MapPlot(
        logo="dep",
        sector="custom",
        west=bounds[0] - 1,
        east=bounds[2] + 1,
        south=bounds[1] - 1,
        north=bounds[3] + 1,
        title="Daily Erosion Project Climate File Locations",
        caption="Daily Erosion Project",
    )
    # All points will overwhelm matplotlib, so we need to plot them in chunks
    pts.to_crs(mp.panels[0].crs).plot(
        ax=mp.panels[0].ax,
        aspect=None,
        marker="o",
        markersize=3,
        zorder=Z_OVERLAY,
    )
    mp.fig.savefig(f"{domain}_climate_file_locations.png")


if __name__ == "__main__":
    main()
