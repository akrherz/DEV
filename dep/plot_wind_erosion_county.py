"""Diagnostic"""

import click
import geopandas as gpd
import numpy as np
from dailyerosion.reference import KG_M2_TO_TON_ACRE
from matplotlib.colors import BoundaryNorm
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import MapPlot, get_cmap
from pyiem.reference import Z_POLITICAL
from sqlalchemy import text


@click.command()
def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("postgis") as conn:
        countydf = gpd.read_postgis(
            text(
                """
    select st_transform(simple_geom, 5070) as geo, ugc
    from ugcs where substr(ugc, 1, 3) = 'MNC' and end_ts is null
                """
            ),
            conn,
            geom_col="geo",
            index_col="ugc",
        )  # type: ignore
    with get_sqlalchemy_conn("dep") as conn:
        fieldsdf = gpd.read_postgis(
            text(
                """
    with agg as (
        select f.field_id, sum(erosion_kgm2) as sum from
        field_wind_erosion_results r
        join field f on (r.field_id = f.field_id)
        where r.valid < '2027-01-01' and erosion_kgm2 > 0 group by f.field_id
    )
    select f.field_id, a.sum, f.geom
    from field f JOIN agg a on (f.field_id = a.field_id)
    ORDER by sum desc
                """
            ),
            conn,
            geom_col="geom",
            index_col="field_id",
        )  # type: ignore

    # Group the fields by the county they reside in and compute the
    # average erosion for that county
    countydf["t_a_yr"] = -0.0001
    for idx, row in countydf.iterrows():
        localfields = fieldsdf[fieldsdf.within(row["geo"])]
        if len(localfields) < 10:
            print(f"Low sample count {idx} {len(localfields)}")
            continue
        countydf.at[idx, "t_a_yr"] = (
            localfields["sum"].mean() * KG_M2_TO_TON_ACRE / 20.0
        )  # t/a/yr
    print(countydf)

    stats = countydf["t_a_yr"].describe(
        percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]
    )

    mp = MapPlot(
        apctx={"_r": "43"},
        sector="state",
        state="MN",
        title=r"2007-2025 Wind Erosion [$T a^{-1} yr^{-1}$]",
        subtitle=(
            f"County mean: {stats['mean']:.1f} "
            r"$T a^{-1} yr^{-1}$, "
            f" 95%: {stats['95%']:.1f} "
            r"$T a^{-1} yr^{-1}$,"
            f" max: {stats['max']:.1f} "
            r"$T a^{-1} yr^{-1}$"
        ),
        logo="dep",
        caption="Daily Erosion Project",
        continentalcolor="white",
        stateborderwidth=1,
    )
    bins = np.arange(0, 15.1, 1)
    cmap = get_cmap("plasma")
    cmap.set_under("#EEEEEE")
    norm = BoundaryNorm(bins, cmap.N)
    mp.draw_colorbar(
        bins, cmap, norm, title=r"$T a^{-1} yr^{-1}$", extend="both"
    )
    countydf.to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        facecolor=cmap(norm(countydf["t_a_yr"].to_numpy())),
        edgecolor="k",
        zorder=Z_POLITICAL,
    )
    # Plot the values at the centroid of the county
    hasdata = countydf[countydf["t_a_yr"] >= 0]
    projected = hasdata["geo"].centroid.to_crs("EPSG:4326")
    mp.plot_values(
        projected.x,
        projected.y,
        hasdata["t_a_yr"].to_numpy(),
        fmt="%.1f",
        labelbuffer=0,
        textsize=12,
    )

    mp.fig.savefig("county_wind_erosion.png")


if __name__ == "__main__":
    main()
