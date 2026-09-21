"""Summarize the sweepin variables with a fancy pants histogram.

A single plot with each variable showing a horizontal histogram.

"""

import pandas as pd
from pyiem.plot import figure


def main():
    """Go Main Go."""
    df = pd.read_csv("sweepin_vars.csv")
    fig = figure(
        title="30 Apr 2023 :: Sweepin Variable Histograms",
        logo="dep",
    )
    vars_to_plot = df.columns[2:]
    subplot_width = 0.9 / len(vars_to_plot)
    x0 = 0.05
    for varname in vars_to_plot:
        ax = fig.add_axes((x0 + 0.02, 0.05, subplot_width - 0.05, 0.75))
        ax.hist(df[varname], bins=20, orientation="horizontal")
        avgval = df[varname].mean()
        ax.set_title(f"{varname}\nAvg:{avgval:.2f}")
        ax.axhline(avgval, color="red", linestyle="--")
        if "wind" in varname:
            ax.set_ylim(top=25)
        x0 += subplot_width

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
