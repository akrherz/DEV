"""Some old data has rows with repeated text. Split these up."""

from zoneinfo import ZoneInfo

import click
from sqlalchemy import text
from tqdm import tqdm

import pandas as pd
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.nws.product import TextProduct
from pyiem.util import logger, utc

LOG = logger()


@click.command()
@click.option("--year", type=int, help="Year to process")
def main(year):
    """Go Main Go."""
    with get_sqlalchemy_conn("afos") as pgconn:
        df = pd.read_sql(
            text(
                """
            select ctid, pil, data, entered at time zone 'UTC' as utc_entered,
            tableoid::regclass as tablename, source from products WHERE
            entered >= :sts and entered < :ets and
            substr(pil, 1, 3) in ('SVR', 'TOR', 'FFW', 'SVS')
            order by entered asc
        """
            ),
            pgconn,
            params={"sts": utc(year), "ets": utc(year + 1)},
        )
    df["utc_entered"] = df["utc_entered"].dt.tz_localize(ZoneInfo("UTC"))
    LOG.info("Found %s rows to process", len(df.index))

    pgconn = get_dbconn("afos")
    for _, row in tqdm(df.iterrows(), total=len(df.index)):
        try:
            TextProduct(row["data"], utcnow=row["utc_entered"])
            continue
        except Exception as exp:
            if str(exp).find(" 1 UGC ") == -1:
                continue
        lines = row["data"].split("\n")
        ttaaii = lines[1][:6]
        pos = row["data"][200:].find(ttaaii) + 200
        if pos < 200:
            LOG.info("failed to find %s", row["ctid"])
            continue
        data = row["data"]
        entries = []
        while pos > 0:
            entries.append(data[:pos])
            data = data[pos:]
            pos = data[200:].find(ttaaii) + 200
        entries.append(data)
        print([repr(x[:30]) for x in entries])
        continue
        prod1text = row["data"][:pos]
        prod2text = "000 \n" + row["data"][pos:]
        try:
            prod1 = TextProduct(prod1text, utcnow=row["utc_entered"])
            prod2 = TextProduct(prod2text, utcnow=row["utc_entered"])
        except Exception as exp:
            LOG.info(
                "Failed smoke test %s %s %s",
                row["pil"],
                row["utc_entered"],
                exp,
            )
            continue
        print(f"{prod1.get_product_id()}, {prod2.get_product_id()}")
        if prod1.valid.year != row["utc_entered"].year:
            print("Year mismatch")
            return
        if prod2.valid.year != row["utc_entered"].year:
            print("Year mismatch")
            return
        cursor = pgconn.cursor()
        cursor.execute(
            f"delete from {row['tablename']} where ctid = %s",
            (row["ctid"],),
        )
        if cursor.rowcount != 1:
            LOG.info("failed to delete %s", row["ctid"])
            return
        cursor.execute(
            "INSERT into products (data, pil, entered, source, wmo, bbb) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (
                prod1text,
                row["pil"],
                prod1.valid,
                row["source"],
                prod1.wmo,
                prod1.bbb,
            ),
        )
        cursor.execute(
            "INSERT into products (data, pil, entered, source, wmo, bbb) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (
                prod2text,
                row["pil"],
                prod2.valid,
                row["source"],
                prod1.wmo,
                prod1.bbb,
            ),
        )
        cursor.close()
        pgconn.commit()


if __name__ == "__main__":
    main()
