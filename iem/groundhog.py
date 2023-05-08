"""Compute some groundhog statistics."""

import matplotlib.patches as mpatches
import pandas as pd
from pyiem.plot import figure
from pyiem.util import get_dbconnstr


def main():
    """Go Main Go."""
    obs = pd.read_sql(
        "SELECT valid, skyc1, skyc2, skyc3, skyc4 from alldata where "
        "station = 'DSM' and to_char(valid, 'MMDD') = '0202' and "
        "extract(minute from valid) > 50 and "
        "extract(hour from valid) = 7 and valid > '2007-01-01' "
        "and report_type = 2 ORDER by valid ASC",
        get_dbconnstr("asos"),
    )

    cobs = pd.read_sql(
        "SELECT year, sum(snow) as snow_total, avg((high+low)/2.) as avg_t "
        "from alldata_ia where station = 'IATDSM' and sday > '0202' and "
        "sday < '0316' GROUP by year",
        get_dbconnstr("coop"),
        index_col="year",
    )

    climo = cobs.mean()

    title = "Des Moines Groundhog Forecast for Next 6 Weeks (3 Feb - 16 Mar)"
    fig = figure(apctx={"_r": "43"}, title=title)
    ax = fig.add_axes([0, 0, 1, 1], frame_on=False)
    ypos = 0.82
    dy = 0.055

    fig.text(0.15, ypos + dy, "7 AM Sunshine [1]", fontsize=16)
    fig.text(
        0.4, ypos + dy, f'Snowfall ({climo["snow_total"]:.1f}")', fontsize=16
    )
    fig.text(
        0.6,
        ypos + dy,
        f"Avg Temp ({climo['avg_t']:.1f}" r"$^\circ$F)",
        fontsize=16,
    )
    fig.text(0.85, ypos + dy, "Verification", fontsize=16)

    for _, row in obs.iterrows():
        year = row["valid"].year
        if year % 5 == 0:
            ax.plot([0.05, 0.95], [ypos, ypos], "k-", lw=2)
        fig.text(0.07, ypos, f"{year}", fontsize=16, va="bottom")
        overcast = "OVC" in [
            row["skyc1"],
            row["skyc2"],
            row["skyc3"],
            row["skyc4"],
        ]
        fig.text(
            0.15,
            ypos,
            "No Shadow" if overcast else "Shadow",
            fontsize=16,
            color="r" if overcast else "b",
            va="bottom",
        )

        # ---------------
        ob_snow = cobs.at[year, "snow_total"]
        dep_snow = ob_snow - climo["snow_total"]
        fig.text(
            0.4,
            ypos,
            f'{ob_snow:.1f}"',
            color="b" if dep_snow > 0 else "r",
            fontsize=16,
            va="bottom",
        )
        if dep_snow < 0:
            # draw red arrow pointing down
            arrow = mpatches.FancyArrowPatch(
                (0.5, ypos + dy - 0.01),
                (0.5, ypos),
                mutation_scale=40,
                color="r",
            )
            ax.add_patch(arrow)
        else:
            arrow = mpatches.FancyArrowPatch(
                (0.5, ypos),
                (0.5, ypos + dy - 0.01),
                mutation_scale=40,
                color="b",
            )
            ax.add_patch(arrow)

        # ---------------
        ob_avgt = cobs.at[year, "avg_t"]
        dep_avgt = ob_avgt - climo["avg_t"]
        fig.text(
            0.6,
            ypos,
            f"{ob_avgt:.1f}" r"$^\circ$F",
            color="r" if dep_avgt > 0 else "b",
            fontsize=16,
            va="bottom",
        )
        if dep_avgt < 0:
            arrow = mpatches.FancyArrowPatch(
                (0.7, ypos + dy - 0.01),
                (0.7, ypos),
                mutation_scale=40,
                color="b",
            )
            ax.add_patch(arrow)
        else:
            arrow = mpatches.FancyArrowPatch(
                (0.7, ypos),
                (0.7, ypos + dy - 0.01),
                mutation_scale=40,
                color="r",
            )
            ax.add_patch(arrow)

        v = "✓"
        c = "g"
        if overcast and (dep_snow > 0 or dep_avgt < 0):
            v = "✗"
            c = "r"
        elif not overcast and (dep_snow < 0 or dep_avgt > 0):
            v = "✗"
            c = "r"
        ax.text(0.85, ypos, v, fontsize=18, va="bottom", color=c)
        ypos -= dy

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    fig.text(
        0.5,
        0.02,
        "[1] No Shadow means overcast skies reported",
        ha="center",
        fontsize=12,
    )
    fig.savefig("220202.png")


if __name__ == "__main__":
    main()
