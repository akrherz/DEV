"""Diagnostic"""

import click
import geopandas as gpd
import numpy as np
from matplotlib.colors import BoundaryNorm
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.plot import MapPlot, get_cmap
from pyiem.reference import Z_POLITICAL
from pyiem.util import logger

LOG = logger()


@click.command()
def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("dep") as conn:
        fieldsdf = gpd.read_postgis(
            sql_helper(
                """
    select f.field_id, f.geom, rectangle_rotation_deg, f.acres,
    coalesce(r.drct, -1) as has_data
    from field f JOIN huc12 h on (f.huc12_id = h.huc12_id)
    LEFT JOIN field_wind_erosion_results r on
    (f.field_id = r.field_id and r.valid = '2026-05-12')
    where f.scenario_id = 0 and h.ugc = 'MNC119'
                """
            ),
            conn,
            params={},
            geom_col="geom",
            index_col="field_id",
        )  # type: ignore
    print(fieldsdf["has_data"].describe())
    LOG.info("Found %s fields", len(fieldsdf.index))
    minx, miny, maxx, maxy = fieldsdf.to_crs(4326)["geom"].total_bounds
    # minx, miny, maxx, maxy = (-96.874, 46.71621, -96.550, 47.065)
    print(minx, miny, maxx, maxy)
    mdlcount = (fieldsdf["has_data"] > -1).sum()
    total_acres = fieldsdf["acres"].sum()
    mdlacres = fieldsdf.loc[fieldsdf["has_data"] > -1, "acres"].sum()
    mp = MapPlot(
        apctx={"_r": "43"},
        # sector="state",
        # state="MN",
        sector="custom",
        south=miny,
        north=maxy,
        west=minx,
        east=maxx,
        title="Polk County",
        subtitle=(
            f"{mdlcount}/{len(fieldsdf.index)} fields modelled by WEPS, "
            f"{mdlacres:,.0f}/{total_acres:,.0f} acres"
        ),
        logo="dep",
        caption="Daily Erosion Project",
        continentalcolor="white",
        stateborderwidth=1,
    )
    bins = np.arange(0, 180.1, 30.0)
    # bins[0] = 0.01
    cmap = get_cmap("jet")
    # cmap.set_under("#0f0")
    norm = BoundaryNorm(bins, cmap.N)
    mp.draw_colorbar(bins, cmap, norm, title="Degrees", extend="neither")
    fieldsdf[fieldsdf["has_data"] > -1].to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        color="g",
        zorder=Z_POLITICAL,
        add_labels=False,
    )
    fieldsdf[fieldsdf["has_data"] < 0].to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        color="r",
        zorder=Z_POLITICAL,
        add_labels=False,
    )
    mp.fig.savefig("polk_fields.png")


if __name__ == "__main__":
    main()
