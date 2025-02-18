"""one off"""

import datetime

import pandas as pd
from pyiem.database import get_dbconn

COMPAREWFOS = "DMX DVN ARX FSD OAX".split()


def printr(row):
    """Print a row's worth of data, please"""
    print(
        ("%s   %s -- %s   %3i   %3i   %3i   %3i")
        % (
            row["wfo"],
            row["date"].strftime("%d %b"),
            (row["date"] + datetime.timedelta(days=2)).strftime("%d %b %Y"),
            row["one"],
            row["two"],
            row["three"],
            row["count"],
        )
    )


def main():
    """Go"""
    pgconn = get_dbconn("postgis")
    df = pd.read_sql(
        """
    with data as (
        select distinct date(issue), wfo, eventid from warnings
        where phenomena = 'TO' and significance = 'W' and issue > '1996-01-01')
    select wfo, date, count(*) from data GROUP by wfo, date
    ORDER by wfo, date
    """,
        pgconn,
        index_col=None,
    )
    rows = []
    for wfo, df2 in df.groupby(by="wfo"):
        maxdate = df2["date"].max()
        mindate = df2["date"].min()
        data = [0] * ((maxdate - mindate).days + 4)
        for _, row in df2.iterrows():
            data[(row["date"] - mindate).days] = row["count"]
        for i in range(0, len(data) - 2):
            if sum(data[i : i + 3]) > 50 or wfo in COMPAREWFOS:
                date = mindate + datetime.timedelta(days=i)
                rows.append(
                    dict(
                        wfo=wfo,
                        date=date,
                        count=sum(data[i : i + 3]),
                        one=data[i],
                        two=data[i + 1],
                        three=data[i + 2],
                    )
                )

    df = pd.DataFrame(rows)
    df.sort_values("count", ascending=False, inplace=True)
    for _, row in df.head(15).iterrows():
        printr(row)
    for wfo in COMPAREWFOS:
        df2 = df[df["wfo"] == wfo]
        printr(df2.iloc[0])


if __name__ == "__main__":
    main()
