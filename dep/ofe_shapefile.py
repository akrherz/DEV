"""Dump our OFEs to a shapefile."""

import geopandas as gpd
from shapely.ops import split
from pyiem.util import get_sqlalchemy_conn


def main():
    """Go main Go."""
    with get_sqlalchemy_conn("idep") as conn:
        flowpaths = gpd.read_postgis(
            "SELECT fid, huc_12, fpath, geom from flowpaths "
            "where scenario = 0",
            conn,
            geom_col="geom",
            index_col="fid",
        )
        points = gpd.read_postgis(
            """
            with data as (
                select geom, flowpath, ofe, lag(ofe) OVER
                (PARTITION by flowpath ORDER by length asc) from
                flowpath_points where scenario = 0)
            select flowpath, ofe, geom from data where ofe > lag
            ORDER by flowpath ASC, ofe ASC
            """,
            conn,
            geom_col="geom",
            index_col=None,
        )
    res = []
    for flowpathid, row in flowpaths.iterrows():
        line = row["geom"]
        huc12 = row["huc_12"]
        fpath = row["fpath"]
        ofe = 1
        for _, row in points[points["flowpath"] == flowpathid].iterrows():
            (ofeline, line) = split(line, row["geom"]).geoms
            res.append([huc12, fpath, ofe, ofeline])
            ofe += 1
        res.append([huc12, fpath, ofe, line])
    gdf = gpd.GeoDataFrame(
        res, columns=["huc12", "flowpath", "ofe", "geom"], geometry="geom"
    )
    gdf.to_file("dep_221004_ofes")


if __name__ == "__main__":
    main()
