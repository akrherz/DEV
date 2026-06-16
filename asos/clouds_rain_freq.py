"""Investigate something interesting..."""

from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import patheffects
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.plot import figure_axes
from sqlalchemy.engine import Connection

clouds = ["OVC", "BKN", "SCT", "FEW", "CLR"]
names = {
    "OVC": "Overcast",
    "BKN": "Broken",
    "SCT": "Scattered",
    "FEW": "Few",
    "CLR": "Clear",
}


@with_sqlalchemy_conn("asos")
def get_data(conn: Connection | None = None):
    """Get data."""

    sql = """
    with oneam as (
        select date(valid), skyc1, skyc2, skyc3, skyc4 from alldata where
        station = 'OTM' and
        extract(hour from valid + '10 minutes'::interval) = 1
        and report_type = 3 and valid > '2000-01-01'
    ), sevenam as (
        select date(valid), skyc1, skyc2, skyc3, skyc4 from alldata where
        station = 'OTM' and
        extract(hour from valid + '10 minutes'::interval) = 7
        and report_type = 3 and valid > '2000-01-01'
    ), precip as (
        select date(valid), sum(p01i) from alldata where station = 'OTM'
        and report_type = 3 and extract(hour from valid + '10 minutes') <= 7
        and valid > '2000-01-01' group by date
    )

    select o.date,
    coalesce(o.skyc1, '') as o_skyc1, coalesce(o.skyc2, '') as o_skyc2,
    coalesce(o.skyc3, '') as o_skyc3, coalesce(o.skyc4, '') as o_skyc4,
    coalesce(s.skyc1, '') as s_skyc1, coalesce(s.skyc2, '') as s_skyc2,
    coalesce(s.skyc3, '') as s_skyc3, coalesce(s.skyc4, '') as s_skyc4, p.sum
    from oneam o JOIN sevenam s on (o.date = s.date)
      JOIN precip p on (o.date = p.date)
    ORDER by o.date asc
    """
    res = conn.execute(sql_helper(sql))

    results = []
    for row in res.mappings():
        o_sky = None
        s_sky = None
        for testcond in clouds:
            if testcond in [
                row["o_skyc1"],
                row["o_skyc2"],
                row["o_skyc3"],
                row["o_skyc4"],
            ]:
                o_sky = testcond
                break
        for testcond in clouds:
            if testcond in [
                row["s_skyc1"],
                row["s_skyc2"],
                row["s_skyc3"],
                row["s_skyc4"],
            ]:
                s_sky = testcond
                break
        if o_sky is not None and s_sky is not None:
            results.append(
                {
                    "date": row["date"],
                    "o_sky": o_sky,
                    "s_sky": s_sky,
                    "precip": row["sum"],
                    "measurable": (
                        # Avoid false tips and flaky things
                        row["sum"] is not None and row["sum"] > 0.045
                    ),
                }
            )
    pd.DataFrame(results).set_index("date").to_csv("/tmp/tmp.csv")


def main():
    """Go Main."""
    csvfn = Path("/tmp/tmp.csv")
    if not csvfn.exists():
        get_data()
    df = pd.read_csv(csvfn, index_col="date", parse_dates=True)
    groups = (
        df.groupby(["o_sky", "s_sky", "measurable"])
        .count()
        .reset_index()
        .pivot(index=["o_sky", "s_sky"], columns="measurable", values="precip")
        .reset_index()
        .copy()
        .assign(freq=lambda x: x[True] / (x[True] + x[False]))
    )
    print(groups)
    overall = (
        groups[True].sum() / (groups[True].sum() + groups[False].sum()) * 100.0
    )
    (fig, ax) = figure_axes(
        title=(
            "2000-2026 Ottumwa Frequency of >= 0.05in Precipitation by "
            "1 AM/7 AM Cloud Coverage Combo"
        ),
        subtitle=(
            f"Overall frequency: {overall:.1f}% "
            f"(1 AM/7 AM pairs: {groups[True].sum() + groups[False].sum():,})"
        ),
        figsize=(8, 6),
    )
    # Give labels more space
    ax.set_position((0.2, 0.15, 0.75, 0.7))

    values = np.zeros((5, 5))
    for _, row in groups.iterrows():
        oidx = clouds.index(row["o_sky"])
        sidx = clouds.index(row["s_sky"])
        values[oidx, sidx] = row["freq"] * 100.0
    _im = ax.imshow(values, vmin=0, vmax=100, aspect="auto")

    # Annotate the values
    for i in range(len(clouds)):
        for j in range(len(clouds)):
            filtered = groups[
                (groups["o_sky"] == clouds[i]) & (groups["s_sky"] == clouds[j])
            ]
            events = filtered.iloc[0][True]
            total = events + filtered.iloc[0][False]
            _text = ax.text(
                j,
                i,
                f"{values[i, j]:.1f}%\n{events:.0f}/{total:.0f}",
                ha="center",
                va="center",
                color="w",
            ).set_path_effects(
                [
                    patheffects.Stroke(linewidth=3, foreground="black"),
                    patheffects.Normal(),
                ]
            )

    xlabels = []
    ylabels = []
    for abbr in clouds:
        events = groups[groups["s_sky"] == abbr][True].sum()
        total = events + groups[groups["s_sky"] == abbr][False].sum()
        freq = events / total * 100.0 if total > 0 else 0.0
        xlabels.append(
            f"{names[abbr]}\n{events:.0f}/{total:.0f} ({freq:.1f}%)"
        )
        events = groups[groups["o_sky"] == abbr][True].sum()
        total = events + groups[groups["o_sky"] == abbr][False].sum()
        freq = events / total * 100.0 if total > 0 else 0.0
        ylabels.append(
            f"{names[abbr]}\n{events:.0f}/{total:.0f} ({freq:.1f}%)"
        )

    ax.set_xticks(np.arange(len(clouds)))
    ax.set_yticks(np.arange(len(clouds)))
    ax.set_xticklabels(xlabels)
    ax.set_yticklabels(ylabels)
    ax.set_xlabel("7 AM Cloud Coverage")
    ax.set_ylabel("1 AM Cloud Coverage")

    fig.savefig("260617.png")


if __name__ == "__main__":
    main()
