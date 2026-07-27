"""Run things for sweep."""

import subprocess
from pathlib import Path

import click
import numpy as np
import pandas as pd
from dailyerosion.reference import KG_M2_TO_TON_ACRE
from lxml import etree
from matplotlib.colors import BoundaryNorm
from pyiem.plot import figure_axes, get_cmap
from tqdm import tqdm


@click.command()
@click.option(
    "--fn",
    required=True,
)
def main(fn: str):
    """Go Main Go."""
    sweepin = Path(fn)

    # Parse sweepin
    tree = etree.parse(str(sweepin))
    root = tree.getroot()
    # Figure out the treatment filename
    treatfn = root.find("./SCI_Subregions/SCI_Subregion/SCI_treat").text
    ttree = etree.parse(treatfn)
    troot = ttree.getroot()
    tnode = troot.find("./SCI_BiomassFlatCover")

    biomass_values = np.arange(0, 1.01, 0.01)

    results = []

    for value in tqdm(biomass_values):
        tnode.text = f"{value:.2f}"
        ttree.write(
            treatfn,
            encoding="ISO-8859-1",
            xml_declaration=True,
            doctype='<!DOCTYPE TreatmentData SYSTEM "treatment.dtd">',
            pretty_print=True,
        )
        subprocess.run(
            ["/opt/dep/bin/sweep_dep", f"-i{fn}", "-Erod"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        # Le Sigh
        with open(f"{fn.replace('.sweep', '')}.erod") as fh:
            loss = float(fh.readlines()[0].split()[0]) * KG_M2_TO_TON_ACRE
        results.append(
            {
                "erosion_ta": loss,
                "biomass": value,
            }
        )

    resultsdf = pd.DataFrame(results)
    print(resultsdf)

    erosion = 0  # tbd
    xaxis = []
    yaxis = []
    (fig, ax) = figure_axes(
        title="SWEPP Sensitivity Wind Speed vs Crop Height",
        subtitle=(
            r"Erosion kg m$^{-2}$, "
            "Crop Height=Varies"
        ),
    )
    cmap = get_cmap("viridis")
    maxval = max(0.04, np.max(erosion))
    levels = np.arange(0, maxval, 0.02)
    levels[0] = 0.001
    cmap.set_under("white")
    norm = BoundaryNorm(levels, cmap.N)

    print("Mean grid value: {:.4f}".format(np.mean(erosion)))
    res = ax.imshow(
        erosion,
        origin="lower",
        cmap=cmap,
        norm=norm,
        interpolation="nearest",
        aspect="auto",
        extent=(xaxis[0], xaxis[-1], yaxis[0], yaxis[-1]),
    )
    cax = fig.add_axes((0.92, 0.1, 0.02, 0.8))
    fig.colorbar(res, cax=cax, extend="both", label="Erosion kg m$^{-2}$")
    ax.set_xlabel("Crop Height (m)")
    ax.set_ylabel("Hourly Wind Speed (m/s)")
    fig.savefig("erosion.png")


if __name__ == "__main__":
    main()
