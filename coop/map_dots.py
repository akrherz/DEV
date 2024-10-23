"""A map of dots!"""

import os

import pandas as pd
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot
from pyiem.reference import Z_OVERLAY, state_names
from pyiem.util import get_dbconn, get_sqlalchemy_conn
from tqdm import tqdm


def get_data():
    """Get data."""
    conn = get_dbconn("coop")
    cursor = conn.cursor()
    data = []
    progress = tqdm(state_names)
    for state in progress:
        progress.set_description(state)
        nt = NetworkTable(f"{state}CLIMATE")
        for sid in nt.sts:
            if nt.sts[sid]["archive_begin"] is None:
                continue
            if (
                nt.sts[sid]["archive_begin"].year > 1970
                or nt.sts[sid]["archive_end"] is not None
            ):
                continue
            cursor.execute(
                "SELECT sum(precip) from ncei_climate91 where station = %s",
                (nt.sts[sid]["ncei91"],),
            )
            climo = cursor.fetchone()[0]
            with get_sqlalchemy_conn("coop") as dbconn:
                df = pd.read_sql(
                    "SELECT day, precip from alldata WHERE station = %s "
                    "ORDER by day asc",
                    dbconn,
                    params=(sid,),
                    index_col="day",
                )
            mindays = 1
            days = 100
            while (days - mindays) > 1:
                res = df["precip"].rolling(days).sum() > climo
                if res.sum() > 0:  # hit
                    days -= max([int((days - mindays) / 2), 1])
                    continue
                mindays = days
                days += 15

            data.append(
                {
                    "sid": sid,
                    "days": days,
                    "lat": nt.sts[sid]["lat"],
                    "lon": nt.sts[sid]["lon"],
                }
            )
    pd.DataFrame(data).to_csv("/tmp/data.csv", index=False)


def main():
    """Go Main Go."""
    if not os.path.isfile("/tmp/data.csv"):
        get_data()
    df = pd.read_csv("/tmp/data.csv").sort_values("days", ascending=False)
    # bins = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366]
    bins = [1, 7, 21, 45, 90, 120, 180, 210, 240, 270, 300]
    # cmap = get_cmap("jet")
    # norm = mpcolors.Normalize(1, 366)
    # colors = cmap(norm(df['doy'].values))

    mp = MapPlot(
        title=(
            "Min Consec Day Period Whereby Site Accumulated Yearly Climatology"
        ),
        axisbg="white",
        subtitle=(
            "Based on NWS COOP Sites with 50+ years data, "
            "NCEI 1991-2020 Climatology"
        ),
        sector="conus",
    )
    # clevlabels = calendar.month_abbr[1:] + [""]
    mp.scatter(
        df["lon"].values,
        df["lat"].values,
        df["days"].values,
        bins,
        # cmap=cmap,
        marker="o",
        s=50,
        zorder=Z_OVERLAY,
        extend="max",
        spacing="proportional",
        # clevlabels=clevlabels,
    )

    mp.postprocess(filename="230113.png")


if __name__ == "__main__":
    main()
