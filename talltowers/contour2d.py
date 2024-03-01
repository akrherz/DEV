"""Create 2-D contour and see what it looks like?"""

from datetime import timedelta, timezone

import numpy as np
from backports.zoneinfo import ZoneInfo  # type: ignore

from metpy.units import masked_array, units
from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn, utc


def main():
    """Go Main Go."""
    CDT = ZoneInfo("America/Chicago")
    sts = utc(2020, 8, 10, 16, 22)
    ets = utc(2020, 8, 10, 16, 32)
    df = read_sql(
        "select valid at time zone 'UTC' as valid, "
        "ws_120m_nwht as ws120, ws_80m_s as ws80, "
        "ws_40m_s as ws40, ws_20m_nw as ws20, "
        "ws_10m_nwht as ws10, ws_5m_nw  as ws5 from data_analog_202008 "
        "where tower = 1 and valid > %s and "
        "valid < %s ORDER by valid DESC",
        get_dbconn("talltowers"),
        index_col=None,
        params=(sts, ets),
    )
    df["valid"] = df["valid"].dt.tz_localize(timezone.utc)
    fig, ax = plt.subplots(1, 1)
    x = [(xx - sts).total_seconds() for xx in df["valid"]]
    y = ([5, 10, 20, 40, 80, 120] * units("meter")).to(units("feet")).m
    z = np.zeros((len(y), len(x)))
    for zz, col in enumerate(["ws5", "ws10", "ws20", "ws40", "ws80", "ws120"]):
        z[zz, :] = (
            masked_array(df[col].values, units("meter / second"))
            .to(units("mile / hour"))
            .m
        )
    cmap = plt.get_cmap("jet")
    res = ax.contourf(
        x, y, z, levels=[10, 25, 50, 75, 90, 100, 110, 120, 130], cmap=cmap
    )
    now = sts
    xticks = []
    xticklabels = []
    while now < ets:
        xticks.append((now - sts).total_seconds())
        xticklabels.append(now.astimezone(CDT).strftime("%I:%M"))
        now += timedelta(minutes=1)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels, rotation=45)
    ax.set_title(
        "ISU Iowa Atmospheric Observatory 1 Hz Wind Gusts [MPH]\n"
        "'Story County TallTower' 10 August 2020 Derecho\n"
        "Wind Sensors at 5, 10, 20, 40, 80, and 120m AGL"
    )
    ax.set_ylabel("Height above Ground [ft]")
    ax.set_xlabel("Central Daylight Time")
    ax.grid(True)
    fig.colorbar(res, label="Wind Gust [MPH]", spacing="proportional")
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
