"""State Fair Wx"""

import os
from datetime import date, timedelta

import numpy as np

import pandas as pd
from pyiem.plot import figure_axes
from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn

FAIRS = [
    [date(1880, 9, 6), date(1880, 9, 10)],
    [date(1881, 9, 5), date(1881, 9, 9)],
    [date(1882, 9, 1), date(1882, 9, 8)],
    [date(1883, 8, 31), date(1883, 9, 7)],
    [date(1884, 8, 29), date(1884, 9, 5)],
    [date(1885, 9, 4), date(1885, 9, 11)],
    [date(1886, 9, 3), date(1886, 9, 11)],
    [date(1887, 9, 2), date(1887, 9, 9)],
    [date(1888, 8, 31), date(1888, 9, 7)],
    [date(1889, 8, 30), date(1889, 9, 6)],
    [date(1890, 8, 29), date(1890, 9, 5)],
    [date(1891, 8, 28), date(1891, 9, 4)],
    [date(1892, 8, 26), date(1892, 9, 2)],
    [date(1893, 9, 1), date(1893, 9, 8)],
    [date(1894, 8, 31), date(1894, 9, 7)],
    [date(1895, 9, 6), date(1895, 9, 13)],
    [date(1896, 9, 4), date(1896, 9, 11)],
    [date(1897, 9, 11), date(1897, 9, 18)],
    [date(1899, 8, 25), date(1899, 9, 1)],
    [date(1900, 8, 24), date(1900, 8, 31)],
    [date(1901, 8, 23), date(1901, 8, 30)],
    [date(1902, 8, 22), date(1902, 8, 29)],
    [date(1903, 8, 21), date(1903, 8, 28)],
    [date(1904, 8, 19), date(1904, 8, 26)],
    [date(1905, 8, 25), date(1905, 9, 1)],
    [date(1906, 8, 24), date(1906, 8, 31)],
    [date(1907, 8, 23), date(1907, 8, 30)],
    [date(1908, 8, 20), date(1908, 8, 28)],
    [date(1909, 8, 27), date(1909, 9, 3)],
    [date(1910, 8, 25), date(1910, 9, 2)],
    [date(1911, 8, 24), date(1911, 9, 1)],
    [date(1912, 8, 22), date(1912, 8, 30)],
    [date(1913, 8, 20), date(1913, 8, 28)],
    [date(1914, 8, 26), date(1914, 9, 4)],
    [date(1915, 8, 25), date(1915, 9, 3)],
    [date(1916, 8, 23), date(1916, 9, 1)],
    [date(1917, 8, 22), date(1917, 8, 31)],
    [date(1918, 8, 21), date(1918, 8, 30)],
    [date(1919, 8, 20), date(1919, 8, 29)],
    [date(1920, 8, 25), date(1920, 9, 3)],
    [date(1921, 8, 24), date(1921, 9, 2)],
    [date(1922, 8, 23), date(1922, 9, 1)],
    [date(1923, 8, 22), date(1923, 8, 31)],
    [date(1924, 8, 20), date(1924, 8, 29)],
    [date(1925, 8, 26), date(1925, 9, 4)],
    [date(1926, 8, 25), date(1926, 9, 3)],
    [date(1927, 8, 24), date(1927, 9, 2)],
    [date(1928, 8, 22), date(1928, 8, 31)],
    [date(1929, 8, 21), date(1929, 8, 30)],
    [date(1930, 8, 20), date(1930, 8, 29)],
    [date(1931, 8, 26), date(1931, 9, 4)],
    [date(1932, 8, 24), date(1932, 9, 2)],
    [date(1933, 8, 23), date(1933, 9, 1)],
    [date(1934, 8, 22), date(1934, 8, 31)],
    [date(1935, 8, 21), date(1935, 8, 30)],
    [date(1936, 8, 26), date(1936, 9, 4)],
    [date(1937, 8, 25), date(1937, 9, 3)],
    [date(1938, 8, 24), date(1938, 9, 2)],
    [date(1939, 8, 23), date(1939, 9, 1)],
    [date(1940, 8, 21), date(1940, 8, 30)],
    [date(1941, 8, 20), date(1941, 8, 29)],
    [date(1946, 8, 21), date(1946, 8, 30)],
    [date(1947, 8, 22), date(1947, 8, 29)],
    [date(1948, 8, 25), date(1948, 9, 3)],
    [date(1949, 8, 24), date(1949, 9, 2)],
    [date(1950, 8, 25), date(1950, 9, 1)],
    [date(1951, 8, 25), date(1951, 9, 3)],
    [date(1952, 8, 23), date(1952, 9, 1)],
    [date(1953, 8, 29), date(1953, 9, 7)],
    [date(1954, 8, 28), date(1954, 9, 6)],
    [date(1955, 8, 27), date(1955, 9, 5)],
    [date(1956, 8, 24), date(1956, 9, 2)],
    [date(1957, 8, 23), date(1957, 9, 1)],
    [date(1958, 8, 22), date(1958, 8, 31)],
    [date(1959, 8, 28), date(1959, 9, 6)],
    [date(1960, 8, 26), date(1960, 9, 4)],
    [date(1961, 8, 25), date(1961, 9, 3)],
    [date(1962, 8, 17), date(1962, 8, 26)],
    [date(1963, 8, 16), date(1963, 8, 25)],
    [date(1964, 8, 21), date(1964, 8, 30)],
    [date(1965, 8, 20), date(1965, 8, 29)],
    [date(1966, 8, 19), date(1966, 8, 28)],
    [date(1967, 8, 18), date(1967, 8, 27)],
    [date(1968, 8, 16), date(1968, 8, 26)],
    [date(1969, 8, 15), date(1969, 8, 24)],
    [date(1970, 8, 21), date(1970, 8, 30)],
    [date(1971, 8, 20), date(1971, 8, 29)],
    [date(1972, 8, 18), date(1972, 8, 28)],
    [date(1973, 8, 17), date(1973, 8, 27)],
    [date(1974, 8, 16), date(1974, 8, 26)],
    [date(1975, 8, 15), date(1975, 8, 24)],
    [date(1976, 8, 18), date(1976, 8, 29)],
    [date(1977, 8, 18), date(1977, 8, 28)],
    [date(1978, 8, 17), date(1978, 8, 27)],
    [date(1979, 8, 16), date(1979, 8, 26)],
    [date(1980, 8, 14), date(1980, 8, 24)],
    [date(1981, 8, 13), date(1981, 8, 23)],
    [date(1982, 8, 12), date(1982, 8, 22)],
    [date(1983, 8, 10), date(1983, 8, 20)],
    [date(1984, 8, 15), date(1984, 8, 25)],
    [date(1985, 8, 15), date(1985, 8, 25)],
    [date(1986, 8, 14), date(1986, 8, 24)],
    [date(1987, 8, 20), date(1987, 8, 30)],
    [date(1988, 8, 18), date(1988, 8, 28)],
    [date(1989, 8, 17), date(1989, 8, 27)],
    [date(1990, 8, 15), date(1990, 8, 26)],
    [date(1991, 8, 14), date(1991, 8, 25)],
    [date(1992, 8, 20), date(1992, 8, 30)],
    [date(1993, 8, 19), date(1993, 8, 29)],
    [date(1994, 8, 11), date(1994, 8, 21)],
    [date(1995, 8, 10), date(1995, 8, 20)],
    [date(1996, 8, 8), date(1996, 8, 18)],
    [date(1997, 8, 7), date(1997, 8, 17)],
    [date(1998, 8, 13), date(1998, 8, 23)],
    [date(1999, 8, 12), date(1999, 8, 22)],
    [date(2000, 8, 10), date(2000, 8, 20)],
    [date(2001, 8, 9), date(2001, 8, 19)],
    [date(2002, 8, 8), date(2002, 8, 18)],
    [date(2003, 8, 7), date(2003, 8, 17)],
    [date(2004, 8, 12), date(2004, 8, 22)],
    [date(2005, 8, 11), date(2005, 8, 21)],
    [date(2006, 8, 10), date(2006, 8, 20)],
    [date(2007, 8, 9), date(2007, 8, 19)],
    [date(2008, 8, 7), date(2008, 8, 17)],
    [date(2009, 8, 13), date(2009, 8, 23)],
    [date(2010, 8, 12), date(2010, 8, 22)],
    [date(2011, 8, 11), date(2011, 8, 21)],
    [date(2012, 8, 9), date(2012, 8, 19)],
    [date(2013, 8, 8), date(2013, 8, 18)],
    [date(2014, 8, 7), date(2014, 8, 17)],
    [date(2015, 8, 13), date(2015, 8, 23)],
    [date(2016, 8, 11), date(2016, 8, 21)],
    [date(2017, 8, 10), date(2017, 8, 20)],
    [date(2018, 8, 9), date(2018, 8, 19)],
    [date(2019, 8, 8), date(2019, 8, 18)],
    # No 2020 Fair, COVID
    [date(2021, 8, 12), date(2021, 8, 22)],
    [date(2022, 8, 11), date(2022, 8, 21)],
]


def hours_above():
    """Plot hours above some threshold."""
    if not os.path.isfile("/tmp/data.csv"):
        years = []
        hours = []
        dbconn = get_dbconn("asos")
        cursor = dbconn.cursor()
        for sts, ets in FAIRS:
            if sts.year < 1973:
                continue
            cursor.execute(
                """
                SELECT distinct
                date_trunc('hour', valid + '10 minutes'::interval)
                from alldata where station = 'DSM' and valid >= %s and
                valid < %s and tmpf >= 79.5
                """,
                (sts, ets + timedelta(hours=24)),
            )
            years.append(sts.year)
            hours.append(cursor.rowcount)
        pd.DataFrame({"years": years, "hours": hours}).to_csv("/tmp/data.csv")
    df = pd.read_csv("/tmp/data.csv")
    (fig, ax) = figure_axes(
        title="Iowa State Fair:: Number of Hourly Observations >= 80$^\circ$F",
        subtitle=(
            "based on hourly Des Moines Airport temperature reports "
            "(1973-2022)"
        ),
        apctx={"_r": "43"},
    )
    ax.bar(df["years"], df["hours"])
    avgv = df["hours"].mean()
    ax.axhline(avgv, lw=2)
    ax.text(2024, avgv, f"Avg:\n{avgv:.1f} hrs", va="center")
    ax.axvspan(1941.5, 1945.5, color="tan")
    ax.axvspan(2019.5, 2020.5, color="tan")
    ax.set_xlim(1972.5, 2022.5)
    ax.set_yticks(np.arange(0, 8 * 24 + 1, 24))
    ax.set_xlabel("No State Fair in 2020")
    ax.set_ylabel("Total Hours")
    ax.grid(True)
    fig.savefig("220822.png")


def main():
    """Do Something!"""
    pgconn = get_dbconn("coop")
    df = pd.read_sql(
        "SELECT day, high, low, precip from alldata where station = 'IATDSM' "
        "ORDER by day ASC",
        pgconn,
        index_col="day",
    )

    years = []
    precip = []
    dry = []
    for sts, ets in FAIRS:
        years.append(sts.year)
        event = df.loc[sts : (ets + timedelta(days=1))]["precip"]
        precip.append(event.sum())
        if precip[-1] < 0.01:
            dry.append(sts.year)

    (fig, ax) = plt.subplots(1, 1)
    ax.bar(years, precip)
    avgval = np.mean(precip)
    ax.axhline(avgval, lw=2, color="r", label=f'Average {avgval:.2f}"')
    ax.grid(True)
    ax.legend()
    ax.set_ylabel("Total Precipitation [inch]")
    ax.set_xlabel(
        f"No Measurable Precip Years {', '.join([str(x) for x in dry])}"
    )
    ax.set_title(
        (
            "Iowa State Fair Weather (via Des Moines Airport / Downtown)\n"
            r"Total Precipitation"
        )
    )
    fig.savefig("test.png")


if __name__ == "__main__":
    hours_above()
