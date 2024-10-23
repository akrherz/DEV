"""Ingest."""

import click
import pandas as pd
from pyiem.database import get_dbconnc
from pyiem.util import logger

LOG = logger()


def is_numeric(val):
    """quack."""
    try:
        float(val)
        return True
    except Exception:
        return False


def update_state_days():
    """Add back in this."""
    df = pd.read_excel(
        "PublicHISTORIC_IADAYS.xlsx", sheet_name="State Days", header=None
    )
    col = 0
    pgconn, cursor = get_dbconnc("coop")
    while col < len(df.columns):
        # Look for Date in row 2
        if df.iloc[2, col] != "Week Ending":
            col += 1
            continue
        print("Found Date in column", col)
        for row in range(3, len(df.index)):
            dt = df.iloc[row, col]
            val = df.iloc[row, col + 1]
            if not is_numeric(val):
                print(dt, val)
                continue
            cursor.execute(
                "update nass_iowa set iowa = %s where valid = %s and "
                "metric = 'days suitable'",
                (val, dt),
            )
            if cursor.rowcount == 0:
                print("No data?")
        col += 1

    cursor.close()
    pgconn.commit()


@click.command()
@click.option("--filename", required=True)
@click.option("--sheetname", required=True)
@click.option("--metric", required=True)
def main(filename, sheetname, metric):
    """Go Main."""
    df = pd.read_excel(filename, sheet_name=sheetname, header=None)

    col = 0
    inserts = 0
    pgconn, cursor = get_dbconnc("coop")
    while col < len(df.columns):
        # Look for Date in row 2
        if df.iloc[2, col] != "DATE":
            col += 1
            continue
        print("Found Date in column", col)
        for row in range(3, len(df.index)):
            dt = df.iloc[row, col]
            if dt is None:
                continue
            vals = list(df.iloc[row, col + 1 : col + 11])
            if not all(is_numeric(v) for v in vals):
                print(dt, vals)
                continue
            cursor.execute(
                "delete from nass_iowa where valid = %s and metric = %s",
                (dt, metric),
            )
            cursor.execute(
                "INSERT into nass_iowa(valid, metric, nw, nc, ne, wc, c, ec, "
                "sw, sc, se, iowa) "
                "VALUES (%s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (dt, metric, *vals),
            )
            inserts += 1
        col += 10

    cursor.close()
    pgconn.commit()
    LOG.info("Inserted %s rows", inserts)


if __name__ == "__main__":
    main()
    # update_state_days()
