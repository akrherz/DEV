"""Here we are."""

import pandas as pd
from pyiem.plot.use_agg import plt

TV = "Total Votes"


def main():
    """Go Main Go."""
    xl = pd.ExcelFile("election.xlsx")
    df2016 = pd.read_excel(xl, "2016", index_col="State")
    df2020 = pd.read_excel(xl, "2020", index_col="State")
    df2016["third_percent"] = (
        (df2016[TV] - df2016["Trump"] - df2016["Clinton"]) / df2016[TV] * 100.0
    )
    df2020["third_percent"] = (
        (df2020[TV] - df2020["Trump"] - df2020["Biden"]) / df2020[TV] * 100.0
    )
    df2016["trump_percent"] = df2016["Trump"] / df2016["Total Votes"] * 100
    df2016["clinton_percent"] = df2016["Clinton"] / df2016["Total Votes"] * 100
    df2016["trump_margin"] = (
        df2016["trump_percent"] - df2016["clinton_percent"]
    )
    df2020["trump_percent"] = df2020["Trump"] / df2020["Total Votes"] * 100
    df2020["biden_percent"] = df2020["Biden"] / df2020["Total Votes"] * 100
    df2020["trump_margin"] = df2020["trump_percent"] - df2020["biden_percent"]
    tip = (df2016["third_percent"] - df2020["third_percent"]) / 2.0
    print(df2016["third_percent"])
    delta = df2020["trump_percent"] - df2016["trump_percent"] - tip

    (fig, ax) = plt.subplots(1, 1, figsize=(12, 6.75))
    delta = delta.sort_values()
    bars = ax.barh(range(len(delta.index)), delta.values)
    for i, (mybar, state, val) in enumerate(
        zip(bars, delta.index.values, delta.values)
    ):
        if state in [
            "Georgia",
            "Michigan",
            "Wisconsin",
            "Arizona",
            "Pennsylvania",
            "Nevada",
        ]:
            mybar.set_color("r")
        x = val + 0.1 if val > 0 else val - 0.1
        ha = "right" if val < 0 else "left"
        ax.text(x, i, state, fontsize=10, va="center", ha=ha)
    ax.set_ylim(-0.7, 49.7)
    ax.set_yticks([])
    ax.set_xlim(-6, 3.0)
    ax.set_xlabel(
        "Absolute Percentage Point Change (2020 - 2016)", fontsize=20
    )
    ax.set_title(
        "2020 vs 2016 Trump Percentage Point Change\nAfter 3rd Party "
        "Percentage Point 2016-2020 Delta Equally Removed",
        fontsize=16,
    )
    fig.text(0.05, 0.01, "@akrherz, 3 Dec 2020. Data: uselectionatlas.org")
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
