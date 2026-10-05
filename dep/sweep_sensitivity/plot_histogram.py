"""Summarize the sweepin variables with a fancy pants histogram.

A single plot with each variable showing a horizontal histogram.

"""

from pathlib import Path

import click
import pandas as pd
from pyiem.plot import figure


@click.command()
@click.option(
    "--filename",
    type=click.Path(exists=True),
    required=True,
    help="The CSV file containing sweepin variables.",
)
def main(filename: Path):
    """Go Main Go."""
    df = pd.read_csv(filename)
    fig = figure(
        title="12 May 2026 :: Sweepin Variable Histograms",
        subtitle="Combined and partitioned by 2025 crop",
        logo="dep",
        figsize=(10.24, 10.24),
    )
    vars_to_plot = df.columns[6:]
    subplot_width = 0.9 / len(vars_to_plot)
    x0 = 0.1
    colors = {"B": "blue", "C": "green", "P": "purple"}
    for varname in vars_to_plot:
        ax = fig.add_axes((x0 + 0.02, 0.7, subplot_width - 0.05, 0.15))
        ax.hist(df[varname], bins=20, orientation="horizontal")
        avgval = df[varname].mean()
        ax.set_title(
            f"{varname}\nAvg:{avgval:.2f}, Max:{df[varname].max():.2f}",
            fontsize=10,
        )
        ax.axhline(avgval, color="red", linestyle="--")
        ax.set_ylim(top=25 if "wind" in varname else 1)

        y0 = 0.7
        for crop in ["B", "C", "P"]:
            ax = fig.add_axes(
                (x0 + 0.02, y0 - 0.2, subplot_width - 0.05, 0.15)
            )
            df2 = df[df["prev_crop"] == crop]
            ax.hist(
                df2[varname],
                bins=20,
                orientation="horizontal",
                label=crop,
                color=colors[crop],
            )
            avgval = df2[varname].mean()
            ax.set_title(
                f"Avg:{avgval:.2f}, Max:{df2[varname].max():.2f}",
                fontsize=10,
            )
            ax.axhline(avgval, color="red", linestyle="--")
            ax.set_ylim(top=25 if "wind" in varname else 1)

            y0 -= 0.2

        x0 += subplot_width

    fig.text(0.01, 0.2, "Alfalfa")
    fig.text(0.01, 0.4, "Corn")
    fig.text(0.01, 0.6, "Soybean")
    fig.text(0.01, 0.8, "All")

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
