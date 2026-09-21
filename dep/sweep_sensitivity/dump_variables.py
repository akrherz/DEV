"""Dump sweepin variables to file for further analysis."""

import os
from pathlib import Path

import click
import numpy as np
import pandas as pd
from lxml import etree


def process_sweepin(sweepin: Path) -> dict:
    """Do the processing work."""
    (huc12, fpath) = sweepin.stem.split("_", 1)

    # sweepin file work
    tree = etree.parse(sweepin)
    root = tree.getroot()
    obs = np.zeros((24))
    wind_nodes = root.findall("./SCI_WindSpeeds/SCI_WindSpeed")
    for i, node in enumerate(wind_nodes):
        obs[i] = float(node.text)

    # Treatment file work
    soilfn = sweepin.with_name(sweepin.stem + ".soilsurf")
    stree = etree.parse(soilfn)
    sroot = stree.getroot()
    soil_nodes = sroot.findall("./SCI_SoilLays/SCI_SoilLay/SCI_WaterContent")

    # Treatment file work
    treatfn = sweepin.with_name(sweepin.stem + ".treat")
    ttree = etree.parse(treatfn)
    troot = ttree.getroot()
    tnode = troot.find("./SCI_BiomassFlatCover")

    return {
        "huc12": huc12,
        "fpath": fpath,
        "sci_biomass_flat_cover": float(tnode.text),
        "max_wind_speed_mps": np.max(obs),
        "avg_wind_speed_mps": np.mean(obs),
        "sci_watercontent": float(soil_nodes[0].text),
    }


@click.command()
def main():
    """Go Main Go."""
    results = []
    for rootdir, _dirs, files in os.walk("/i/0/sweepin"):
        for fn in files:
            if not fn.endswith(".sweep"):
                continue
            sweepin = Path(os.path.join(rootdir, fn))
            results.append(process_sweepin(sweepin))

    pd.DataFrame(results).to_csv("sweepin_vars.csv", index=False)


if __name__ == "__main__":
    main()
