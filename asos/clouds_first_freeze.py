"""feature one-off."""

import datetime

import matplotlib.pyplot as plt
import numpy as np
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    pgconn = get_dbconn("asos")
    cursor = pgconn.cursor()
    lookup = {"CLR": 0, "FEW": 25, "SCT": 50, "BKN": 75, "OVC": 100}

    times = []
    cursor.execute(
        """
    WITH obs as (
        SELECT valid + '10 minutes'::interval as v,
        rank() OVER (PARTITION by extract(year from valid) ORDER by valid ASC)
        from alldata where station = 'AMW' and extract(month from valid) > 6
        and tmpf::int < 29)

    SELECT v from obs where rank = 1 ORDER by v ASC"""
    )
    for row in cursor:
        times.append(row[0].replace(minute=0))

    data = np.ones((len(times), 49)) * -1
    baseyear = times[0].year

    for time in times:
        cursor.execute(
            """
        SELECT valid + '10 minutes'::interval, skyc1, skyc2, skyc3, skyc4
        from alldata
        WHERE station = 'AMW' and valid between %s and %s
        and report_type = 3 ORDER by valid ASC
        """,
            (
                time - datetime.timedelta(hours=25),
                time + datetime.timedelta(hours=25),
            ),
        )
        for row in cursor:
            y = row[0].year - baseyear
            x = int((row[0] - time).total_seconds() / 3600.0) + 24
            if x < 0 or x > 48:
                continue
            clouds = row[1:]
            vals = [lookup.get(cl, np.nan) for cl in clouds]
            data[y, x] = np.nanmax(np.array(vals))

    cmap = plt.get_cmap("gray_r")
    cmap.set_under("tan")
    (fig, ax) = plt.subplots(1, 1)
    res = ax.imshow(
        data,
        interpolation="nearest",
        cmap=cmap,
        aspect="auto",
        extent=(-24.5, 24.5, 2024.5, baseyear - 0.5),
        vmin=0,
    )
    cb = fig.colorbar(res)
    cb.set_ticks([0, 25, 50, 75, 100])
    cb.set_ticklabels(["Clear", "Few", "Scattered", "Broken", "Overcast"])
    ax.set_xlim(-23.5, 23.5)
    ax.grid(True)
    ax.set_ylabel("Year")
    ax.set_yticks(range(2000, 2025, 5))
    ax.set_xlabel(
        (
            r"Hours from first fall sub 29$^\circ$F Temperature, "
            "tan is missing"
        )
    )
    ax.set_title(
        "Ames [AMW] Cloud Coverage Reports\n"
        f"{baseyear}-2024 for  +/- 24 hours around first fall "
        r"sub 29$^\circ$F Temp"
    )
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
