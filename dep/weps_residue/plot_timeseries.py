"""Diagnostic Plot."""

import click
import numpy as np
import pandas as pd
from pyiem.plot import figure

DATE_AXIS = pd.date_range("2007/01/01", "2026/12/31")
XWIDTH = 0.19
pd.set_option("display.max_rows", 500)


@click.command()
@click.option("--filename", default="plot.out")
def main(filename: str) -> None:
    """Go Main Go."""
    data = np.loadtxt(filename, skiprows=1)
    with open(filename) as fh:
        names = [
            x.strip() for x in fh.read(1000).split("\n")[0][2:].split("|")
        ]
    dailydf = pd.DataFrame(data, columns=names, index=DATE_AXIS)
    dailydf["doy"] = dailydf.index.dayofyear
    cols = [
        "t_ne_bare",
        "cr_fr_los",
        "ne_sfcv",
        "ridg_ht",
        "fl_cov%",
        "r_rough",
        "cr_fract",
    ]
    print(dailydf.loc[pd.Timestamp("2007-11-07")][cols])
    print(dailydf.loc[pd.Timestamp("2007-11-08")][cols])
    print(dailydf.loc[pd.Timestamp("2008-04-13")][cols])
    print(dailydf.loc[pd.Timestamp("2008-04-14")][cols])
    print(dailydf.loc[pd.Timestamp("2008-04-17")][cols])
    print(dailydf.loc[pd.Timestamp("2008-04-18")][cols])

    print(dailydf[cols].describe())

    df = dailydf
    df["energy_gap"] = df["ne_wus"] - df["t_wust"]
    exceeded = df[df["energy_gap"] > 0]

    print(f"Total timesteps: {len(df)}")
    print(
        f"Days where Net Energy (ne_wus) > Threshold (t_wust): {len(exceeded)}"
    )

    print("\n--- Summary Statistics ---")
    print(f"Mean Anemometer Ustar (wus_anemom): {df['wus_anemom'].mean():.4f}")
    print(f"Mean Net Surface Ustar (ne_wus):     {df['ne_wus'].mean():.4f}")
    print(f"Mean Threshold Ustar (t_wust):       {df['t_wust'].mean():.4f}")

    print(f"Max ne_wus recorded:  {df['ne_wus'].max():.4f}")
    print(f"Min t_wust recorded:  {df['t_wust'].min():.4f}")

    # Filter for the 24 threshold-exceeding days
    exceeded = df[df["ne_wus"] > df["t_wust"]]

    # Print key variables on those days
    cols = [
        "daysim",
        "tot_loss",
        "ne_wus",
        "t_wust",
        "cr_fract",
        "cr_ms_los",
        "precip",
        "snow_depth",
    ]
    print(exceeded[cols])

    fig = figure(
        title="man: 090201081102_93.man soil: sand7.ifc wind: NW_MN.win",
        subtitle="WEPS run with -W0 (darcian flow)",
        logo="dep",
        figsize=(10, 10),
    )
    (ax, ax1, ax2, ax3, ax4) = fig.subplots(5, 1, sharex=True)
    ax.plot(
        dailydf.index.to_numpy(),
        dailydf["cr_fract"].to_numpy(),
    )
    ax.set_ylabel("cr_fract")
    ax.grid(True)

    #
    ptime_below_05 = (
        (dailydf["t_surf_wet"] < 0.5).sum() / len(dailydf.index) * 100.0
    )
    ax1.set_title(f"% Time below 0.5m/s: {ptime_below_05:.1f}%")
    ax1.plot(
        dailydf.index.to_numpy(),
        dailydf["t_surf_wet"].to_numpy(),
    )
    ax1.set_ylabel("t_surf_wet [m/s]")
    ax1.grid(True)

    #
    ptime_below_05 = (
        (dailydf["t_flat_cov"] < 0.5).sum() / len(dailydf.index) * 100.0
    )
    ax2.set_title(f"% Time below 0.5m/s: {ptime_below_05:.1f}%")
    ax2.plot(
        dailydf.index.to_numpy(),
        dailydf["t_flat_cov"].to_numpy(),
    )
    # ax2.set_ylim(0, 1)
    ax2.set_ylabel("t_flat_cov")
    ax2.grid(True)

    #
    ptime_below_05 = (
        (dailydf["t_ne_bare"] < 0.5).sum() / len(dailydf.index) * 100.0
    )
    ax3.set_title(f"% Time below 0.5m/s: {ptime_below_05:.1f}%")
    ax3.plot(
        dailydf.index.to_numpy(),
        dailydf["t_ne_bare"].to_numpy(),
    )
    ax3.set_ylabel("t_ne_bare [m/s]")
    ax3.grid(True)

    #
    ax4.plot(
        dailydf.index.to_numpy(),
        dailydf["ne_sfcv"].to_numpy(),
    )
    ax4.set_ylabel("ne_sfcv")
    ax4.grid(True)

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
