"""List out some records."""

import os

import pandas as pd
from pyiem.database import get_dbconn
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot


def get_data():
    """do things."""
    nt = NetworkTable("IA_ASOS")
    pgconn = get_dbconn("asos")
    cursor = pgconn.cursor()
    rows = []
    for station in nt.sts:
        cursor.execute(
            """
            SELECT min(feel) as min_feel
                from t2023 where station = %s and
                valid > '2023-03-17'
                and feel is not null
            """,
            (station,),
        )
        min_feel = cursor.fetchone()[0]
        cursor.execute(
            """
            select a.valid from alldata a
            where station = %s and to_char(a.valid, 'mmdd') >= '0317' and
            to_char(a.valid, 'mmdd') < '0701' and a.feel <= %s
            and a.valid < '2023-01-01'
            ORDER by valid DESC LIMIT 1
            """,
            (station, min_feel),
        )
        row1 = cursor.fetchone()
        byear = nt.sts[station]["archive_begin"].year
        rows.append(
            {
                "station": station,
                "date": (
                    f"<{byear}"
                    if row1 is None
                    else row1[0].strftime("%-m/%-d\n%Y")
                ),
                "min_feel": min_feel,
                "lat": nt.sts[station]["lat"],
                "lon": nt.sts[station]["lon"],
                "byear": byear,
            }
        )
        print(rows[-1])
    df = pd.DataFrame(rows)
    df.to_csv("/tmp/today.csv")
    return df


def main():
    """GO Main go."""
    if not os.path.isfile("/tmp/today.csv"):
        df = get_data()
    else:
        df = pd.read_csv("/tmp/today.csv").sort_values("byear", ascending=True)
    mp = MapPlot(
        title=(
            "Most Recent Mar 17-May 31 Date with as cold wind chill as "
            "17-19 Mar 2023"
        ),
        subtitle=(
            "Sites with '<' label indicate no comparables since start of obs"
        ),
        continentalcolor="white",
    )
    color = df["date"].apply(lambda x: "tan" if x.startswith("<") else "b")
    mp.plot_values(
        df["lon"].values,
        df["lat"].values,
        df["date"].values,
        color=color.values,
        labelspacing=1,
    )
    mp.fig.savefig("230320.png")


if __name__ == "__main__":
    main()
