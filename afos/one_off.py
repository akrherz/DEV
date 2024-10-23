"""Some old data has rows with repeated text. Split these up."""

from zoneinfo import ZoneInfo

import click
import pandas as pd
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.nws.product import TextProduct
from pyiem.util import logger, utc
from sqlalchemy import text

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
            and strpos(data, 'KWBCe') > 0
            order by entered asc
        """
            ),
            pgconn,
            params={"sts": utc(year), "ets": utc(year + 1)},
        )
    df["utc_entered"] = df["utc_entered"].dt.tz_localize(ZoneInfo("UTC"))
    LOG.info("Found %s rows to process", len(df.index))

    pgconn = get_dbconn("afos")
    for _, row in df.iterrows():
        data = row["data"]
        entries = data.split("\x0c")
        for i, entry in enumerate(entries):
            pos = entry.find("KDEN")
            if pos > -1:
                if len(entry) < 30 or entry[pos + 4] != "W":
                    entries[i] = None
                else:
                    entries[i] = "000 \n" + entry[pos + 4 :]
                    print(repr(entries[i][:30]))
        cursor = pgconn.cursor()
        cursor.execute(
            f"delete from {row['tablename']} where ctid = %s",
            (row["ctid"],),
        )
        if cursor.rowcount != 1:
            LOG.info("failed to delete %s", row["ctid"])
            return
        for entry in entries:
            if entry is None or len(entry) < 30:
                continue
            try:
                prod = TextProduct(entry, utcnow=row["utc_entered"])
                if prod.afos is None:
                    print("AFOS is None")
                    return
                if prod.valid.year != row["utc_entered"].year:
                    print("Year mismatch")
                    return
            except Exception as exp:
                LOG.info(
                    "Failed smoke test %s %s %s",
                    row["pil"],
                    row["utc_entered"],
                    exp,
                )
                continue
            cursor.execute(
                "INSERT into products (data, pil, entered, source, wmo, bbb) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (
                    entry,
                    prod.afos,
                    prod.valid,
                    row["source"],
                    prod.wmo,
                    prod.bbb,
                ),
            )
        cursor.close()
        pgconn.commit()


if __name__ == "__main__":
    main()
