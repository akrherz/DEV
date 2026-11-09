"""Diagnostic"""

import click
import geopandas as gpd
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
        select f.field_id, geom, acres * erosion_kgm2 as et from
        field_wind_erosion_results r
        join field f on (r.field_id = f.field_id)
        where r.valid = '2026-05-14' and erosion_kgm2 > 0
                """
            ),
            conn,
            geom_col="geom",
            index_col="field_id",
        )  # type: ignore

    # Group the fields by the county they reside in and compute the
    # average erosion for that county
    countydf["data"] = -0.0001
    for idx, row in countydf.iterrows():
        localfields = fieldsdf[fieldsdf.within(row["geo"])]
        if len(localfields) < 10:
            print(f"Low sample count {idx} {len(localfields)}")
        countydf.loc[idx, "data"] = (
            localfields["et"].sum() * KG_M2_TO_TON_ACRE / 1000.0
        )
    print(countydf)

    stats = countydf["data"].describe(
        percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]
    )

    mp = MapPlot(
        apctx={"_r": "43"},
        sector="state",
        state="MN",
        title="2026-05-14 Eroding Kilo-Tons per County",
        subtitle=(
            f"County mean: {stats['mean']:.1f} "
            "kilo-tons, "
            f" 95%: {stats['95%']:.1f} "
            "kilo-tons,"
            f" max: {stats['max']:.1f} "
            "kilo-tons"
        ),
        logo="dep",
        caption="Daily Erosion Project",
        continentalcolor="white",
        stateborderwidth=1,
    )
    bins = [
        int(x)
        for x in [
            0,
            stats["5%"],
            stats["25%"],
            stats["50%"],
            stats["75%"],
            stats["95%"],
            stats["max"],
        ]
    ]
    bins = [0, 0, 0, 0, 2, 78, 428]

    cmap = get_cmap("plasma")
    cmap.set_under("#EEEEEE")
    norm = BoundaryNorm(bins, cmap.N)
    mp.draw_colorbar(
        bins,
        cmap,
        norm,
        title="kilo-tons",
        extend="max",
        spacing="proportional",
    )
    countydf.to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        facecolor=cmap(norm(countydf["data"].to_numpy())),
        edgecolor="k",
        zorder=Z_POLITICAL,
        add_labels=False,
    )
    # Plot the values at the centroid of the county
    hasdata = countydf[countydf["data"] >= 0]
    projected = hasdata["geo"].centroid.to_crs("EPSG:4326")
    mp.plot_values(
        projected.x,
        projected.y,
        hasdata["data"].to_numpy(),
        fmt="%.1f",
        labelbuffer=0,
        textsize=10,
    )

    mp.fig.savefig("260514_county_acres_tons.png")


if __name__ == "__main__":
    main()
