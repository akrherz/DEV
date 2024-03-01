"""
Compute the difference between the 12 UTC 850 hPa temp and afternoon high
"""

import datetime
from calendar import month_abbr

from pyiem.datatypes import temperature
from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    ASOS = get_dbconn("asos")
    acursor = ASOS.cursor()

    POSTGIS = get_dbconn("postgis")
    pcursor = POSTGIS.cursor()

    data = [0] * 12
    for i in range(12):
        data[i] = []
    pcursor.execute(
        """
    select valid, tmpc from raob_profile p JOIN raob_flights f on
    (p.fid = f.fid) where f.station in ('KOAX', 'KOVN', 'KOMA')  and
    p.pressure = 850 and extract(hour from valid at time zone 'UTC') = 12
    and tmpc > -40
    ORDER by valid ASC
    """
    )
    for row in pcursor:
        valid = row[0]
        t850 = temperature(row[1], "C")
        acursor.execute(
            f"SELECT max(tmpf) from t{valid.year} "
            "WHERE station = 'OMA' and valid BETWEEN %s and %s",
            (valid, valid + datetime.timedelta(hours=12)),
        )
        row2 = acursor.fetchone()
        if row2[0] is None:
            continue
        high = temperature(row2[0], "F")

        data[valid.month - 1].append(high.value("C") - t850.value("C"))

    (fig, ax) = plt.subplots(1, 1)

    ax.plot([1, 12], [13, 13], "-", lw=1.5, color="green", zorder=1)
    ax.boxplot(data)
    ax.set_title("1960-2013 Omaha Daytime High Temp vs 12 UTC 850 hPa Temp")
    ax.set_ylabel(r"Temperature Difference $^\circ$C")
    ax.set_xticks(range(1, 13))
    ax.set_ylim(-20, 25)
    ax.set_xticklabels(month_abbr[1:])
    ax.grid(axis="y")

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
