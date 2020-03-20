"""State Fair Wx"""
from __future__ import print_function

import mx.DateTime
import psycopg2
import numpy
import numpy.ma
import matplotlib.pyplot as plt
import pandas as pd

COOP = psycopg2.connect(database="coop", host="iemdb", user="nobody")
ASOS = psycopg2.connect(
    database="asos", host="localhost", port=5555, user="nobody"
)

FAIRS = [
    [mx.DateTime.DateTime(1880, 9, 6), mx.DateTime.DateTime(1880, 9, 10)],
    [mx.DateTime.DateTime(1881, 9, 5), mx.DateTime.DateTime(1881, 9, 9)],
    [mx.DateTime.DateTime(1882, 9, 1), mx.DateTime.DateTime(1882, 9, 8)],
    [mx.DateTime.DateTime(1883, 8, 31), mx.DateTime.DateTime(1883, 9, 7)],
    [mx.DateTime.DateTime(1884, 8, 29), mx.DateTime.DateTime(1884, 9, 5)],
    [mx.DateTime.DateTime(1885, 9, 4), mx.DateTime.DateTime(1885, 9, 11)],
    [mx.DateTime.DateTime(1886, 9, 3), mx.DateTime.DateTime(1886, 9, 11)],
    [mx.DateTime.DateTime(1887, 9, 2), mx.DateTime.DateTime(1887, 9, 9)],
    [mx.DateTime.DateTime(1888, 8, 31), mx.DateTime.DateTime(1888, 9, 7)],
    [mx.DateTime.DateTime(1889, 8, 30), mx.DateTime.DateTime(1889, 9, 6)],
    [mx.DateTime.DateTime(1890, 8, 29), mx.DateTime.DateTime(1890, 9, 5)],
    [mx.DateTime.DateTime(1891, 8, 28), mx.DateTime.DateTime(1891, 9, 4)],
    [mx.DateTime.DateTime(1892, 8, 26), mx.DateTime.DateTime(1892, 9, 2)],
    [mx.DateTime.DateTime(1893, 9, 1), mx.DateTime.DateTime(1893, 9, 8)],
    [mx.DateTime.DateTime(1894, 8, 31), mx.DateTime.DateTime(1894, 9, 7)],
    [mx.DateTime.DateTime(1895, 9, 6), mx.DateTime.DateTime(1895, 9, 13)],
    [mx.DateTime.DateTime(1896, 9, 4), mx.DateTime.DateTime(1896, 9, 11)],
    [mx.DateTime.DateTime(1897, 9, 11), mx.DateTime.DateTime(1897, 9, 18)],
    [mx.DateTime.DateTime(1899, 8, 25), mx.DateTime.DateTime(1899, 9, 1)],
    [mx.DateTime.DateTime(1900, 8, 24), mx.DateTime.DateTime(1900, 8, 31)],
    [mx.DateTime.DateTime(1901, 8, 23), mx.DateTime.DateTime(1901, 8, 30)],
    [mx.DateTime.DateTime(1902, 8, 22), mx.DateTime.DateTime(1902, 8, 29)],
    [mx.DateTime.DateTime(1903, 8, 21), mx.DateTime.DateTime(1903, 8, 28)],
    [mx.DateTime.DateTime(1904, 8, 19), mx.DateTime.DateTime(1904, 8, 26)],
    [mx.DateTime.DateTime(1905, 8, 25), mx.DateTime.DateTime(1905, 9, 1)],
    [mx.DateTime.DateTime(1906, 8, 24), mx.DateTime.DateTime(1906, 8, 31)],
    [mx.DateTime.DateTime(1907, 8, 23), mx.DateTime.DateTime(1907, 8, 30)],
    [mx.DateTime.DateTime(1908, 8, 20), mx.DateTime.DateTime(1908, 8, 28)],
    [mx.DateTime.DateTime(1909, 8, 27), mx.DateTime.DateTime(1909, 9, 3)],
    [mx.DateTime.DateTime(1910, 8, 25), mx.DateTime.DateTime(1910, 9, 2)],
    [mx.DateTime.DateTime(1911, 8, 24), mx.DateTime.DateTime(1911, 9, 1)],
    [mx.DateTime.DateTime(1912, 8, 22), mx.DateTime.DateTime(1912, 8, 30)],
    [mx.DateTime.DateTime(1913, 8, 20), mx.DateTime.DateTime(1913, 8, 28)],
    [mx.DateTime.DateTime(1914, 8, 26), mx.DateTime.DateTime(1914, 9, 4)],
    [mx.DateTime.DateTime(1915, 8, 25), mx.DateTime.DateTime(1915, 9, 3)],
    [mx.DateTime.DateTime(1916, 8, 23), mx.DateTime.DateTime(1916, 9, 1)],
    [mx.DateTime.DateTime(1917, 8, 22), mx.DateTime.DateTime(1917, 8, 31)],
    [mx.DateTime.DateTime(1918, 8, 21), mx.DateTime.DateTime(1918, 8, 30)],
    [mx.DateTime.DateTime(1919, 8, 20), mx.DateTime.DateTime(1919, 8, 29)],
    [mx.DateTime.DateTime(1920, 8, 25), mx.DateTime.DateTime(1920, 9, 3)],
    [mx.DateTime.DateTime(1921, 8, 24), mx.DateTime.DateTime(1921, 9, 2)],
    [mx.DateTime.DateTime(1922, 8, 23), mx.DateTime.DateTime(1922, 9, 1)],
    [mx.DateTime.DateTime(1923, 8, 22), mx.DateTime.DateTime(1923, 8, 31)],
    [mx.DateTime.DateTime(1924, 8, 20), mx.DateTime.DateTime(1924, 8, 29)],
    [mx.DateTime.DateTime(1925, 8, 26), mx.DateTime.DateTime(1925, 9, 4)],
    [mx.DateTime.DateTime(1926, 8, 25), mx.DateTime.DateTime(1926, 9, 3)],
    [mx.DateTime.DateTime(1927, 8, 24), mx.DateTime.DateTime(1927, 9, 2)],
    [mx.DateTime.DateTime(1928, 8, 22), mx.DateTime.DateTime(1928, 8, 31)],
    [mx.DateTime.DateTime(1929, 8, 21), mx.DateTime.DateTime(1929, 8, 30)],
    [mx.DateTime.DateTime(1930, 8, 20), mx.DateTime.DateTime(1930, 8, 29)],
    [mx.DateTime.DateTime(1931, 8, 26), mx.DateTime.DateTime(1931, 9, 4)],
    [mx.DateTime.DateTime(1932, 8, 24), mx.DateTime.DateTime(1932, 9, 2)],
    [mx.DateTime.DateTime(1933, 8, 23), mx.DateTime.DateTime(1933, 9, 1)],
    [mx.DateTime.DateTime(1934, 8, 22), mx.DateTime.DateTime(1934, 8, 31)],
    [mx.DateTime.DateTime(1935, 8, 21), mx.DateTime.DateTime(1935, 8, 30)],
    [mx.DateTime.DateTime(1936, 8, 26), mx.DateTime.DateTime(1936, 9, 4)],
    [mx.DateTime.DateTime(1937, 8, 25), mx.DateTime.DateTime(1937, 9, 3)],
    [mx.DateTime.DateTime(1938, 8, 24), mx.DateTime.DateTime(1938, 9, 2)],
    [mx.DateTime.DateTime(1939, 8, 23), mx.DateTime.DateTime(1939, 9, 1)],
    [mx.DateTime.DateTime(1940, 8, 21), mx.DateTime.DateTime(1940, 8, 30)],
    [mx.DateTime.DateTime(1941, 8, 20), mx.DateTime.DateTime(1941, 8, 29)],
    [mx.DateTime.DateTime(1946, 8, 21), mx.DateTime.DateTime(1946, 8, 30)],
    [mx.DateTime.DateTime(1947, 8, 22), mx.DateTime.DateTime(1947, 8, 29)],
    [mx.DateTime.DateTime(1948, 8, 25), mx.DateTime.DateTime(1948, 9, 3)],
    [mx.DateTime.DateTime(1949, 8, 24), mx.DateTime.DateTime(1949, 9, 2)],
    [mx.DateTime.DateTime(1950, 8, 25), mx.DateTime.DateTime(1950, 9, 1)],
    [mx.DateTime.DateTime(1951, 8, 25), mx.DateTime.DateTime(1951, 9, 3)],
    [mx.DateTime.DateTime(1952, 8, 23), mx.DateTime.DateTime(1952, 9, 1)],
    [mx.DateTime.DateTime(1953, 8, 29), mx.DateTime.DateTime(1953, 9, 7)],
    [mx.DateTime.DateTime(1954, 8, 28), mx.DateTime.DateTime(1954, 9, 6)],
    [mx.DateTime.DateTime(1955, 8, 27), mx.DateTime.DateTime(1955, 9, 5)],
    [mx.DateTime.DateTime(1956, 8, 24), mx.DateTime.DateTime(1956, 9, 2)],
    [mx.DateTime.DateTime(1957, 8, 23), mx.DateTime.DateTime(1957, 9, 1)],
    [mx.DateTime.DateTime(1958, 8, 22), mx.DateTime.DateTime(1958, 8, 31)],
    [mx.DateTime.DateTime(1959, 8, 28), mx.DateTime.DateTime(1959, 9, 6)],
    [mx.DateTime.DateTime(1960, 8, 26), mx.DateTime.DateTime(1960, 9, 4)],
    [mx.DateTime.DateTime(1961, 8, 25), mx.DateTime.DateTime(1961, 9, 3)],
    [mx.DateTime.DateTime(1962, 8, 17), mx.DateTime.DateTime(1962, 8, 26)],
    [mx.DateTime.DateTime(1963, 8, 16), mx.DateTime.DateTime(1963, 8, 25)],
    [mx.DateTime.DateTime(1964, 8, 21), mx.DateTime.DateTime(1964, 8, 30)],
    [mx.DateTime.DateTime(1965, 8, 20), mx.DateTime.DateTime(1965, 8, 29)],
    [mx.DateTime.DateTime(1966, 8, 19), mx.DateTime.DateTime(1966, 8, 28)],
    [mx.DateTime.DateTime(1967, 8, 18), mx.DateTime.DateTime(1967, 8, 27)],
    [mx.DateTime.DateTime(1968, 8, 16), mx.DateTime.DateTime(1968, 8, 26)],
    [mx.DateTime.DateTime(1969, 8, 15), mx.DateTime.DateTime(1969, 8, 24)],
    [mx.DateTime.DateTime(1970, 8, 21), mx.DateTime.DateTime(1970, 8, 30)],
    [mx.DateTime.DateTime(1971, 8, 20), mx.DateTime.DateTime(1971, 8, 29)],
    [mx.DateTime.DateTime(1972, 8, 18), mx.DateTime.DateTime(1972, 8, 28)],
    [mx.DateTime.DateTime(1973, 8, 17), mx.DateTime.DateTime(1973, 8, 27)],
    [mx.DateTime.DateTime(1974, 8, 16), mx.DateTime.DateTime(1974, 8, 26)],
    [mx.DateTime.DateTime(1975, 8, 15), mx.DateTime.DateTime(1975, 8, 24)],
    [mx.DateTime.DateTime(1976, 8, 18), mx.DateTime.DateTime(1976, 8, 29)],
    [mx.DateTime.DateTime(1977, 8, 18), mx.DateTime.DateTime(1977, 8, 28)],
    [mx.DateTime.DateTime(1978, 8, 17), mx.DateTime.DateTime(1978, 8, 27)],
    [mx.DateTime.DateTime(1979, 8, 16), mx.DateTime.DateTime(1979, 8, 26)],
    [mx.DateTime.DateTime(1980, 8, 14), mx.DateTime.DateTime(1980, 8, 24)],
    [mx.DateTime.DateTime(1981, 8, 13), mx.DateTime.DateTime(1981, 8, 23)],
    [mx.DateTime.DateTime(1982, 8, 12), mx.DateTime.DateTime(1982, 8, 22)],
    [mx.DateTime.DateTime(1983, 8, 10), mx.DateTime.DateTime(1983, 8, 20)],
    [mx.DateTime.DateTime(1984, 8, 15), mx.DateTime.DateTime(1984, 8, 25)],
    [mx.DateTime.DateTime(1985, 8, 15), mx.DateTime.DateTime(1985, 8, 25)],
    [mx.DateTime.DateTime(1986, 8, 14), mx.DateTime.DateTime(1986, 8, 24)],
    [mx.DateTime.DateTime(1987, 8, 20), mx.DateTime.DateTime(1987, 8, 30)],
    [mx.DateTime.DateTime(1988, 8, 18), mx.DateTime.DateTime(1988, 8, 28)],
    [mx.DateTime.DateTime(1989, 8, 17), mx.DateTime.DateTime(1989, 8, 27)],
    [mx.DateTime.DateTime(1990, 8, 15), mx.DateTime.DateTime(1990, 8, 26)],
    [mx.DateTime.DateTime(1991, 8, 14), mx.DateTime.DateTime(1991, 8, 25)],
    [mx.DateTime.DateTime(1992, 8, 20), mx.DateTime.DateTime(1992, 8, 30)],
    [mx.DateTime.DateTime(1993, 8, 19), mx.DateTime.DateTime(1993, 8, 29)],
    [mx.DateTime.DateTime(1994, 8, 11), mx.DateTime.DateTime(1994, 8, 21)],
    [mx.DateTime.DateTime(1995, 8, 10), mx.DateTime.DateTime(1995, 8, 20)],
    [mx.DateTime.DateTime(1996, 8, 8), mx.DateTime.DateTime(1996, 8, 18)],
    [mx.DateTime.DateTime(1997, 8, 7), mx.DateTime.DateTime(1997, 8, 17)],
    [mx.DateTime.DateTime(1998, 8, 13), mx.DateTime.DateTime(1998, 8, 23)],
    [mx.DateTime.DateTime(1999, 8, 12), mx.DateTime.DateTime(1999, 8, 22)],
    [mx.DateTime.DateTime(2000, 8, 10), mx.DateTime.DateTime(2000, 8, 20)],
    [mx.DateTime.DateTime(2001, 8, 9), mx.DateTime.DateTime(2001, 8, 19)],
    [mx.DateTime.DateTime(2002, 8, 8), mx.DateTime.DateTime(2002, 8, 18)],
    [mx.DateTime.DateTime(2003, 8, 7), mx.DateTime.DateTime(2003, 8, 17)],
    [mx.DateTime.DateTime(2004, 8, 12), mx.DateTime.DateTime(2004, 8, 22)],
    [mx.DateTime.DateTime(2005, 8, 11), mx.DateTime.DateTime(2005, 8, 21)],
    [mx.DateTime.DateTime(2006, 8, 10), mx.DateTime.DateTime(2006, 8, 20)],
    [mx.DateTime.DateTime(2007, 8, 9), mx.DateTime.DateTime(2007, 8, 19)],
    [mx.DateTime.DateTime(2008, 8, 7), mx.DateTime.DateTime(2008, 8, 17)],
    [mx.DateTime.DateTime(2009, 8, 13), mx.DateTime.DateTime(2009, 8, 23)],
    [mx.DateTime.DateTime(2010, 8, 12), mx.DateTime.DateTime(2010, 8, 22)],
    [mx.DateTime.DateTime(2011, 8, 11), mx.DateTime.DateTime(2011, 8, 21)],
    [mx.DateTime.DateTime(2012, 8, 9), mx.DateTime.DateTime(2012, 8, 19)],
    [mx.DateTime.DateTime(2013, 8, 8), mx.DateTime.DateTime(2013, 8, 18)],
    [mx.DateTime.DateTime(2014, 8, 7), mx.DateTime.DateTime(2014, 8, 17)],
    [mx.DateTime.DateTime(2015, 8, 13), mx.DateTime.DateTime(2015, 8, 23)],
    [mx.DateTime.DateTime(2016, 8, 11), mx.DateTime.DateTime(2016, 8, 21)],
    [mx.DateTime.DateTime(2017, 8, 10), mx.DateTime.DateTime(2017, 8, 20)],
]


def main():
    """Do Something!"""
    acursor = ASOS.cursor()
    rows = []

    for sts, ets in FAIRS:
        if sts.year < 1951:
            continue
        acursor.execute(
            """
            WITH hourly as (
                SELECT date_trunc('hour', valid) as hr, max(tmpf) from
                t"""
            + str(sts.year)
            + """ WHERE station = 'DSM' and
                valid between '%s 00:00' and '%s 00:00' and
                extract(hour from valid) between 6 and 20
                and dwpf is not null GROUP by hr
            ) SELECT count(*),
            sum(case when max >= 79.5 then 1 else 0 end) from hourly
        """
            % (sts.strftime("%Y-%m-%d"), ets.strftime("%Y-%m-%d"))
        )
        row = acursor.fetchone()
        rows.append(dict(year=sts.year, count=row[0], hits=row[1]))

    df = pd.DataFrame(rows)
    df["percentage"] = df["hits"] / df["count"] * 100.0
    (fig, ax) = plt.subplots(1, 1)
    ax.bar(df["year"], df["percentage"])
    ax.grid(True)
    ax.axhline(df["percentage"].mean(), lw=2, color="r")
    ax.text(
        2019,
        df["percentage"].mean(),
        "Avg:\n%.1f" % (df["percentage"].mean(),),
        va="center",
    )
    ax.set_xlim(1949, 2018)
    ax.set_ylabel("Percentage of Hours")
    ax.set_title(
        (
            "Iowa State Fair Weather (via Des Moines Airport)\n"
            r"% of Hours between 7 AM and 10 PM "
            r"with Temperature >= 80$^\circ$F"
        )
    )
    fig.savefig("test.png")


if __name__ == "__main__":
    main()

"""
(fig, ax) = plt.subplots(2,1, sharex=True)
bars = ax[0].bar(numpy.arange(1880,2016)-0.4, avgH, edgecolor='r', facecolor='r')
for bar in bars:
    if bar.get_height() < avgHH:
        bar.set_facecolor('b')
        bar.set_edgecolor('b')
ax[0].bar(numpy.arange(1942,1946), [110,110,110,110], fc='#EEEEEE', ec='#EEEEEE')
ax[0].set_xlim(1879.5,2015.5)
ax[0].set_ylim(70,100)
ax[0].grid(True)
ax[0].set_title("Iowa State Fair Average Daily Temps (Des Moines wx site)")
ax[0].set_ylabel("High Temperature $^{\circ}\mathrm{F}$")

bars = ax[1].bar(numpy.arange(1880,2016)-0.4, avgL, edgecolor='r', facecolor='r')
for bar in bars:
    if bar.get_height() < avgLL:
        bar.set_facecolor('b')
        bar.set_edgecolor('b')
ax[1].bar(numpy.arange(1942,1946), [110,110,110,110], fc='#EEEEEE', ec='#EEEEEE')
ax[1].set_ylim(50,75)
ax[1].grid(True)
ax[1].set_ylabel("Low Temperature $^{\circ}\mathrm{F}$")

fig.savefig('test.png')
"""
