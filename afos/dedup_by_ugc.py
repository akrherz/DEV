"""We got some entered, pil, bbb combos > 2, which need some help."""

import sys
from datetime import timezone

import click
from sqlalchemy import text

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.nws.product import TextProduct
from pyiem.util import logger, utc

LOG = logger()


def process(row):
    """Figure out what to do."""
    bbbc = " and bbb = :bbb" if row["bbb"] is not None else " and bbb is null"
    with get_sqlalchemy_conn("afos") as conn:
        products = pd.read_sql(
            text(f"""
            select ctid, bbb, data, tableoid::regclass as table from
            products where entered = :entered and
            pil = :pil {bbbc}
            """),
            conn,
            params={
                "entered": row["utc_valid"],
                "pil": row["pil"],
                "bbb": row["bbb"],
            },
        )
    products["ugcs"] = None
    for idx, row2 in products.iterrows():
        try:
            prod = TextProduct(row2["data"], utcnow=row["utc_valid"])
            if prod.segments[0].ugcexpire is None:
                raise ValueError("ugcexpire is None")
        except Exception as exp:
            print(exp, row)
            return
        products.at[idx, "ugcs"] = ",".join(
            str(x) for x in prod.segments[0].ugcs
        ) + prod.segments[0].ugcexpire.strftime("%Y%m%d%H%M")
    unicount = products["ugcs"].nunique()
    for ugcs, gdf in products.groupby("ugcs"):
        newbbb = None
        with get_sqlalchemy_conn("afos") as conn:
            for opt in ["RRA", "RRB", "RRC", "RRD", "RRE", "RRF"]:
                if row["bbb"] is not None and row["bbb"] >= opt:
                    continue
                res = conn.execute(
                    text(
                        "select count(*) from products where "
                        "entered = :entered and pil = :pil and bbb = :bbb"
                    ),
                    {
                        "entered": row["utc_valid"],
                        "pil": row["pil"],
                        "bbb": opt,
                    },
                )
                if res.fetchone()[0] == 0:
                    LOG.info(
                        "Inserting %s %s %s %s %s",
                        row["utc_valid"],
                        row["pil"],
                        opt,
                        ugcs,
                        unicount,
                    )
                    newbbb = opt
                    break
            if newbbb is None:
                LOG.info(
                    "No newbbb found for %s %s %s",
                    row["utc_valid"],
                    row["pil"],
                    ugcs,
                )
                continue
            i = 0
            for idx, row2 in gdf.iterrows():
                lines = row2["data"].split("\n")
                if row["bbb"] is None:
                    lines[1] = lines[1] + f" {newbbb}"
                else:
                    lines[1] = lines[1].replace(row["bbb"], newbbb)
                newtext = "\n".join(lines)
                print(repr(newtext[:50]))
                if i == 0:
                    res = conn.execute(
                        text(
                            f"UPDATE {row2['table']} SET bbb = :bbb, "
                            "data = :data WHERE ctid = :ctid"
                        ),
                        {"bbb": newbbb, "data": newtext, "ctid": row2["ctid"]},
                    )
                else:
                    res = conn.execute(
                        text(
                            f"DELETE from {row2['table']} WHERE ctid = :ctid"
                        ),
                        {"ctid": row2["ctid"]},
                    )
                i += 1
                if res.rowcount != 1:
                    LOG.info("Failed to update %s", row2["ctid"])
                    sys.exit()
            conn.commit()
            return


@click.command()
@click.option("--year", type=int, help="Year to process")
@click.option("--pil", help="PIL (3 char) to process")
def main(year, pil):
    """Go Main Go."""
    # build a list of problematic products
    with get_sqlalchemy_conn("afos") as conn:
        products = pd.read_sql(
            text("""
            select entered at time zone 'UTC' as utc_valid,
            pil, bbb, count(*) from products where entered >= :sts and
            entered < :ets and substr(pil, 1, 3) = :pil
            GROUP by utc_valid, pil, bbb HAVING count(*) > 1
            """),
            conn,
            params={
                "sts": utc(year, 1, 1),
                "ets": utc(year + 1, 1, 1),
                "pil": pil,
            },
        )
        # products = products[products["bbb"] != "COR"]
        if products.empty:
            LOG.info("No results found!")
            return
        products["utc_valid"] = products["utc_valid"].dt.tz_localize(
            timezone.utc
        )
        LOG.info("Found %s rows to process", len(products.index))
        for _, row in products.iterrows():
            process(row)


if __name__ == "__main__":
    main()
