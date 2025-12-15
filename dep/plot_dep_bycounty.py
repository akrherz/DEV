"""We have something from NRI to compare with."""

import click
import geopandas as gpd
import matplotlib.colors as mpcolors
from pydep.reference import KG_M2_TO_TON_ACRE
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.dep import RAMPS
from pyiem.plot import MapPlot
from pyiem.plot.colormaps import dep_erosion
from pyiem.reference import Z_OVERLAY2


@click.command()
@click.option("--year", type=int, required=True, help="year")
def main(year):
    """Go Main."""
    # Get DEP by huc12
    with get_sqlalchemy_conn("idep") as conn:
        idep = gpd.read_postgis(
            sql_helper("""
            with data as (
                select huc_12, sum(avg_loss) * :factor as loss
                from results_by_huc12
                where scenario = 0 and valid >= :sts and
                valid <= :ets GROUP by huc_12)
            select d.huc_12, d.loss, ST_Transform(simple_geom, 4326) as geo
            from data d JOIN huc12 h on (d.huc_12 = h.huc_12) WHERE
            h.scenario = 0 and h.states ~* 'IA'
            """),
            conn,
            geom_col="geo",
            params={
                "sts": f"{year}-01-01",
                "ets": f"{year}-12-31",
                "factor": KG_M2_TO_TON_ACRE,
            },
            index_col="huc_12",
        )  # type: ignore
    # Get counties so that we can later join
    with get_sqlalchemy_conn("postgis") as conn:
        counties = gpd.read_postgis(
            "select simple_geom, ugc from ugcs where substr(ugc, 3, 1) = 'C' "
            "and state = 'IA' and end_ts is null",
            conn,
            geom_col="simple_geom",
            index_col=None,
        )
    counties["cfips"] = counties["ugc"].str.slice(3, 6).astype(int)
    counties = counties.set_index("cfips")
    counties["dep"] = (
        gpd.sjoin(counties, idep, predicate="intersects")
        .groupby("cfips")["loss"]
        .mean()
    )
    counties["dep_std"] = (
        gpd.sjoin(counties, idep, predicate="intersects")
        .groupby("cfips")["loss"]
        .std()
    )
    mp = MapPlot(
        title=f"{year} DEP County Average + StdDev Hillslope Erosion",
        subtitle=(f"DEP Avg: {counties['dep'].mean():.1f} T/a/yr"),
        logo="dep",
        caption="Daily Erosion Project",
    )
    cmap = dep_erosion()
    bins = RAMPS["english"][1]
    norm = mpcolors.BoundaryNorm(bins, cmap.N)
    counties.to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        color=cmap(norm(counties["dep"])),
        zorder=Z_OVERLAY2,
    )
    counties["labels"] = counties.apply(
        lambda row: f"{row['dep']:.1f}\n+/- {row['dep_std']:.1f}",
        axis=1,
    )
    mp.plot_values(
        counties.centroid.x,
        counties.centroid.y,
        counties["labels"].values,
        fmt="%s",
        labelbuffer=0,
        textsize=10,
    )

    mp.draw_colorbar(bins, cmap, norm, units="T/a", extend="both")
    mp.drawcounties()
    mp.fig.savefig(f"dep_county_{year}.png")


if __name__ == "__main__":
    main()
