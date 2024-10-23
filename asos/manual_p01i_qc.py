"""Find bad precip data and correct things."""

from zoneinfo import ZoneInfo

import click
import pandas as pd
from pyiem.database import get_dbconnc, get_sqlalchemy_conn
from pyiem.network import Table as NetworkTable
from pyiem.util import logger
from sqlalchemy import text

LOG = logger()


def process(row, station, nt, threshold, autozap):
    """Do what we need to do here."""
    delta = pd.Timedelta(hours=3)
    with get_sqlalchemy_conn("asos") as conn:
        obs = pd.read_sql(
            text(
                "SELECT valid, p01i from alldata where "
                "station = :station and valid >= :sts and valid <= :ets "
                "ORDER by valid ASC"
            ),
            conn,
            params={
                "station": station,
                "sts": row["valid"] - delta,
                "ets": row["valid"] + delta,
            },
        )
    print(row["valid"])
    print(obs.head(100))
    if autozap:
        res = ""
        for idx, cullrow in obs.iterrows():
            if pd.notna(cullrow["p01i"]) and cullrow["p01i"] >= threshold:
                res += f"{idx}p "
    else:
        res = input("Null space sep list (#p): ")
        if res == "":
            return
    tzinfo = ZoneInfo(nt.sts[station]["tzname"])
    iempgconn, iemcursor = get_dbconnc("iem")
    conn, cursor = get_dbconnc("asos")
    mapper = {
        "p": "p01i",
    }
    for entry in res.split():
        idx = int(entry[:-1])
        cullrow = obs.loc[idx]
        colval = entry[-1]
        col = mapper[colval]
        cursor.execute(
            f"UPDATE t{cullrow['valid'].year} SET {col} = null, "
            "editable = 'f' "
            "WHERE station = %s and valid = %s",
            (station, cullrow["valid"]),
        )
        print(f"Setting {cullrow['valid']} {col}->null {cursor.rowcount} rows")
        iemcursor.execute(
            f"delete from hourly_{cullrow['valid'].year} "
            "where iemid = %s and valid = %s and phour >= %s",
            (
                nt.sts[station]["iemid"],
                cullrow["valid"].replace(minute=0),
                row["p01i"],
            ),
        )
        print(f"Removed {iemcursor.rowcount} hourly precip rows")

        iemcursor.execute(
            f"update summary_{cullrow['valid'].year} set pday = null "
            "where iemid = %s and day = %s and pday > %s",
            (
                nt.sts[station]["iemid"],
                cullrow["valid"].astimezone(tzinfo).date(),
                row["p01i"],
            ),
        )
    iemcursor.close()
    iempgconn.commit()
    cursor.close()
    conn.commit()


@click.command()
@click.option("--station", required=True)
@click.option("--network", required=True)
@click.option("--threshold", type=float, default=10.0)
@click.option("--autozap", is_flag=True, default=False)
def main(station, network, threshold, autozap):
    """Go Main Go."""
    nt = NetworkTable(network, only_online=False)
    # Look for obs that are maybe bad
    with get_sqlalchemy_conn("asos") as conn:
        obs = pd.read_sql(
            text("""
            select valid, p01i from alldata
            where station = :station and p01i >= :t ORDER by p01i desc
                """),
            conn,
            params={"station": station, "t": threshold},
        )
        LOG.info("Found %s rows", len(obs.index))

    for _, row in obs.iterrows():
        process(row, station, nt, threshold, autozap)


if __name__ == "__main__":
    main()
