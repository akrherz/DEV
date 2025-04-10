"""
Manually review temperatures.
"""

from typing import Optional
from zoneinfo import ZoneInfo

import click
import pandas as pd
from pyiem.database import get_dbconnc, get_sqlalchemy_conn, sql_helper
from pyiem.network import Table as NetworkTable
from pyiem.util import logger

LOG = logger()


def process(conn, row, station, nt):
    """Do what we need to do here."""
    delta = pd.Timedelta(hours=3)
    obs = pd.read_sql(
        sql_helper("""
    SELECT valid, tmpf, dwpf, relh, feel from alldata where
    station = :station and valid >= :sts and valid <= :ets and
    report_type in (3, 4) ORDER by valid ASC
        """),
        conn,
        params={
            "station": station,
            "sts": row["valid"] - delta,
            "ets": row["valid"] + delta,
        },
    )
    print(row["valid"])
    print(obs.head(100))
    res = input("Rows to null (#t #d): ")
    if res == "":
        return
    tzinfo = ZoneInfo(nt.sts[station]["tzname"])
    iempgconn, iemcursor = get_dbconnc("iem")
    for entry in res.split():
        idx = int(entry[:-1])
        cullrow = obs.loc[idx]
        colval = entry[-1]
        tonull = ""
        if colval == "t":
            tonull = "tmpf = null, dwpf = null, relh = null, feel = null"
        elif colval == "d":
            tonull = "tmpf = null, dwpf = null, relh = null, feel = null"
        table = f"t{cullrow['valid'].year}"
        conn.execute(
            sql_helper(
                "UPDATE {table} SET {tonull}, "
                "editable = 'f' "
                "WHERE station = :station and valid = :dt",
                tonull=tonull,
                table=table,
            ),
            {
                "station": station,
                "dt": cullrow["valid"],
            },
        )
        print(f"Setting {cullrow['valid']} {tonull}")

        iemcursor.execute(
            f"update summary_{cullrow['valid'].year} set max_feel = null, "
            "max_tmpf = null, min_tmpf = null, min_feel = null, "
            "avg_feel = null, max_rh = null, avg_rh = null, min_rh = null "
            "where iemid = %s and day = %s",
            (
                nt.sts[station]["iemid"],
                cullrow["valid"].astimezone(tzinfo).date(),
            ),
        )
    iemcursor.close()
    iempgconn.commit()
    conn.commit()


@click.command()
@click.option("--station", required=True)
@click.option("--network", required=True)
@click.option("--varname", default="feel")
@click.option("--above", type=int, default=None)
@click.option("--below", type=int, default=None)
@click.option("--year", type=int, default=None)
@click.option("--month", type=int, help="Month to filter on")
def main(station, network, varname, above, below, year, month: Optional[int]):
    """Go Main Go."""
    nt = NetworkTable(network, only_online=False)
    # Look for obs that are maybe bad
    op = ">" if above is not None else "<"
    tbl = f"t{year}" if year is not None else "alldata"
    mfilter = ""
    if month is not None:
        mfilter = " and extract(month from valid) = :month "
    with get_sqlalchemy_conn("asos") as conn:
        obs = pd.read_sql(
            sql_helper(
                """
            select valid, tmpf, dwpf, relh, feel from {tbl}
            where station = :station and {varname} {op} :t {mfilter}
            ORDER by {varname} asc
                """,
                tbl=tbl,
                op=op,
                varname=varname,
                mfilter=mfilter,
            ),
            conn,
            params={
                "station": station,
                "t": above if above is not None else below,
                "month": month,
            },
        )
        LOG.info("Found %s rows", len(obs.index))

        for _, row in obs.iterrows():
            process(conn, row, station, nt)


if __name__ == "__main__":
    main()
