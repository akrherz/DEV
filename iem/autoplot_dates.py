"""
for file in $(git ls-files); do
HASH=$(git rev-list HEAD "$file" | tail -n 1);
DATE=$(git show -s --format="%ci" $HASH --);
printf "%-35s %s  %s\n" "$file" $HASH: "$DATE"; done
"""

import pandas as pd
from pyiem.plot import figure_axes


def main():
    """Go Main Go."""
    df = pd.read_csv("autoplot_dates.txt", header=None)
    df.columns = ["num", "hash", "dt"]
    df["dt"] = pd.to_datetime(df["dt"])
    df = df.sort_values("num", ascending=True)
    df["count"] = 1
    df["acc"] = df["count"].cumsum()

    fig, ax = figure_axes(
        title="IEM Accumulated Number of 'Autoplot' Applications",
        subtitle="220 Total as of 14 July 2021, First on 24 August 2014.",
        figsize=(8, 6),
    )
    ax.plot(df["dt"], df["acc"])
    ax.set_ylabel("Accumulated Number of Apps")
    ax.grid(True)

    fig.savefig("210715.png")


if __name__ == "__main__":
    main()
