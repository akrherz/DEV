"""
Look for wind information that is likely bad and null it out.
"""

from zoneinfo import ZoneInfo

import click
from sqlalchemy import text

import pandas as pd
from pyiem.database import get_dbconnc, get_sqlalchemy_conn
from pyiem.network import Table as NetworkTable
from pyiem.util import logger

LOG = logger()


def process(conn, row, station, nt, threshold: int):
    """Do what we need to do here."""
    delta = pd.Timedelta(hours=3)
    obs = pd.read_sql(
        text("""
    SELECT valid, drct, sknt, gust, peak_wind_gust from alldata where
    station = :station and valid >= :sts and valid <= :ets
    ORDER by valid ASC
        """),
        conn,
        params={
            "station": station,
            "sts": row["valid"] - delta,
            "ets": row["valid"] + delta,
        },
    )
    if len(obs.index) > 10:
        obs = obs[
            (obs["sknt"] >= threshold)
            | (obs["gust"] >= threshold)
            | (obs["peak_wind_gust"] >= threshold)
        ]
    print(row["valid"])
    print(obs.head(100))
    res = input("Null space sep list (#s #g #p): ")
    if res == "":
        return
    tzinfo = ZoneInfo(nt.sts[station]["tzname"])
    iempgconn, iemcursor = get_dbconnc("iem")
    mapper = {
        "s": "sknt",
        "g": "gust",
        "p": "peak_wind_gust",
    }
    for entry in res.split():
        idx = int(entry[:-1])
        cullrow = obs.loc[idx]
        colval = entry[-1]
        col = mapper[colval]
        conn.execute(
            text(
                f"UPDATE t{cullrow['valid'].year} SET {col} = null, "
                "editable = 'f' "
                "WHERE station = :station and valid = :dt"
            ),
            {
                "station": station,
                "dt": cullrow["valid"],
            },
        )
        print(f"Setting {cullrow['valid']} {col}->null")

        iemcursor.execute(
            f"update summary_{cullrow['valid'].year} set max_sknt = null, "
            "max_gust = null where iemid = %s and day = %s",
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
@click.option("--threshold", type=int, default=100)
def main(station, network, threshold):
    """Go Main Go."""
    nt = NetworkTable(network, only_online=False)
    # Look for obs that are maybe bad
    with get_sqlalchemy_conn("asos") as conn:
        obs = pd.read_sql(
            text("""
            select valid, sknt, gust, peak_wind_gust, drct from alldata
            where station = :station and (
                 sknt > :t or gust > :t or peak_wind_gust > :t
            ) ORDER by greatest(sknt, gust, peak_wind_gust) desc
                """),
            conn,
            params={"station": station, "t": threshold},
        )
        LOG.info("Found %s rows", len(obs.index))

        for _, row in obs.iterrows():
            process(conn, row, station, nt, threshold)


if __name__ == "__main__":
    main()
