"""Generate a plot of 1minute srad."""


import pandas as pd
from pyiem.plot import figure
from pyiem.util import get_sqlalchemy_conn


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("isuag") as conn:
        df = pd.read_sql(
            """
            SELECT valid, slrkj_tot * 1000. / 60. as wmps,
            extract(day from valid) as day,
            extract(minute from valid) +
                extract(hour from valid) * 60. as minute
            from sm_minute where station = 'KNAI4'
            and valid > '2023-05-16' ORDER by valid ASC
        """,
            conn,
            index_col=None,
        )

    fig = figure(
        title="ISU Soil Moisture -- Kanawha [NC Iowa] Solar Radiation",
        subtitle=(
            "Impact of Canadian Wildfire Smoke on 17th, "
            "some smoke on evening of 16th"
        ),
        figsize=(10.24, 7.68),
    )
    ax = fig.add_axes([0.1, 0.35, 0.85, 0.55])
    ax2 = fig.add_axes([0.1, 0.1, 0.85, 0.25])
    df2 = df[df["day"] == 16].copy().set_index("minute")
    mj = (df2["wmps"] * 60).sum() / 1_000_000.0
    ax.plot(
        df2.index.values, df2["wmps"].values, label=f"16 May 2023: {mj:.1f} MJ"
    )
    df3 = df[df["day"] == 17].copy().set_index("minute")
    mj = (df3["wmps"] * 60).sum() / 1_000_000.0
    ax.plot(
        df3.index.values, df3["wmps"].values, label=f"17 May 2023: {mj:.1f} MJ"
    )
    delta = df3["wmps"] - df2["wmps"]
    ax2.bar(delta.index.values, delta.values)

    for _ax in [ax, ax2]:
        _ax.grid(True)
        _ax.set_xlim(300, 22 * 60)
        _ax.set_xticks(range(360, 22 * 60 + 1, 120))
        _ax.set_xlabel("Central Daylight Time")
    ax.set_xticklabels([])
    ax2.set_xticklabels(
        [
            "6 AM",
            "8 AM",
            "10 AM",
            "Noon",
            "2 PM",
            "4 PM",
            "6 PM",
            "8 PM",
            "10 PM",
        ]
    )
    ax.legend()
    ax.set_ylabel("One Minute Averaged Solar Rad [W m-2]")
    ax2.set_ylabel("17th minus 16th [W m-2]")
    fig.savefig("230518.png")


if __name__ == "__main__":
    main()
