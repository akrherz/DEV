"""
Manually review temperatures.
"""

from zoneinfo import ZoneInfo

import click
from sqlalchemy import text

import pandas as pd
from pyiem.database import get_dbconnc, get_sqlalchemy_conn
from pyiem.network import Table as NetworkTable
from pyiem.util import logger

LOG = logger()


def process(conn, row, station, nt):
    """Do what we need to do here."""
    delta = pd.Timedelta(hours=3)
    obs = pd.read_sql(
        "SELECT valid, tmpf, dwpf, relh, feel from alldata where "
        "station = %s and valid >= %s and valid <= %s and "
        "report_type in (3, 4) ORDER by valid ASC",
        conn,
        params=(
            station,
            row["valid"] - delta,
            row["valid"] + delta,
        ),
    )
    print(row["valid"])
    print(obs.head(100))
    res = input("Null space sep list (#t #d #r #f): ")
    if res == "":
        return
    tzinfo = ZoneInfo(nt.sts[station]["tzname"])
    iempgconn, iemcursor = get_dbconnc("iem")
    mapper = {
        "t": "tmpf",
        "d": "dwpf",
        "r": "relh",
        "f": "feel",
    }
    for entry in res.split():
        idx = int(entry[:1])
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
def main(station, network, varname, above, below, year):
    """Go Main Go."""
    nt = NetworkTable(network, only_online=False)
    # Look for obs that are maybe bad
    op = ">" if above is not None else "<"
    tbl = f"t{year}" if year is not None else "alldata"
    with get_sqlalchemy_conn("asos") as conn:
        obs = pd.read_sql(
            text(f"""
            select valid, tmpf, dwpf, relh, feel from {tbl}
            where station = :station and {varname} {op} :t
            ORDER by feel desc
                """),
            conn,
            params={
                "station": station,
                "t": above if above is not None else below,
            },
        )
        LOG.info("Found %s rows", len(obs.index))

        for _, row in obs.iterrows():
            process(conn, row, station, nt)


if __name__ == "__main__":
    main()
