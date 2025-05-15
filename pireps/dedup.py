"""Deduplicate PIREPs."""

import click
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.util import logger
from sqlalchemy.engine import Connection
from tqdm import tqdm

LOG = logger()


def do(progress, conn: Connection, dt):
    """do a date."""
    table = f"pireps_{dt.year}"
    # bias toward the longest reports first, which are more likely well formed
    pireps = pd.read_sql(
        sql_helper(
            """
        select ctid, report, valid, product_id from {table} WHERE
        valid >= :sts and valid < :ets
        ORDER by valid ASC, length(report) DESC
        """,
            table=table,
        ),
        conn,
        params={
            "sts": dt.replace(hour=0, minute=0, second=0),
            "ets": dt.replace(hour=23, minute=59, second=59),
        },
    )
    nodups = 0
    deleted = 0
    entries = len(pireps.index)
    for _, df in pireps.groupby(["valid", "report"]):
        if len(df.index) == 1:
            nodups += 1
            continue
        # Find the row to keep, either the first one with a valid product_id
        keepdf = df.loc[df["product_id"].notnull()]
        if keepdf.empty:
            keepidx = df.index[0]
        else:
            keepidx = keepdf.index[0]
        delete_ctids = df.loc[df.index != keepidx]["ctid"].tolist()
        conn.execute(
            sql_helper(
                "DELETE FROM {table} WHERE ctid = ANY(:ctids)",
                table=table,
            ),
            {"ctids": delete_ctids},
        )
        deleted += len(delete_ctids)

    progress.write(
        f"{dt:%Y-%m-%d} {entries} entries, {nodups} nodups, {deleted} deleted"
    )


@click.command()
@click.option("--year", type=int, required=True, help="Year to process")
def main(year: int):
    """GO Main Go."""
    progress = tqdm(pd.date_range(f"{year}/01/01", f"{year}/12/31"))
    with get_sqlalchemy_conn("postgis") as conn:
        for date in progress:
            progress.set_description(f"Processing {date:%Y-%m-%d}")
            do(progress, conn, date)
            conn.commit()


if __name__ == "__main__":
    main()
