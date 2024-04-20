"""Some of the special 15s data from the eclipse."""

import glob
from zoneinfo import ZoneInfo

import pandas as pd
from matplotlib.dates import DateFormatter, MinuteLocator
from matplotlib.lines import Line2D
from pyiem.plot import figure_axes


def main():
    """Go Main."""
    # https://www.chromosphere.co.uk/wp-content/blogs.dir/1/files/2015/03/eclipse_percent.py
    eclipse = pd.read_csv("/tmp/eclipse.dat")

    frames = []
    for fn in glob.glob("/tmp/WestPoint_EclipseSI*.dat"):
        obs = pd.read_csv(
            fn,
            skiprows=[0, 2, 3],
            na_values=["NAN", "INF"],
            encoding="ISO-8859-1",
        )
        frames.append(obs)
    df = pd.concat(frames)
    df["utc_valid"] = pd.to_datetime(
        df["TIMESTAMP"], format="%Y-%m-%d %H:%M:%S"
    ) + pd.Timedelta("6 hours")
    df["utc_valid"] = df["utc_valid"].dt.tz_localize("UTC")
    eclipse["utc_valid"] = pd.to_datetime(eclipse["utc_valid"]).dt.tz_localize(
        "UTC"
    )
    df = df.set_index("utc_valid").sort_index()
    eclipse = eclipse.set_index("utc_valid")

    fig, ax = figure_axes(
        title="8 April 2024 Solar Eclipse near West Point, IA",
        subtitle=(
            "15s instantaneous solar radiation from ISU Soil Moisture Station"
        ),
        figsize=(10.24, 7.68),
    )
    ax.set_position([0.1, 0.2, 0.8, 0.7])
    ax.plot(df.index.values, df["SlrW"], lw=2, color="k")
    ax2 = ax.twinx()
    ax2.plot(eclipse.index.values, eclipse["coverage"], lw=2)
    ax2.set_ylim(0, 100)
    ax2.set_ylabel(
        f"Eclipse Coverage [%] Max: {eclipse['coverage'].max():.1f}%",
        color="b",
    )

    x1 = eclipse[eclipse["coverage"] > 0].index[0]
    x2 = eclipse[eclipse["coverage"] > 0].index[-1]
    ax.axvline(x1, lw=2, color="r", zorder=2)
    ax.axvline(x2, lw=2, color="r", zorder=2)
    obs1 = df.at[x1, "SlrW"]
    obs2 = df.at[x2, "SlrW"]
    # ax.plot([x1, x2], [obs1, obs2], lw=2, color="r", zorder=2)
    df["coverage"] = eclipse["coverage"] / 100.0
    df.at[x1, "linear"] = obs1
    df.at[x2, "linear"] = obs2
    # df["theory"] = df["theory"] - bias
    print(
        df.loc[
            pd.Timestamp("2024-04-08 19:00+00") : pd.Timestamp(
                "2024-04-08 19:05+00"
            )
        ][["SlrW", "coverage"]]
    )
    tomorrow = df.loc[x1.replace(day=13) : x2.replace(day=13)].copy()
    tomorrow.index = tomorrow.index - pd.Timedelta("5 day")
    df["max"] = tomorrow["SlrW"] - 13
    df["theory"] = df["max"] * (1 - df["coverage"])
    df2 = df.loc[x1:x2]
    ax.plot(df2.index.values, df2["max"], label="Theory", lw=2, color="g")
    ax.plot(df2.index.values, df2["theory"], ls=":", lw=2, color="k")

    ax.xaxis.set_major_locator(MinuteLocator(byminute=[0, 15, 30, 45]))
    ax.xaxis.set_major_formatter(
        DateFormatter("%-I:%M\n%p", tz=ZoneInfo("America/Chicago"))
    )
    ax.set_ylim(0, 1000)
    ax.set_xlim(x1 - pd.Timedelta(hours=1), x2 + pd.Timedelta(hours=1))
    ax2.set_xlim(x1 - pd.Timedelta(hours=1), x2 + pd.Timedelta(hours=1))
    ax.grid(True)
    ax.set_ylabel("Solar Radiation [W m-2]")

    labels = [
        "Eclipse Coverage [%]",
        "Period of Eclipse",
        "No-Eclipse Clear Sky Est",
        "No-Eclipse * (1 - Coverage/100)",
        f"Observed, Min: {df2['SlrW'].min():.1f} W m-2",
    ]
    ax.legend(
        [
            Line2D([0], [0], color="b", lw=2),
            Line2D([0], [0], color="r", lw=2),
            Line2D([0], [0], color="g", lw=2),
            Line2D([0], [0], color="brown", ls=":", lw=2),
            Line2D([0], [0], color="k", lw=2),
        ],
        labels,
        loc=(0.0, -0.2),
        ncol=3,
    )

    fig.savefig("240420.png")


if __name__ == "__main__":
    main()
