"""Eduardo has a spreadsheet of groupids, do we have samples?"""

import click
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from sqlalchemy import text


@click.command()
@click.option("--filename", help="The excel file.")
@click.option("--huc12", type=str, help="The HUC12 to search for.")
def main(filename: str, huc12: str):
    """Go Main Go."""
    rasterdf = pd.read_excel(filename, index_col="unique_id")

    with get_sqlalchemy_conn("idep") as conn:
        ofedf = pd.read_sql(
            text("""
    select groupid, count(*) from flowpath_ofes o JOIN flowpaths f on
    (o.flowpath = f.fid) where huc_12 = :huc12 and scenario = 0
    GROUP by groupid
    """),
            conn,
            index_col="groupid",
            params={"huc12": huc12},
        )
    rasterdf["ofes"] = ofedf["count"]
    rasterdf = rasterdf.sort_values("Count", ascending=False)
    helpdf = rasterdf[(rasterdf["Count"] >= 1000) & rasterdf["ofes"].isna()]
    print(helpdf[["Count", "ofes"]].head(20))


if __name__ == "__main__":
    main()
