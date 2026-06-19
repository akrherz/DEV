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
    select simple_geom, ugc from ugcs where substr(ugc, 1, 3) = 'MNC'
    and end_ts is null
                """
            ),
            conn,
            geom_col="simple_geom",
            index_col="ugc",
        )  # type: ignore
    with get_sqlalchemy_conn("idep") as conn:
        fieldsdf = gpd.read_postgis(
            text(
                """
    select f.field_id, sum(erosion_kgm2), ST_Transform(geom, 4326) as geo from
    field_wind_erosion_results r
    join fields f on (r.field_id = f.field_id) where r.valid < '2026-01-01'
    and erosion_kgm2 >= 0 group by f.field_id, geo
                """
            ),
            conn,
            geom_col="geo",
            index_col="field_id",
        )  # type: ignore

    # Group the fields by the county they reside in and compute the
    # average erosion for that county
    countydf["t_a_yr"] = np.nan
    for idx, row in countydf.iterrows():
        localfields = fieldsdf[fieldsdf.within(row["simple_geom"])]
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
    bins[0] = 0.01
    cmap = get_cmap("plasma")
    cmap.set_bad("#fff")
    norm = BoundaryNorm(bins, cmap.N)
    mp.draw_colorbar(
        bins, cmap, norm, title=r"$T a^{-1} yr^{-1}$", extend="both"
    )
    hasdata = countydf[countydf["t_a_yr"].notna()]
    hasdata.to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        facecolor=cmap(norm(hasdata["t_a_yr"].to_numpy())),
        edgecolor="k",
        zorder=Z_POLITICAL,
    )
    # Plot the values at the centroid of the county
    mp.plot_values(
        hasdata["simple_geom"].centroid.x,
        hasdata["simple_geom"].centroid.y,
        hasdata["t_a_yr"].to_numpy(),
        fmt="%.1f",
        labelbuffer=0,
        textsize=12,
    )

    mp.fig.savefig("county_wind_erosion.png")


if __name__ == "__main__":
    main()
