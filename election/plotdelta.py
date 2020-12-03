"""Here we are."""

from pyiem.plot.use_agg import plt
import pandas as pd


def main():
    """Go Main Go."""
    xl = pd.ExcelFile("/tmp/election.xlsx")
    df2016 = pd.read_excel(xl, "2016", index_col="State")
    df2020 = pd.read_excel(xl, "2020", index_col="State")
    df2016["trump_percent"] = df2016["Trump"] / df2016["Total Votes"] * 100
    df2016["clinton_percent"] = df2016["Clinton"] / df2016["Total Votes"] * 100
    df2016["trump_margin"] = (
        df2016["trump_percent"] - df2016["clinton_percent"]
    )
    df2020["trump_percent"] = df2020["Trump"] / df2020["Total Votes"] * 100
    df2020["biden_percent"] = df2020["Biden"] / df2020["Total Votes"] * 100
    df2020["trump_margin"] = df2020["trump_percent"] - df2020["biden_percent"]

    (fig, ax) = plt.subplots(1, 1, figsize=(12, 6.75))
    delta = (
        (df2020["Total Votes"] - df2016["Total Votes"])
        / df2016["Total Votes"]
        * 100
    )
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
    ax.set_xlim(0, 40.0)
    ax.set_xlabel("Voter Turnout Percent Change (2020 - 2016)", fontsize=20)
    ax.set_title(
        "2020 vs 2016 Percentage Change in Total Votes Cast", fontsize=26
    )
    fig.text(0.05, 0.01, "@akrherz, 3 Dec 2020. Data: uselectionatlas.org")
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
