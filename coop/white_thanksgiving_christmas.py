"""White Christmas + White Thanksgiving."""
import datetime

from pandas import Timestamp
from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn


def thanksgiving():
    """Thanksgiving please"""
    days = []
    # monday is 0
    offsets = [3, 2, 1, 0, 6, 5, 4]
    for year in range(1893, datetime.date.today().year):
        nov1 = datetime.datetime(year, 11, 1)
        r1 = nov1 + datetime.timedelta(days=offsets[nov1.weekday()])
        day = r1 + datetime.timedelta(days=21)
        days.append(Timestamp(day))
    return days


def christmas():
    """Christmas please"""
    days = []
    for year in range(1893, datetime.date.today().year):
        days.append(Timestamp(year=year, day=25, month=12))
    return days


def main():
    """Go Main Go."""
    pgconn = get_dbconn("coop")
    df = read_sql(
        """
        SELECT day, year, sday, snowd from alldata_ia where station = 'IA2203'
        and year >= 1893 and month > 10 and year < 2019
        ORDER by day ASC
    """,
        pgconn,
        index_col="day",
    )
    t = thanksgiving()
    c = christmas()
    events = t + c
    df2 = df.loc[events].copy()
    df2.loc[df2["sday"] != "1225", "sday"] = "T"
    df3 = df2.pivot(index="year", columns="sday", values="snowd")
    print(df3.head(20))
    df3 = df3.fillna(0)

    fig, ax = plt.subplots(1, 1)
    years = 2019 - 1893
    thit = len(df3[df3["T"] > 0.01].index) / years * 100.0
    chit = len(df3[df3["1225"] > 0.01].index) / years * 100.0
    bhit = (
        len(df3[(df3["1225"] > 0.01) & (df3["T"] > 0.01)].index)
        / years
        * 100.0
    )
    vals = [thit, chit, bhit]
    ax.bar(range(3), vals)
    for x, y in zip(range(3), vals):
        ax.text(x, y + 1, f"{y:.1f}%", ha="center")
    ax.set_xticks(range(3))
    ax.set_xticklabels(
        ["White\nThanksgiving", "White\nChristmas", "Both White\non same year"]
    )
    ax.set_title("1893-2018 Des Moines Snow Cover (> Trace)")
    ax.grid(True)
    ax.set_ylabel("Frequency [%]")
    ax.set_ylim(0, 50)
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
