"""Plot of NWS Warnings."""

import geopandas as gpd
import pandas as pd
from matplotlib.colors import BoundaryNorm
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.plot import MapPlot, get_cmap
from pyiem.reference import Z_OVERLAY


def main():
    """Go Main"""
    with get_sqlalchemy_conn("postgis") as conn:
        warningsdf: pd.DataFrame = gpd.read_postgis(
            sql_helper("""
    with data as (
        select w.geom, w.wfo, w.vtec_year,
        rank() OVER (PARTITION by w.vtec_year
        ORDER by w.issue ASC) from sbw w, states s WHERE w.status = 'NEW' and
        w.phenomena = 'SV' and w.significance = 'W' and
        w.wfo in ('DMX', 'DVN', 'ARX', 'FSD', 'OAX') and
        ST_Intersects(w.geom, s.the_geom) and s.state_abbr = 'IA'
        and ST_Area(ST_Intersection(w.geom, s.the_geom)) > 0.02
    )
    SELECT geom, wfo, vtec_year from data where rank = 1 order by vtec_year asc
                       """),
            conn,
            geom_col="geom",
        )
    print(warningsdf)
    wfos = warningsdf["wfo"].value_counts()
    wfocnts = (
        "WFO Counts: "
        f"OAX Omaha: {wfos['OAX']}, "
        f"DMX Des Moines: {wfos['DMX']}, "
        f"DVN Davenport: {wfos['DVN']}, "
        f"ARX La Crosse: {wfos['ARX']}, "
        f"FSD Sioux Falls: {wfos['FSD']}"
    )
    mp = MapPlot(
        sector="spherical_mercator",
        west=-96.5,
        east=-91.0,
        south=40.5,
        north=43.0,
        title="2000-2025 First Iowa Severe Thunderstorm Warning of the Year",
        subtitle=wfocnts,
    )
    cmap = get_cmap("jet")
    clevs = range(
        warningsdf["vtec_year"].min(), warningsdf["vtec_year"].max() + 2
    )
    norm = BoundaryNorm(clevs, cmap.N)
    warningsdf.to_crs(mp.panels[0].crs).plot(  # type: ignore
        ax=mp.panels[0].ax,
        aspect=None,
        color=cmap(norm(warningsdf["vtec_year"].to_numpy())),
        edgecolor="k",
        lw=0.5,
        zorder=Z_OVERLAY,
    )
    mp.draw_colorbar(clevs, cmap, norm, units="Year", extend="neither")
    mp.drawcounties()
    mp.postprocess(filename="250227.png")


if __name__ == "__main__":
    main()
