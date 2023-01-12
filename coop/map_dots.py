"""A map of dots!"""
import os
import calendar

from tqdm import tqdm
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot
from pyiem.reference import Z_OVERLAY, state_names
from pyiem.util import get_dbconn
import pandas as pd


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
            cursor.execute(
                """
                with obs as (
                    select year, extract(doy from day) as doy,
                    sum(precip) OVER (PARTITION by year ORDER by day asc)
                    from alldata where station = %s
                ), agg as (
                    select year, min(doy) from obs where
                    sum >= %s group by year
                )
                select year, min from agg ORDER by min asc LIMIT 1
                """,
                (sid, climo),
            )
            if cursor.rowcount == 0:
                continue
            row = cursor.fetchone()
            data.append(
                {
                    "sid": sid,
                    "year": row[0],
                    "doy": float(row[1]),
                    "lat": nt.sts[sid]["lat"],
                    "lon": nt.sts[sid]["lon"],
                }
            )
    pd.DataFrame(data).to_csv("/tmp/data.csv", index=False)


def main():
    """Go Main Go."""
    if not os.path.isfile("/tmp/data.csv"):
        get_data()
    df = pd.read_csv("/tmp/data.csv").sort_values("doy", ascending=False)
    bins = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366]
    # cmap = get_cmap("Paired")
    # norm = mpcolors.Normalize(1, 366)
    # colors = cmap(norm(df['doy'].values))

    mp = MapPlot(
        title=(
            "Min Year-To-Date Period for Site to Exceed "
            "Yearly Precip Climatology"
        ),
        axisbg="white",
        subtitle=(
            "Based on NWS COOP Sites with 50+ years data, "
            "NCEI 1991-2020 Climatology"
        ),
        sector="conus",
    )
    clevlabels = calendar.month_abbr[1:] + [""]
    mp.scatter(
        df["lon"].values,
        df["lat"].values,
        df["doy"].values,
        bins,
        marker="o",
        s=50,
        zorder=Z_OVERLAY,
        extend="neither",
        clevlabels=clevlabels,
    )

    mp.postprocess(filename="230112.png")


if __name__ == "__main__":
    main()
