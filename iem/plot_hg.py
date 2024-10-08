"""Plot HG."""

import matplotlib.pyplot as plt
import pandas as pd
from pyiem.database import get_dbconn


def get_station(station):
    """Get the data."""
    pgconn = get_dbconn("hads")
    cursor = pgconn.cursor()
    cursor.execute(
        """
        SELECT distinct valid, value from raw2015_07 where
        station = %s and valid > '2015-07-06' and key = 'HGIRGZ'
        ORDER by valid ASC
    """,
        (station,),
    )
    rows = []
    for row in cursor:
        rows.append(dict(valid=row[0], value=row[1]))

    return pd.DataFrame(rows)


def main():
    """Go Main Go."""
    (fig, ax) = plt.subplots(1, 1)

    for station in ["MIWI4", "TMAI4", "TAMI4", "BPLI4", "MROI4"]:
        df = get_station(station)
        ax.plot(df["valid"], df["value"], label=station)

    ax.legend(loc="best")
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
