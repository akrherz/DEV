"""For pre-2000, we were too aggressive."""

import sys
from datetime import timezone

import click
from sqlalchemy import text

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.nws.product import TextProduct, TextProductException
from pyiem.util import logger, utc

LOG = logger()


def process(df):
    """Figure out what to take and what not to take."""
    for idx, row in df.iterrows():
        try:
            prod = TextProduct(row["data"], utcnow=row["utc_valid"])
            df.at[idx, "ugcs"] = ",".join(
                str(x) for x in prod.segments[0].ugcs
            )
            df.at[idx, "ugcexpire"] = prod.segments[0].ugcexpire
            df.at[idx, "noTTAA00"] = row["data"].find("TTAA00") == -1
        except TextProductException:
            LOG.info("Failed to parse ctid: %s", row["ctid"])
            continue
        except Exception as exp:
            LOG.exception(exp)
            continue

    # Screen
    if (
        "ugcs" not in df.columns
        or df["ugcs"].nunique() != 1
        or df["ugcexpire"].nunique() != 1
    ):
        return

    df["take"] = False
    df.loc[df["bbb"] == "COR", "take"] = True
    df.loc[df["bbb"].isna(), "take"] = True
    if df["take"].sum() == 0:
        df.loc[df["noTTAA00"], "take"] = True
    if df["take"].sum() == 0:
        df.loc[df.index[0], "take"] = True
    if df["take"].sum() == 0:
        print("Logic Failure.")
        print(df)
        sys.exit()

    with get_sqlalchemy_conn("afos") as conn:
        for idx, row in df.iterrows():
            if not row["take"]:
                conn.execute(
                    text(f"delete from {row['table']} WHERE ctid = :ctid"),
                    {"ctid": row["ctid"]},
                )
                continue
            if row["bbb"] == "COR":
                continue
            if row["bbb"] is not None:
                newtext = (
                    row["data"][:30].replace(f" {row['bbb']}\n", "\n")
                    + row["data"][30:]
                )
                conn.execute(
                    text(
                        f"UPDATE {row['table']} SET data = :newtext, "
                        "bbb = null WHERE ctid = :ctid"
                    ),
                    {"newtext": newtext, "ctid": row["ctid"]},
                )
        conn.commit()
    print(df)


@click.command()
@click.option("--year", type=int, help="Year to process")
def main(year):
    """Go Main Go."""
    # build a list of problematic products
    with get_sqlalchemy_conn("afos") as conn:
        products = pd.read_sql(
            text("""
            select ctid, entered at time zone 'UTC' as utc_valid,
            tableoid::regclass as table,
            pil, bbb, data from products where entered >= :sts and
            entered < :ets and substr(pil, 1, 3) in ('SVR', 'TOR', 'FFW')
                 ORDER by entered asc
            """),
            conn,
            params={
                "sts": utc(year, 1, 1),
                "ets": utc(year + 1, 1, 1),
            },
        )
        if products.empty:
            LOG.info("No results found!")
            return
        products["utc_valid"] = products["utc_valid"].dt.tz_localize(
            timezone.utc
        )
    LOG.info("Found %s rows to process", len(products.index))
    for _idx, gdf in products.groupby(["utc_valid", "pil"]):
        if len(gdf.index) < 2:
            continue
        process(gdf.copy())


if __name__ == "__main__":
    main()
