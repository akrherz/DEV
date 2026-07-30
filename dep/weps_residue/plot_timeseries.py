"""Diagnostic Plot."""

import click
import numpy as np
import pandas as pd
from pyiem.plot import figure

DATE_AXIS = pd.date_range("2007/01/01", "2026/12/31")
XWIDTH = 0.19


@click.command()
def main() -> None:
    """Go Main Go."""
    data = np.loadtxt("plot.out", skiprows=1)
    with open("plot.out") as fh:
        names = [
            x.strip() for x in fh.read(1000).split("\n")[0][2:].split("|")
        ]
    dailydf = pd.DataFrame(data, columns=names, index=DATE_AXIS)
    dailydf["doy"] = dailydf.index.dayofyear

    fig = figure(
        title="WEPS Surface Water and resultant Threshold Friction Velocity",
        subtitle="WEPS run with -W0 (darcian flow)",
        logo="dep",
    )
    ax = fig.add_axes((0.1, 0.55, 0.8, 0.35))
    ax.plot(
        dailydf.index.to_numpy(),
        dailydf["Surf_H2O"].to_numpy() * 1000.0,
    )
    ax.set_ylabel("Surf_H2O [g/kg]")
    ax.grid(True)

    ptime_below_05 = (
        (dailydf["t_surf_wet"] < 0.5).sum() / len(dailydf.index) * 100.0
    )
    ax = fig.add_axes((0.1, 0.1, 0.8, 0.35))
    ax.set_title(f"% Time below 0.5m/s -> {ptime_below_05:.1f}%")
    ax.plot(
        dailydf.index.to_numpy(),
        dailydf["t_surf_wet"].to_numpy(),
    )
    ax.set_ylabel("t_surf_wet [m/s]")
    ax.grid(True)

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
