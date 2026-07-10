"""Proctor the WEPS runs for sensitivity work."""

import glob
import os
import shutil
import subprocess
import tempfile
from itertools import product
from multiprocessing import Pool

import click
import numpy as np
import pandas as pd
from dailyerosion.reference import KG_M2_TO_TON_ACRE
from pydantic import BaseModel
from tqdm import tqdm

YEARS = 20.0
MAN_META = {
    "070102020605_9.man": {
        "landuse": "CBCBCCCBCCCBCWPCCCCC",
        "tillage_code": 5,
    },
    "090203090201_758.man": {
        "landuse": "WBWBWCTRBBPBTTTTBTTB",
        "tillage_code": 1,
    },
    "101702031502_59.man": {
        "landuse": "BCBCBCBCBBBCBCPCBCCB",
        "tillage_code": 1,
    },
    "corn_soybean_1NoTill.man": {
        "huc12": "-",
        "fpath": "-",
        "landuse": "CBCBCBCBCBCBCBCBCBCB",
        "tillage_code": 1,
    },
    "corn_soybean_3high_mulch.man": {
        "huc12": "-",
        "fpath": "-",
        "landuse": "CBCBCBCBCBCBCBCBCBCB",
        "tillage_code": 3,
    },
    "corn_soybean_5lowmulch.man": {
        "huc12": "-",
        "fpath": "-",
        "landuse": "CBCBCBCBCBCBCBCBCBCB",
        "tillage_code": 5,
    },
    "corn_soybean_2very_high_mulch.man": {
        "huc12": "-",
        "fpath": "-",
        "landuse": "CBCBCBCBCBCBCBCBCBCB",
        "tillage_code": 2,
    },
    "corn_soybean_4medium_mulch.man": {
        "huc12": "-",
        "fpath": "-",
        "landuse": "CBCBCBCBCBCBCBCBCBCB",
        "tillage_code": 4,
    },
    "corn_soybean_6_FallMoldboard.man": {
        "huc12": "-",
        "fpath": "-",
        "landuse": "CBCBCBCBCBCBCBCBCBCB",
        "tillage_code": 6,
    },
}


class WEPSRun(BaseModel):
    """A WEPS run."""

    climate_file: str
    wind_file: str
    soil_file: str
    man_file: str


def add_management_meta(man_file: str) -> dict:
    """Add management metadata to the result dict."""
    meta = MAN_META[man_file]
    if "huc12" not in meta:
        huc12, fpath = man_file.split(".")[0].split("_")
    else:
        huc12 = meta["huc12"]
        fpath = meta["fpath"]
    return {
        "tillage_code": MAN_META[man_file]["tillage_code"],
        "landuse": MAN_META[man_file]["landuse"],
        "huc12": huc12,
        "fpath": fpath,
    }


def add_soil_meta(soil_file: str) -> dict:
    """Figure out some soil metadata."""
    with open(soil_file) as fh:
        lines = fh.readlines()
    return {
        "sand": lines[29].split()[0],
        "silt": lines[31].split()[1],
        "clay": lines[33].split()[2],
    }


def make_run(runopts: WEPSRun) -> dict:
    """Run WEPS and generate a dict result payload."""
    with open("../weps.run") as fh:
        lines = fh.readlines()
    # Replace the lines in the weps.run file with the runopts values
    # avert your eyes here, for now
    lines[35] = f"{runopts.climate_file}\n"
    shutil.copyfile(
        f"../../climate_files/{runopts.climate_file}", runopts.climate_file
    )
    lines[37] = f"{runopts.wind_file}\n"
    shutil.copyfile(f"../../wind_files/{runopts.wind_file}", runopts.wind_file)
    lines[41] = f"{runopts.soil_file}\n"
    shutil.copyfile(f"../../soil_files/{runopts.soil_file}", runopts.soil_file)
    lines[43] = f"{runopts.man_file}\n"
    shutil.copyfile(f"../../man_files/{runopts.man_file}", runopts.man_file)
    with open("weps.run", "w") as fh:
        fh.writelines(lines)
    # Run WEPS
    cmd = [
        "/opt/dep/bin/weps_dep",
        "-c0",  # no soil conditioning output
        "-E1",  # Run WEPS erosion, needs to be on always for -o to work
        "-e0",  # Don't create all sweep files
        "-H0",  # No heartbeat output
        "-I1",  # Run the given management cycles, TODO
        "-n0",  # Don't create new input files
        "-t0",  # No confidence interval reported
        "-T0",  # No deep furrow effect
        "-W1",  # simple runoff method, perf
        "-u0",  # No resurfacing of buried roots, perf opt?
    ]
    subprocess.run(
        cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    # Read the results from the output files
    data = np.loadtxt("plot.out", skiprows=1)
    with open("plot.out") as fh:
        names = [
            x.strip() for x in fh.read(1000).split("\n")[0][2:].split("|")
        ]
    dailydf = pd.DataFrame(data, columns=names)
    result = {
        "man_file": runopts.man_file,
        "climate_file": runopts.climate_file,
        "wind_file": runopts.wind_file,
        "soil_file": runopts.soil_file,
        "erosion_tayr": (
            round(
                dailydf["tot_loss"].abs().sum() * KG_M2_TO_TON_ACRE / YEARS, 4
            )
        ),
    }
    result.update(add_management_meta(runopts.man_file))
    result.update(add_soil_meta(runopts.soil_file))
    return result


def set_to_rundir():
    """Move my working directory to a temporary directory for the run."""
    tmpdir = tempfile.mkdtemp(dir="rundir")
    os.chdir(tmpdir)


@click.command()
@click.option("--workers", type=int, default=4)
def main(workers: int):
    """Go Main Go."""
    os.makedirs("rundir", exist_ok=True)

    clifiles = glob.glob("climate_files/*")
    windfiles = glob.glob("wind_files/*")
    soilfiles = glob.glob("soil_files/*")
    manfiles = list(MAN_META.keys())

    pool = Pool(workers, initializer=set_to_rundir)

    results = []
    jobs = product(clifiles, windfiles, soilfiles, manfiles)
    progress = tqdm(
        total=len(clifiles) * len(windfiles) * len(soilfiles) * len(manfiles)
    )
    for result in pool.imap_unordered(
        make_run,
        (
            WEPSRun(
                climate_file=os.path.basename(climate_file),
                wind_file=os.path.basename(wind_file),
                soil_file=os.path.basename(soil_file),
                man_file=os.path.basename(man_file),
            )
            for climate_file, wind_file, soil_file, man_file in jobs
        ),
    ):
        results.append(result)
        progress.update(1)

    # results = [r.get() for r in results]
    pool.close()
    pool.join()
    pd.DataFrame(results).to_csv("results.csv", index=False)

    # If we made it this far, it is probably OK to blow out the rundir
    shutil.rmtree("rundir")


if __name__ == "__main__":
    main()
