"""Produce a heatmap of OFE groupids."""

import click
import geopandas as gpd
from matplotlib.colors import BoundaryNorm
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import MapPlot, get_cmap
from pyiem.reference import Z_OVERLAY2_LABEL
from sqlalchemy import text


@click.command()
@click.option("--groupid", type=str, required=True)
@click.option("--radius", type=float, default=25.0)
def main(groupid: str, radius: float):
    """Go Main Go."""

    with get_sqlalchemy_conn("idep") as conn:
        ofedf = gpd.read_postgis(
            text("""
    select groupid, st_pointn(o.geom, 1) as pt
    from flowpath_ofes o JOIN flowpaths f on
    (o.flowpath = f.fid) where scenario = 0 and groupid = :groupid
    and ofe = 1
    """),
            conn,
            params={"groupid": groupid},
            geom_col="pt",
            crs="EPSG:5070",
        )
    print(ofedf.shape[0])
    minx, miny, maxx, maxy = ofedf.to_crs(4326).total_bounds
    buffer = 0.1
    mp = MapPlot(
        title=f"Number of OFE=1 within {radius:.0f}km for GroupID: {groupid}",
        subtitle="'X' denotes < 10 OFEs",
        caption="Daily Erosion Project",
        logo="dep",
        sector="custom",
        west=minx - buffer,
        north=maxy + buffer,
        south=miny - buffer,
        east=maxx + buffer,
    )
    minx, miny, maxx, maxy = ofedf.total_bounds
    meters = radius * 1_000
    ofedf["col"] = ((ofedf.geometry.x - minx) / meters).astype(int)
    ofedf["row"] = ((ofedf.geometry.y - miny) / meters).astype(int)
    bins = [1, 5, 10, 25, 50, 100]
    cmap = get_cmap("viridis")
    norm = BoundaryNorm(bins, cmap.N)
    grouped = ofedf.groupby(["row", "col"]).size().reset_index()
    grouped["x"] = minx + grouped["col"] * meters
    grouped["y"] = miny + grouped["row"] * meters
    grouped = gpd.GeoDataFrame(
        grouped,
        geometry=gpd.points_from_xy(grouped["x"], grouped["y"], crs=5070),
    )
    filtered: gpd.GeoDataFrame = grouped[grouped[0] < 10]
    filtered.to_crs(mp.panels[0].crs).plot(
        ax=mp.panels[0].ax,
        aspect=None,
        markersize=15,
        color=cmap(norm(filtered[0])),
        zorder=Z_OVERLAY2_LABEL,
        marker="x",
    )
    filtered: gpd.GeoDataFrame = grouped[grouped[0] >= 10]
    filtered.to_crs(mp.panels[0].crs).plot(
        ax=mp.panels[0].ax,
        aspect=None,
        markersize=15,
        color=cmap(norm(filtered[0])),
        zorder=Z_OVERLAY2_LABEL,
    )
    mp.draw_colorbar(
        bins, cmap, norm, units="Count", extend="max", spacing="proportional"
    )

    fn = groupid.replace(" ", "_").replace("/", "_")
    mp.postprocess(filename=f"/tmp/{fn}.png")


if __name__ == "__main__":
    main()
