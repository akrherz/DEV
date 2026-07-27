"""List out some RAGBRAI stats."""

from datetime import datetime

import pandas as pd
from metpy.calc import wind_components
from metpy.units import units
from pyiem.database import get_dbconn
from pyiem.plot import figure

DATES = [
    [datetime(1973, 8, 26), datetime(1973, 8, 31)],
    [datetime(1974, 8, 4), datetime(1974, 8, 10)],
    [datetime(1975, 8, 3), datetime(1975, 8, 9)],
    [datetime(1976, 8, 1), datetime(1976, 8, 7)],
    [datetime(1977, 7, 31), datetime(1977, 8, 6)],
    [datetime(1978, 7, 30), datetime(1978, 8, 5)],
    [datetime(1979, 7, 29), datetime(1979, 8, 4)],
    [datetime(1980, 7, 27), datetime(1980, 8, 2)],
    [datetime(1981, 7, 26), datetime(1981, 8, 1)],
    [datetime(1982, 7, 25), datetime(1982, 7, 31)],
    [datetime(1983, 7, 24), datetime(1983, 7, 30)],
    [datetime(1984, 7, 22), datetime(1984, 7, 28)],
    [datetime(1985, 7, 21), datetime(1985, 7, 27)],
    [datetime(1986, 7, 20), datetime(1986, 7, 26)],
    [datetime(1987, 7, 19), datetime(1987, 7, 25)],
    [datetime(1988, 7, 24), datetime(1988, 7, 30)],
    [datetime(1989, 7, 22), datetime(1989, 7, 28)],
    [datetime(1990, 7, 22), datetime(1990, 7, 28)],
    [datetime(1991, 7, 21), datetime(1991, 7, 27)],
    [datetime(1992, 7, 19), datetime(1992, 7, 25)],
    [datetime(1993, 7, 25), datetime(1993, 7, 31)],
    [datetime(1994, 7, 24), datetime(1994, 7, 30)],
    [datetime(1995, 7, 23), datetime(1995, 7, 29)],
    [datetime(1996, 7, 21), datetime(1996, 7, 27)],
    [datetime(1997, 7, 20), datetime(1997, 7, 26)],
    [datetime(1998, 7, 19), datetime(1998, 7, 25)],
    [datetime(1999, 7, 25), datetime(1999, 7, 31)],
    [datetime(2000, 7, 23), datetime(2000, 7, 29)],
    [datetime(2001, 7, 22), datetime(2001, 7, 28)],
    [datetime(2002, 7, 21), datetime(2002, 7, 27)],
    [datetime(2003, 7, 20), datetime(2003, 7, 26)],
    [datetime(2004, 7, 25), datetime(2004, 7, 31)],
    [datetime(2005, 7, 24), datetime(2005, 7, 30)],
    [datetime(2006, 7, 23), datetime(2006, 7, 29)],
    [datetime(2007, 7, 22), datetime(2007, 7, 28)],
    [datetime(2008, 7, 20), datetime(2008, 7, 26)],
    [datetime(2009, 7, 19), datetime(2009, 7, 25)],
    [datetime(2010, 7, 25), datetime(2010, 7, 31)],
    [datetime(2011, 7, 24), datetime(2011, 7, 30)],
    [datetime(2012, 7, 22), datetime(2012, 7, 28)],
    [datetime(2013, 7, 21), datetime(2013, 7, 27)],
    [datetime(2014, 7, 20), datetime(2014, 7, 26)],
    [datetime(2015, 7, 19), datetime(2015, 7, 25)],
    [datetime(2016, 7, 24), datetime(2016, 7, 30)],
    [datetime(2017, 7, 23), datetime(2017, 7, 29)],
    [datetime(2018, 7, 22), datetime(2018, 7, 28)],
    [datetime(2019, 7, 21), datetime(2019, 7, 27)],
    # COVID
    [datetime(2021, 7, 25), datetime(2021, 7, 31)],
    [datetime(2022, 7, 24), datetime(2022, 7, 30)],
    [datetime(2023, 7, 23), datetime(2023, 7, 29)],
    [datetime(2024, 7, 21), datetime(2024, 7, 27)],
    [datetime(2025, 7, 20), datetime(2025, 7, 26)],
    [datetime(2026, 7, 19), datetime(2026, 7, 25)],
]


def main():
    """Go Main Go."""
    pgconn = get_dbconn("asos")
    acursor = pgconn.cursor()

    last_year = DATES[-1][0].year

    results: list[dict] = []

    for sts, ets in DATES:
        acursor.execute(
            """
        SELECT tmpf, dwpf, sknt, drct, valid, feel from alldata
        WHERE station = 'DSM'
        and valid >= %s and valid <= %s and tmpf is not null
        and dwpf is not null
        and sknt >= 0 and drct >= 0 and report_type = 3
        ORDER by valid ASC
        """,
            (sts, ets.replace(hour=23, minute=59)),
        )
        cnt = 0
        tot = 0
        ttot = 0
        utot = 0
        ucnt = 0
        vtot = 0
        threshold_hours = 0
        for row in acursor:
            ttot += row[0]
            h = row[5]
            if h > 85:
                threshold_hours += 1
            if row[4].hour > 5 and row[4].hour < 22:
                u, v = wind_components(
                    units("kt") * row[2],
                    units("degree") * row[3],
                )
                utot += u.m
                vtot += v.m
                ucnt += 1
            tot += h
            cnt += 1
        results.append(
            {
                "year": sts.year,
                "uwnd": utot / float(ucnt) * 1.15,
                "hindex": tot / float(cnt),
                "threshold_hours": threshold_hours,
            }
        )

    obsdf = pd.DataFrame(results).set_index("year")

    fig = figure(
        title=f"1973-{last_year} RAGBRAI Weather",
        subtitle=(
            "* Using Des Moines Airport data as proxy for entire route "
            "conditions."
        ),
        figsize=(10.24, 7.68),
    )
    ax = fig.add_subplot(211)
    avgval = obsdf["threshold_hours"].mean()
    above = obsdf["threshold_hours"] > avgval
    ax.bar(
        obsdf[above].index.to_numpy(),
        obsdf[above]["threshold_hours"].to_numpy(),
        fc="r",
    )
    ax.bar(
        obsdf[~above].index.to_numpy(),
        obsdf[~above]["threshold_hours"].to_numpy(),
        fc="b",
    )
    ax.axhline(
        avgval,
        color="k",
        lw=2,
        zorder=10,
        label=f"Avg {avgval:.1f} Hours",
    )
    ax.set_ylim(ymin=0)
    ax.set_ylabel("Hours with Heat Index >= 85°F")
    ax.grid(True)
    ax.set_xlim(1972.5, last_year + 0.5)
    ax.legend()

    # Shade 2020 as no-data
    ax.axvspan(2019.5, 2020.5, fc="tan", ec="tan", alpha=0.5)

    ax2 = fig.add_subplot(212)
    tail = obsdf["uwnd"] > 0
    ax2.bar(
        obsdf[tail].index.to_numpy(),
        obsdf[tail]["uwnd"].to_numpy(),
        fc="g",
    )
    ax2.bar(
        obsdf[~tail].index.to_numpy(),
        obsdf[~tail]["uwnd"].to_numpy(),
        fc="r",
    )
    ax2.set_ylabel("6 AM - 9 PM\nEast/West Daytime\n Average Wind Speed [mph]")
    ax2.text(1990, 5, "Tail-winds")
    ax2.text(1990, -5, "Head-winds")
    ax2.set_xlim(1972.5, last_year + 0.5)
    ax2.set_ylim(-6, 6)

    ax2.grid(True)

    # Shade 2020 as no-data
    ax2.axvspan(2019.5, 2020.5, fc="tan", ec="tan", alpha=0.5)
    ax2.set_xlabel("Year, 2020 cancelled due to COVID-19")

    fig.savefig("260728.png")


if __name__ == "__main__":
    main()
