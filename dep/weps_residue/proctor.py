"""Proctor the running of these tests."""

import calendar
import os
import subprocess
from pathlib import Path

import click
import numpy as np
import pandas as pd
from dailyerosion.reference import KG_M2_TO_TON_ACRE
from jinja2 import Template
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from pydantic import BaseModel
from pyiem.plot import figure

DATE_AXIS = pd.date_range("2007/01/01", "2026/12/31")
VARNAMES = {
    "fl_cov%": "Fractional Flat Cover %",
    "ne_wus": "Actual Friction Velocity",
    "ne_sfcv": "Actual Sfc Clod+Crust",
    "ne_sf84": "Actual Sfc Fract < 0.84mm",
    "t_wust": "Threshold Friction Velocity",
    "t_flat_cov": "Threshold Friction Velocity\nfor Flat Cover",
    "t_ne_bare": "Bare\nThreshold Friction Velocity",
    "t_surf_wet": "Threshold Friction Velocity\nfor Surface Wetness",
    "wus_anemom": "Friction Velocity\nafter Anemometer Only",
    "wus_random": "Friction Velocity\nafter Random Roughness Only",
    "wus_ridge": "Friction Velocity\nafter Ridge Only",
    "wus_biodrg": "Friction Velocity\nafter Biodrag Only",
}
XWIDTH = 0.19


class WEPSRun(BaseModel):
    """What knobs we turn."""

    man_file: str
    soil_file: str
    wind_file: str


def add_month_labels(ax: Axes):
    """Go common things."""
    ax.set_xticks([1, 60, 121, 182, 244, 305])
    ax.set_xticklabels(calendar.month_abbr[1:][::2])


def do_friction(dailydf: pd.DataFrame, fig: Figure):
    """Do the hard work here."""
    xpos = 0.05
    xdelta = 0.24
    ymax = None
    for stepvar in ["t_ne_bare", "t_flat_cov", "t_ag_den", "t_surf_wet"]:
        ax = fig.add_axes((xpos, 0.6, XWIDTH, 0.25))
        xpos += xdelta
        ax.set_title(VARNAMES.get(stepvar, stepvar))
        ax.set_ylabel(stepvar)
        for yr in range(2007, 2027):
            yeardf = dailydf[dailydf.index.year == yr]
            ax.scatter(
                yeardf["doy"],
                yeardf[stepvar].to_numpy(),
            )
        add_month_labels(ax)
        ax.grid(True)
        if ymax is None:
            ymax = ax.get_ylim()[1]
        # ax.set_ylim(0, ymax)


def row2(dailydf: pd.DataFrame, fig: Figure):
    """Stuff done in row2"""

    ax1 = fig.add_axes((0.05, 0.35, XWIDTH, 0.2))
    ax1.set_title("Does t_* == t_wust?")
    ax1.set_ylabel("Difference")
    for yr in range(2007, 2027):
        yeardf = dailydf[dailydf.index.year == yr]
        sanity = (
            yeardf[["t_ne_bare", "t_flat_cov", "t_ag_den", "t_surf_wet"]].sum(
                axis=1
            )
            - yeardf["t_wust"]
        )
        ax1.scatter(
            yeardf["doy"],
            sanity.to_numpy(),
        )
    add_month_labels(ax1)
    ax1.grid(True)
    ax1.set_ylim(-1, 1)

    ax1 = fig.add_axes((0.3, 0.35, XWIDTH, 0.2))
    ax1.set_title(VARNAMES["t_wust"])
    ax1.set_ylabel("t_wust")
    for yr in range(2007, 2027):
        yeardf = dailydf[dailydf.index.year == yr]
        ax1.scatter(
            yeardf["doy"],
            yeardf["t_wust"].to_numpy(),
        )
    add_month_labels(ax1)
    ax1.grid(True)
    ax1.set_ylim(bottom=0)
    ylim = ax1.get_ylim()

    ax1 = fig.add_axes((0.55, 0.35, XWIDTH, 0.2))
    ax1.set_title(VARNAMES["ne_wus"])
    ax1.set_ylabel("ne_wus")
    for yr in range(2007, 2027):
        yeardf = dailydf[dailydf.index.year == yr]
        ax1.scatter(
            yeardf["doy"],
            yeardf["ne_wus"].to_numpy(),
        )
    add_month_labels(ax1)
    ax1.grid(True)
    ax1.set_ylim(*ylim)

    # Compute contribution frequencies when the threshold was above the actual
    ax1 = fig.add_axes((0.75, 0.35, XWIDTH, 0.2), frame_on=False)
    ax1.set_title("Var Stops Erosion")
    ax1.set_xticks([])
    ax1.set_yticks([])
    cell_text = []
    for col in ["t_ne_bare", "t_flat_cov", "t_surf_wet", "t_ag_den", "t_wust"]:
        freq = (dailydf[col] >= dailydf["ne_wus"]).sum() / dailydf.shape[0]
        cell_text.append([col, f"{freq * 100.0:.2f}%"])
    ax1.table(
        cellText=cell_text,
        colLabels=["Variable", "Frequency"],
        loc="center",
        bbox=(0, 0, 1, 1),
    )


def run_model(config: WEPSRun):
    """Do the run."""
    if Path("weps.runx").exists():
        os.unlink("weps.runx")
    with open("weps_run.j2") as fh:
        tpl = Template(fh.read())
    with open("weps.run", "w") as fh:
        fh.write(tpl.render(**config.__dict__))
    subprocess.run(
        [
            "/tmp/weps",
            "-c0",  # No soil conditioning output, 1 is default
            "-H0",  # No heartbeat output for GUI, 1 is default
            "-I1",  # Initialization loops, 1 is default
            "-n1",  # Don't write XML inputs
            "-W0",  # Runoff calculation, holy sensitive to Surf_H2O
            "-u0",  # Resurface roots, default is 1 , sensitive
        ],
        check=True,
    )


@click.command()
@click.option("--var1", required=True)
@click.option("--var2", required=True)
@click.option("--man-file", required=True)
@click.option("--soil-file", required=True)
@click.option("--wind-file", required=True)
@click.option("--skiprun", is_flag=True, help="Skip running WEPS model")
def main(
    var1: str,
    var2: str,
    man_file: str,
    soil_file: str,
    wind_file: str,
    skiprun: bool,
) -> None:
    """Go Main Go."""
    cfg = WEPSRun(man_file=man_file, soil_file=soil_file, wind_file=wind_file)
    if not skiprun:
        run_model(cfg)
    data = np.loadtxt("plot.out", skiprows=1)
    with open("plot.out") as fh:
        names = [
            x.strip() for x in fh.read(1000).split("\n")[0][2:].split("|")
        ]
    dailydf = pd.DataFrame(data, columns=names, index=DATE_AXIS)
    dailydf["doy"] = dailydf.index.dayofyear

    tayr = abs(dailydf["tot_loss"].sum() * KG_M2_TO_TON_ACRE / 20.0)
    print(dailydf["max_wind"].groupby(dailydf.index.year).describe())
    print(
        dailydf[
            ["t_ne_bare", "t_flat_cov", "t_ag_den", "t_surf_wet"]
        ].describe()
    )
    events = (dailydf["tot_loss"] < 0).sum()
    fig = figure(
        title=(
            f"WEPS: man: {cfg.man_file} soil: {cfg.soil_file} "
            f"wind: {cfg.wind_file}"
        ),
        subtitle=(
            f"Total Erosion: {tayr:.2f} tons/acre/yr over {events} events"
        ),
        logo="dep",
        figsize=(10.24, 10.24),
    )
    do_friction(dailydf, fig)
    row2(dailydf, fig)

    # Diagnose eros, which is the off on flag, I believe
    ax = fig.add_axes((0.65, 0.05, XWIDTH, 0.23))
    data = np.zeros((20, 366))
    for yr in range(2007, 2027):
        yeardf = dailydf[dailydf.index.year == yr]
        data[yr - 2007, : len(yeardf.index)] = yeardf["eros"].to_numpy()
    ax.imshow(data, aspect="auto", interpolation="nearest")
    ax.set_yticks(np.arange(0, 20, 5))
    ax.set_yticklabels(np.arange(2007, 2027, 5))
    ax.set_title("eros Erosion Possible? yellow=yes")
    add_month_labels(ax)
    ax.grid(True)

    # Plot var1 from command line
    ax1 = fig.add_axes((0.05, 0.05, XWIDTH, 0.23))
    ax1.set_title(VARNAMES.get(var1, var1))
    ax1.set_ylabel(var1)
    for yr in range(2007, 2027):
        yeardf = dailydf[dailydf.index.year == yr]
        ax1.scatter(
            yeardf["doy"],
            yeardf[var1].to_numpy(),
        )
    add_month_labels(ax1)
    ax1.grid(True)

    # Plot var2 from command line
    ax1 = fig.add_axes((0.35, 0.05, XWIDTH, 0.23))
    ax1.set_title(VARNAMES.get(var2, var2))
    ax1.set_ylabel(var2)
    for yr in range(2007, 2027):
        yeardf = dailydf[dailydf.index.year == yr]
        ax1.scatter(
            yeardf["doy"],
            yeardf[var2].to_numpy(),
        )
    add_month_labels(ax1)
    ax1.grid(True)

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
