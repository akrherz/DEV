"""
IEM Autoplot 169 encovers lots of data QC issues, so we have some quasi
automation here to help with manual dumping.
"""
import sys

import pandas as pd
import pytz
from pyiem.util import get_dbconn, get_sqlalchemy_conn


def process(engine, conn, row, station):
    """Do what we need to do here."""
    delta = pd.Timedelta(hours=1)
    obs = pd.read_sql(
        "SELECT valid, tmpf, dwpf, feel, relh from alldata where "
        "station = %s and valid >= %s and valid <= %s and tmpf is not null "
        "ORDER by valid ASC",
        engine,
        params=(
            station,
            row["start_valid_utc"].replace(tzinfo=pytz.UTC) - delta,
            row["end_valid_utc"].replace(tzinfo=pytz.UTC) + delta,
        ),
        index_col=None,
    )
    print(obs.head(100))
    res = input("List (space sep) dumped obs or enter for noop: ")
    if res == "":
        return
    cursor = conn.cursor()
    for _, cullrow in obs.loc[[int(i) for i in res.split()]].iterrows():
        cursor.execute(
            f"UPDATE t{cullrow['valid'].year} SET tmpf = null, dwpf = null, "
            "feel = null, relh = null, editable = 'f' "
            "WHERE station = %s and valid = %s",
            (station, cullrow["valid"]),
        )
        print(f"Nulled out {cullrow['valid']} count: {cursor.rowcount}")
    cursor.close()
    conn.commit()


def main(argv):
    """Go Main Go."""
    network = argv[1]
    station = argv[2]
    hours = argv[3]
    mydir = argv[4]
    how = argv[5]
    url = (
        "http://iem.local/plotting/auto/plot/169/"
        f"network:{network}::zstation:{station}::hours:{hours}::month:all::"
        f"dir:{mydir}::how:{how}::_cb:1.csv"
    )
    df = pd.read_csv(url, parse_dates=["start_valid_utc", "end_valid_utc"])

    conn = get_dbconn("asos")
    with get_sqlalchemy_conn("asos") as engine:
        for _, row in df.iterrows():
            process(engine, conn, row, station)


if __name__ == "__main__":
    main(sys.argv)
