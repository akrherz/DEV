"""Dump sweepin variables to file for further analysis."""

from datetime import datetime
from pathlib import Path

import click
import numpy as np
import pandas as pd
from lxml import etree
from pyiem.database import get_sqlalchemy_conn, sql_helper
from tqdm import tqdm


def process_sweepin(sweepin: Path, cropinfo: pd.Series) -> dict:
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

    treat_nodes = troot.findall("./SCI_brcdInputs/SCI_brcdInput/SCI_brcdRsai")
    if not treat_nodes:
        rsai = None
    else:
        rsai = float(treat_nodes[0].text)
        if rsai > 1:
            print(treatfn)

    return {
        "huc12": huc12,
        "fpath": fpath,
        "prev_crop": cropinfo["prev_crop"],
        "cur_crop": cropinfo["cur_crop"],
        "prev_mgmt": cropinfo["prev_mgmt"],
        "cur_mgmt": cropinfo["cur_mgmt"],
        "sci_biomass_flat_cover": float(tnode.text),
        "max_wind_speed_mps": np.max(obs),
        "avg_wind_speed_mps": np.mean(obs),
        "sci_watercontent": float(soil_nodes[0].text),
        "brcd_rsai": rsai,
    }


@click.command()
@click.option(
    "--date",
    "dt",
    type=click.DateTime(),
    required=True,
    help="The date the sweepin files are valid for, needed to get crop.",
)
def main(dt: datetime):
    """Go Main Go."""
    if dt.year == 2007:
        raise click.BadArgumentUsage("Year 2007 is not supported.")
    with get_sqlalchemy_conn("dep") as conn:
        cropsdf = pd.read_sql(
            sql_helper("""
            select huc12_code || '_' || huc12_fpath_num as key,
            substr(landuse, :previdx, 1) as prev_crop,
            substr(landuse, :curidx, 1) as cur_crop,
            substr(management, :previdx, 1) as prev_mgmt,
            substr(management, :curidx, 1) as cur_mgmt
            from ofe_view where ofe = 1
            """),
            conn,
            index_col="key",
            params={
                "previdx": dt.year - 2007,
                "curidx": dt.year - 2007 + 1,
            },
        )
    results = []
    progress = tqdm(cropsdf.iterrows(), total=len(cropsdf.index))
    hits = 0
    for key, row in progress:
        huc12, _fpath = key.split("_")
        sweep_path = (
            Path("/i/0/sweepin_260512")
            / f"{huc12[:8]}"
            / f"{huc12[8:]}"
            / f"{key}.sweep"
        )
        if not sweep_path.exists():
            continue
        progress.set_description(f"{hits}")
        hits += 1
        results.append(process_sweepin(sweep_path, row))

    pd.DataFrame(results).to_csv("sweepin_vars.csv", index=False)


if __name__ == "__main__":
    main()
