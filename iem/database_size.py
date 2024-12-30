"""Total up database usage."""

import pandas as pd
from pyiem.plot import figure
from pyiem.plot.use_agg import plt

ARCHIVES = [
    ("ASOS/METAR Observations", 183_000_000),
    ("ASOS Satellite Cloud Prod", 54_000_000),
    ("TAF Forecasts", 5_000_000),
    ("Temp/Winds Aloft", 1_900_000),
    ("HML Forecast Data", 72_000_000),
    ("HML Observations", 580_000_000),
    ("CF6 Data", 331_000),
    ("CLI Data", 227_000),
    ("Hourly Precip Reports", 54_000_000),
    ("Daily Summary Data", 20_000_000),
    ("Daily Climodat Reports", 2_100_000),
    ("HADS/SHEF Reports", 2_300_000_000),
    ("NLDN Lightning Strokes", 51_000_000),
    ("Local Storm Reports", 218_000),
    ("VTEC Warnings", 402_000),
    ("Storm Based Warnings", 157_000),
    ("Pilot Reports (PIREPS)", 1_100_000),
    ("Special Weather Statements", 52_000),
    ("NEXRAD Storm Attributes", 52_000_000),
    ("Upper Air/RAOB Observations", 14_400_000),
    ("NWS Text Products", 21_200_000),
    ("ASOS 1 Minute Data", 373_000_000),
    ("ISU Soil Moisture Network", 14_000_000),
    ("Webcam Telemetry", 37_000_000),
    ("Model Output Statistics", 980_000_000),
    ("Roadway Weather (RWIS)", 42_000_000),
    ("SCAN Observations", 1_800_000),
    ("US Climate Reference Network", 15_000_000),
    ("BUFR Surface Data", 46_000_000),
]


def main():
    """Go Main."""
    obs = pd.DataFrame(ARCHIVES, columns=["name", "size"])
    obs = obs.sort_values("size", ascending=False)

    # Insert blank rows every 5 bars
    spacing = 5
    for i in range(spacing, len(obs) + 5, spacing):
        obs = pd.concat(
            [
                obs.iloc[:i],
                pd.DataFrame([["", 0]], columns=obs.columns),
                obs.iloc[i:],
            ],
            ignore_index=True,
        ).reindex()
    plt.style.use("ggplot")
    fig = figure(
        title="2024 IEM Estimated Database Row Counts by Observation Type",
        subtitle=f"Total row counts plotted: {obs['size'].sum():,.0f}",
        figsize=(8, 6),
    )
    ax = fig.add_axes((0.3, 0.05, 0.55, 0.85), facecolor="white")
    ax.grid(axis="x", color="gray")
    ax.set_xscale("log")
    ax.barh(obs.index.to_numpy(), obs["size"], fc="b", ec="b")
    ax.set_yticks(obs.index.to_numpy())
    ax.set_yticklabels(obs["name"])
    for idx, row in obs.iterrows():
        if row["size"] == 0:
            continue
        label = ""
        # create pretty number with K, M, or B
        if row["size"] > 1_000_000_000:
            label = f"{row['size'] / 1_000_000_000:.1f}B"
        elif row["size"] > 1_000_000:
            label = f"{row['size'] / 1_000_000:.0f}M"
        elif row["size"] > 1_000:
            label = f"{row['size'] / 1_000:.0f}K"
        ax.text(
            row["size"],
            idx,
            f"   {label}",
            va="center",
            bbox=dict(color="white", pad=0),
        )
    ax.set_ylim(-0.5, len(obs) - 0.5)
    fig.savefig("241231.png")


if __name__ == "__main__":
    main()
