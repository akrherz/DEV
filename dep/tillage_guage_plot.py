"""Creating a single gauge plot showing the yearly average soil delivery.

The gauge should go from 0 to 20 t/a/yr, with the following color scheme:
- Green: 0-5 t/a/yr
- Yellow: 5-10 t/a/yr
- Orange: 10-15 t/a/yr
- Red: 15-20 t/a/yr

The gauge should have a black outline and a black needle pointing to the
appropriate value.

The gauge should have a title of "Yearly Average Soil Delivery [t/a/yr]" and
a subtitle of "Scenario: {scenario}".

The gauge should be saved to the file "gauge.png".
"""

import math

import click
import pandas as pd
from matplotlib.patches import Rectangle
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import figure


def gauge_factory(fig, row, col, title, value):
    """."""
    x0 = 0.05
    y0 = -0.02
    width = 0.28
    height = 0.23
    spacing = 0.02
    if col == 0:
        faux = fig.add_axes([0, 0, 1, 1], frame_on=False)
        faux.axhline(y0 + height * (row + 1) + 0.07 * (row + 1), color="black")
    ax = fig.add_axes(
        [
            x0 + col * spacing + col * width,
            y0 + row * spacing * 3 + row * height,
            width,
            height,
        ],
        projection="polar",
        frame_on=False,
    )
    ax.set_rorigin(-4.5)
    ax.set_yticks([])

    # 0 to 2 T/a/yr
    ax.add_patch(
        Rectangle((math.pi * 0.8, 1), math.pi * 0.2, 2, color="#4CE600")
    )
    # 2 - 5
    ax.add_patch(
        Rectangle((math.pi * 0.5, 1), math.pi * 0.3, 2, color="#A9FF6A")
    )
    # 5 to 8
    ax.add_patch(
        Rectangle((math.pi * 0.2, 1), math.pi * 0.3, 2, color="#FFAA00")
    )
    # 8 to 10
    ax.add_patch(Rectangle((0, 1), math.pi * 0.2, 2, color="#FF0000"))
    ax.set_xlim(0, math.pi)
    ax.set_xticks([0, math.pi * 0.2, math.pi * 0.5, math.pi * 0.8, math.pi])
    ax.set_xticklabels(["10", "8", "5", "2", "0"])

    ax.arrow(
        (10 - min(10, value)) / 10.0 * math.pi,
        -4.5,
        0,
        5.0,
        width=0.1,
        head_width=0.2,
        head_length=1,
        fc="yellow",
        ec="k",
        clip_on=False,
    )
    # https://github.com/matplotlib/matplotlib/issues/8521/
    ax.bar(0, 1).remove()
    ax.text(
        0.5,
        1,
        f"{title}\n{value:.1f} T/a/yr",
        fontsize=14,
        transform=ax.transAxes,
        ha="center",
    )


@click.command()
@click.option("--huc12", help="HUC12 to plot")
def main(huc12):
    """."""
    with get_sqlalchemy_conn("idep") as conn:
        huc12df = pd.read_sql(
            "SELECT huc_12, name "
            "from huc12 WHERE scenario = 0 and huc_12 = %s",
            conn,
            params=(huc12,),
            index_col="huc_12",
        )
    fn = f"scenario_tracks_{huc12}.csv"
    dfall = pd.read_csv(fn)

    fig = figure(
        title=f"HUC12: {huc12} {huc12df.loc[huc12, 'name']}",
        subtitle="Yearly Hillslope Soil Delivery by Tillage Scenario",
        logo="dep",
        figsize=(8, 6),
    )
    gauge_factory(
        fig, 2, 0, "Baseline", dfall[dfall["scenario"] == 0]["delivery"].mean()
    )
    gauge_factory(
        fig,
        2,
        1,
        "Pasture",
        dfall[dfall["scenario"] == 165]["delivery"].mean(),
    )
    gauge_factory(
        fig,
        2,
        2,
        "No Till",
        dfall[dfall["scenario"] == 157]["delivery"].mean(),
    )

    gauge_factory(
        fig,
        1,
        0,
        "Very High Mulch (no Chisel)",
        dfall[dfall["scenario"] == 164]["delivery"].mean(),
    )
    gauge_factory(
        fig,
        1,
        1,
        "Very High Mulch",
        dfall[dfall["scenario"] == 158]["delivery"].mean(),
    )
    gauge_factory(
        fig,
        1,
        2,
        "High Mulch",
        dfall[dfall["scenario"] == 159]["delivery"].mean(),
    )

    gauge_factory(
        fig,
        0,
        0,
        "Medium Mulch",
        dfall[dfall["scenario"] == 160]["delivery"].mean(),
    )
    gauge_factory(
        fig,
        0,
        1,
        "Low Mulch",
        dfall[dfall["scenario"] == 161]["delivery"].mean(),
    )
    gauge_factory(
        fig,
        0,
        2,
        "Moldboard Plow",
        dfall[dfall["scenario"] == 162]["delivery"].mean(),
    )

    # Save the gauge to a file
    fig.savefig(f"/tmp/{huc12}_tillage_gauge.png")


if __name__ == "__main__":
    main()
