"""
IEM Autoplot 169 encovers lots of data QC issues, so we have some quasi
automation here to help with manual dumping.
"""

from datetime import timezone

import click
import pandas as pd
from pyiem.database import sql_helper, with_sqlalchemy_conn
from sqlalchemy.engine import Connection


@with_sqlalchemy_conn("asos")
def process(row, station, varname: str, conn: Connection | None = None):
    """Do what we need to do here."""
    delta = pd.Timedelta(hours=3)
    obs = pd.read_sql(
        sql_helper(
            """
    SELECT valid, tmpf, dwpf, feel, relh from alldata where
    station = :station and valid >= :sts and valid <= :ets
    and {varname} is not null ORDER by valid ASC""",
            varname=varname,
        ),
        conn,
        params={
            "station": station,
            "sts": row["start_valid_utc"] - delta,
            "ets": row["end_valid_utc"] + delta,
        },
        index_col=None,
    )
    print(obs.head(100))
    res = input("List (space sep) dumped obs or enter for noop: ")
    if res == "":
        return
    for _, cullrow in obs.loc[[int(i) for i in res.split()]].iterrows():
        conn.execute(
            sql_helper(
                """
    UPDATE {table} SET tmpf = null, dwpf = null, feel = null, relh = null,
    editable = 'f' WHERE station = :station and valid = :valid""",
                table=f"t{cullrow['valid'].year}",
            ),
            {"station": station, "valid": cullrow["valid"]},
        )
        print(f"Nulled out {cullrow['valid']} count: {conn.rowcount}")
    conn.commit()


@click.command()
@click.option("--network", required=True)
@click.option("--station", required=True)
@click.option("--hours", type=int, default=24)
@click.option("--mydir", required=True)  # warm or cool
@click.option("--how", required=True)  # exact or over
@click.option("--varname", default="tmpf")
def main(network, station, hours, mydir, how, varname):
    """Go Main Go."""
    url = (
        "https://mesonet.agron.iastate.edu/plotting/auto/plot/169/"
        f"network:{network}::zstation:{station}::hours:{hours}::month:all::"
        f"dir:{mydir}::how:{how}::v:{varname}::_cb:1.csv"
    )
    df = pd.read_csv(url, parse_dates=["start_valid_utc", "end_valid_utc"])
    df["start_valid_utc"] = df["start_valid_utc"].dt.tz_localize(timezone.utc)
    df["end_valid_utc"] = df["end_valid_utc"].dt.tz_localize(timezone.utc)
    for _, row in df.iterrows():
        process(row, station, varname)


if __name__ == "__main__":
    main()
