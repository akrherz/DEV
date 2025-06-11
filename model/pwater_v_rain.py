"""An old plot."""

import numpy as np
from pyiem.database import get_dbconn
from pyiem.plot import figure


def main():
    """Go Main Go."""
    MOS = get_dbconn("mos")
    mcursor = MOS.cursor()
    COOP = get_dbconn("coop")
    ccursor = COOP.cursor()

    # Get rain obs
    obs = {}
    ccursor.execute(
        "SELECT day, precip from alldata_ia where year > 2003 and "
        "month = 6 and station = 'IATDSM' and precip > 0.001"
    )
    for row in ccursor:
        obs[row[0].strftime("%Y%m%d")] = row[1]

    # Get pwater
    mcursor.execute(
        """
        SELECT runtime, pwater from model_gridpoint where station = 'KDSM'
        and model = 'NAM' and runtime = ftime and
        extract(month from runtime) = 6
        and extract(hour from runtime) = 7 and pwater > 0 and pwater < 400
    """
    )
    total = np.ma.zeros((25,), "f")  # 4 mm to 100
    hits = np.ma.zeros((25,), "f")
    pwater = []
    precip = []
    for row in mcursor:
        binval = int(row[1] / 4)
        ob = obs.get(f"{row[0]:%Y%m%d}", None)
        if ob is not None:
            hits[binval] += 1
        total[binval] += 1
        pwater.append(row[1])
        precip.append(0 if ob is None else ob)

    fig = figure(
        title="Des Moines June Precipitable Water & Rainfall (2004-2025)",
        subtitle="7 AM NAM model analysis and same day daily rainfall",
        figsize=(8, 6),
    )
    ax = [
        fig.add_axes((0.1, 0.55, 0.8, 0.35)),
        fig.add_axes((0.1, 0.1, 0.8, 0.4)),
    ]
    hits.mask = np.where(hits == 0, True, False)
    total.mask = np.where(total == 0, True, False)
    climate = np.ma.sum(hits) / np.ma.sum(total) * 100.0
    percent = hits / total * 100.0
    bars = ax[0].bar(
        np.arange(0, 100, 4) + 2,
        percent,
        align="center",
        width=4.0,
        facecolor="lightblue",
    )
    ax[0].axhline(climate, color="b")
    ax[0].text(5, climate + 3, "Climatology", color="b")
    for i in range(len(bars)):
        if total[i] > 0:
            ax[0].text(
                i * 4 + 2, percent[i] - 7, f"{total[i]:.0f}", ha="center"
            )
    ax[0].text(5, 80, "Bar label is \n# of days")
    ax[0].set_ylabel("Measurable Daily Precip[%]")
    ax[0].set_xticks(np.arange(0, 3 * 25.5, 25.4 / 4.0))
    ax[0].set_xticklabels(np.arange(0, 3.1, 0.25))
    ax[0].grid(True)
    ax[0].set_xlim(0, 60)
    ax[0].set_yticks([0, 5, 25, 50, 75, 95, 100])
    ax[0].set_ylim(0, 101)

    ax[1].scatter(pwater, precip)
    ax[1].set_xticks(np.arange(0, 3 * 25.5, 25.4 / 4.0))
    ax[1].set_xlabel("Preciptable Water [inch]")
    ax[1].set_xticklabels(np.arange(0, 3.1, 0.25))
    ax[1].set_ylim(-0.1, 3.5)
    ax[1].set_ylabel("Daily Precipitation [inch]")
    ax[1].plot([0, 2 * 25.4], [0, 2])
    ax[1].grid(True)
    ax[1].set_xlim(0, 60)

    fig.savefig("250611.png")


if __name__ == "__main__":
    main()
