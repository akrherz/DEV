"""
Compute the amount of precipitation that falls during a SVR,TOR warning
"""
import datetime

import matplotlib.pyplot as plt
import pandas as pd
from pyiem.util import get_dbconn, utc
from tqdm import tqdm


def main():
    """GO Main Go."""
    POSTGIS = get_dbconn("postgis")
    pcursor = POSTGIS.cursor()
    ASOS = get_dbconn("asos1min")
    acursor = ASOS.cursor()

    nextyear = datetime.date.today().year + 1
    df = pd.DataFrame(index=list(range(2006, nextyear)))
    for col in ["in", "around", "out"]:
        df[col] = 0.0

    progress = tqdm(range(2006, nextyear))
    for year in progress:
        progress.set_description(str(year))
        warntimes = []
        around = []
        pcursor.execute(
            f"""
        select distinct generate_series(issue, expire, '1 minute'::interval)
        from sbw_{year}
        where wfo = 'DMX' and phenomena in ('SV','TO') and significance = 'W'
        and status = 'NEW'
        and ST_Contains(geom,
        GeomFromEWKT('SRID=4326;POINT(-93.66308 41.53397)'))
        """
        )
        for row in pcursor:
            warntimes.append(row[0])

        pcursor.execute(
            f"""
        select distinct generate_series(issue - '1 hour'::interval,
            expire + '1 hour'::interval, '1 minute'::interval) from sbw_{year}
        where wfo = 'DMX' and phenomena in ('SV','TO') and significance = 'W'
        and status = 'NEW'
        and ST_Contains(geom,
        GeomFromEWKT('SRID=4326;POINT(-93.66308 41.53397)'))
        """
        )
        for row in pcursor:
            around.append(row[0])

        # Get rainfall
        acursor.execute(
            "SELECT valid, precip from alldata_1minute "
            "where station = 'DSM' and valid > %s and valid < %s "
            "and precip > 0",
            (utc(year, 1, 1), utc(year + 1, 1, 1)),
        )
        for row in acursor:
            if row[0] in warntimes:
                df.at[row[0].year, "in"] += row[1]
            elif row[0] in around:
                df.at[row[0].year, "around"] += row[1]
            else:
                df.at[row[0].year, "out"] += row[1]

    df["total"] = df["in"] + df["around"] + df["out"]
    print(df)
    fig, ax = plt.subplots(2, 1, sharex=True)

    ax[0].set_ylabel("Yearly Precip [inch]")
    ax[1].set_ylabel("Percentage [%]")
    ax[1].set_ylim(0, 100)
    ax[0].set_title(
        "Des Moines Yearly Airport Precipitation [2006-2021]\n"
        "Contribution during, around, and outside of TOR,SVR warning"
    )
    x = df.index.astype(int).tolist()
    ax[0].bar(x, df["in"], fc="r")
    ax[0].bar(x, df["around"], bottom=df["in"], fc="b")
    ax[0].bar(
        x,
        df["out"],
        bottom=(df["in"] + df["around"]),
        fc="g",
    )

    df["in_per"] = df["in"] / df["total"] * 100.0
    p = df["in"].sum() / df["total"].sum() * 100.0
    ax[1].bar(x, df["in_per"], fc="r", label=f"During {p:.1f}%")

    df["around_per"] = df["around"] / df["total"] * 100.0
    p = df["around"].sum() / df["total"].sum() * 100.0
    ax[1].bar(
        x,
        df["around_per"],
        bottom=df["in_per"],
        fc="b",
        label=f"+/- 1 hour {p:.1f}%",
    )

    df["out_per"] = df["out"] / df["total"] * 100.0
    p = df["out"].sum() / df["total"].sum() * 100.0
    ax[1].bar(
        x,
        df["out_per"],
        bottom=(df["in_per"] + df["around_per"]),
        fc="g",
        label=f"Outside {p:.1f}%",
    )

    ax[1].legend(ncol=3, loc=(0.03, 1.01))
    ax[1].grid(True)
    ax[0].grid(True)
    ax[1].set_xticks(range(2006, 2022, 3))
    ax[1].set_xlabel("2021 thru 16 Sept, yearly precip may have missing data")

    fig.savefig("210917.png")


if __name__ == "__main__":
    main()
