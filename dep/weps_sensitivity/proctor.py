"""Proctor the WEPS runs for sensitivity work."""

import glob
import os
import shutil
import subprocess
import tempfile
from functools import lru_cache
from itertools import product
from multiprocessing import Pool
from typing import Annotated

import click
import numpy as np
import pandas as pd
from dailyerosion.io.wepp import read_cli
from dailyerosion.reference import KG_M2_TO_TON_ACRE
from jinja2 import Template
from pydantic import BaseModel, Field
from tqdm import tqdm

with open("weps_run.j2") as fh:
    WEPS_RUN_TEMPLATE = Template(fh.read())
TBD = -99
YEARS = 20.0
DATE_AXIS = pd.date_range("2007/01/01", "2026/12/31")
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
    region_angle: Annotated[
        int,
        Field(ge=0, lt=360),
    ]
    field_xlength: Annotated[
        float,
        Field(gt=0),
    ]
    field_ylength: Annotated[
        float,
        Field(gt=0),
    ]
    tillage_direction: Annotated[
        int,
        Field(ge=0, lt=360),
    ]


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
        "silt": lines[31].split()[0],
        "clay": lines[33].split()[0],
        "om": lines[50].split()[0],
        "caco3": lines[54].split()[0],
        "gmd": lines[61].split()[0],
        "min_agg_sz": lines[67].split()[0],
        "max_agg_sz": lines[65].split()[0],
        "agg_stability": lines[71].split()[0],
        "wilting_point": lines[106].split()[0],
        "field_capacity": lines[104].split()[0],
        "random_roughness": lines[87].split()[0],
        "surface_crust_fract": lines[80].split()[0],
        "crust_thickness": lines[74].split()[0],
        "slope_gradient": lines[14].split()[0],
        "bulk_density": lines[48].split()[0],
    }


@lru_cache()
def add_cli_meta(climate_file: str) -> dict:
    """Compute some required metadata from the CLI file."""
    clidf = read_cli(climate_file)
    clidf["threeday_precip"] = clidf["pcpn"].rolling(3).sum()
    spring_ddd = (
        clidf[(clidf.index.month >= 3) & (clidf.index.month <= 5)][
            "threeday_precip"
        ]
        < 0.01
    ).sum() / YEARS
    fall_ddd = (
        clidf[(clidf.index.month >= 9)]["threeday_precip"] < 0.01
    ).sum() / YEARS
    return {
        "spring_dry_duration_days": spring_ddd,
        "fall_dry_duration_days": fall_ddd,
        "spring_prevailing_drct": TBD,
        "fall_prevailing_drct": TBD,
    }


@lru_cache()
def add_wind_meta(wind_file: str) -> dict:
    """Compute interesting things with the wind file."""
    data = np.loadtxt(wind_file, skiprows=7)
    dailydf = pd.DataFrame(
        {"dailymax": np.max(data[:, 4:], axis=1)}, index=DATE_AXIS
    )
    springdf = dailydf[(dailydf.index.month >= 3) & (dailydf.index.month <= 5)]
    # A bit more than fall here, but this was my guidance
    falldf = dailydf[(dailydf.index.month >= 9)]
    return {
        "avg_spring_days_gt_15": (springdf["dailymax"] > 15).sum() / YEARS,
        "spring_p95": np.percentile(springdf["dailymax"], 95),
        "avg_fall_days_gt_15": (falldf["dailymax"] > 15).sum() / YEARS,
        "fall_p95": np.percentile(falldf["dailymax"], 95),
        "wind_mean": np.mean(data[:, 4:]),
        "wind_daily_max_mean": dailydf["dailymax"].mean(),
    }


def add_plot_meta() -> dict:
    """Harvest things from the plot.out file."""
    # Read the results from the output files
    data = np.loadtxt("plot.out", skiprows=1)
    with open("plot.out") as fh:
        names = [
            x.strip() for x in fh.read(1000).split("\n")[0][2:].split("|")
        ]
    dailydf = pd.DataFrame(data, columns=names, index=DATE_AXIS)
    springdf = dailydf[(dailydf.index.month >= 3) & (dailydf.index.month <= 5)]
    falldf = dailydf[(dailydf.index.month >= 9)]

    return {
        "spring_soilmoist": TBD,
        "spring_t_flat_cov": springdf["t_flat_cov"].mean(),
        "spring_bio_lai": springdf["bio_lai"].mean(),
        "spring_post_tillage_roughness": TBD,
        "fall_soilmoist": TBD,
        "fall_t_flat_cov": falldf["t_flat_cov"].mean(),
        "fall_bio_lai": falldf["bio_lai"].mean(),
        "fall_post_tillage_roughness": TBD,
        "erosion_tayr": (
            round(
                dailydf["tot_loss"].abs().sum() * KG_M2_TO_TON_ACRE / YEARS, 4
            )
        ),
        "spring_erosion_tayr": (
            round(
                springdf["tot_loss"].abs().sum() * KG_M2_TO_TON_ACRE / YEARS, 4
            )
        ),
        "fall_erosion_tayr": (
            round(
                falldf["tot_loss"].abs().sum() * KG_M2_TO_TON_ACRE / YEARS, 4
            )
        ),
        "suspension_tayr": (
            round(dailydf["suspen"].abs().sum() * KG_M2_TO_TON_ACRE / YEARS, 4)
        ),
        "spring_suspension_tayr": (
            round(
                springdf["suspen"].abs().sum() * KG_M2_TO_TON_ACRE / YEARS, 4
            )
        ),
        "fall_suspension_tayr": (
            round(falldf["suspen"].abs().sum() * KG_M2_TO_TON_ACRE / YEARS, 4)
        ),
        "pm10_tayr": (
            round(dailydf["pm10"].abs().sum() * KG_M2_TO_TON_ACRE / YEARS, 4)
        ),
        "spring_pm10_tayr": (
            round(springdf["pm10"].abs().sum() * KG_M2_TO_TON_ACRE / YEARS, 4)
        ),
        "fall_pm10_tayr": (
            round(falldf["pm10"].abs().sum() * KG_M2_TO_TON_ACRE / YEARS, 4)
        ),
        "saltation_tayr": TBD,
        "spring_saltation_tayr": TBD,
        "fall_saltation_tayr": TBD,
    }


def make_run(runopts: WEPSRun) -> dict:
    """Run WEPS and generate a dict result payload."""
    with open("weps.run", "w") as fh:
        fh.write(
            WEPS_RUN_TEMPLATE.render(
                {
                    "climate_file": runopts.climate_file,
                    "wind_file": runopts.wind_file,
                    "soil_file": runopts.soil_file,
                    "man_file": runopts.man_file,
                    "region_angle": runopts.region_angle,
                    "field_xlength": runopts.field_xlength,
                    "field_ylength": runopts.field_ylength,
                }
            )
        )
    shutil.copyfile(
        f"../../climate_files/{runopts.climate_file}", runopts.climate_file
    )
    shutil.copyfile(f"../../wind_files/{runopts.wind_file}", runopts.wind_file)
    shutil.copyfile(f"../../soil_files/{runopts.soil_file}", runopts.soil_file)
    shutil.copyfile(f"../../man_files/{runopts.man_file}", runopts.man_file)
    with open(runopts.man_file) as fh:
        lines = fh.readlines()
    for linenum, line in enumerate(lines):
        if line.startswith("O 03"):
            tokens = lines[linenum + 1].split()
            tokens[4] = f"{runopts.tillage_direction:.1f}"
            lines[linenum + 1] = " ".join(tokens) + "\n"
    with open(runopts.man_file, "w") as fh:
        fh.write("".join(lines))
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
    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        print(f"Run failure for {runopts}")
        return None
    result = {
        "man_file": runopts.man_file,
        "climate_file": runopts.climate_file,
        "wind_file": runopts.wind_file,
        "soil_file": runopts.soil_file,
        "field_width": 714.08,
        "field_length": 714.08,
        "annual_stir": TBD,
        "tillage_direction": runopts.tillage_direction,
        "decomposition_rate": TBD,
        "ridge_height": TBD,
        "ridge_spacing": TBD,
        "region_angle": runopts.region_angle,
        "windbreak_height": 0,
        "barrier_porosity": 0,
        "barrier_orientation": 0,
    }
    result.update(add_plot_meta())
    result.update(add_management_meta(runopts.man_file))
    result.update(add_soil_meta(runopts.soil_file))
    result.update(add_wind_meta(runopts.wind_file))
    result.update(add_cli_meta(runopts.climate_file))
    return result


def set_to_rundir():
    """Move my working directory to a temporary directory for the run."""
    tmpdir = tempfile.mkdtemp(dir="rundir")
    os.chdir(tmpdir)


@click.command()
@click.option("--workers", type=int, required=True)
def main(workers: int):
    """Go Main Go."""
    os.makedirs("rundir", exist_ok=True)

    clifiles = glob.glob("climate_files/*")
    windfiles = glob.glob("wind_files/*")
    soilfiles = glob.glob("soil_files/*")
    manfiles = list(MAN_META.keys())
    region_angles = [0, 90]
    tillage_direction = [0, 90]

    pool = Pool(workers, initializer=set_to_rundir)

    results = []
    jobs = product(
        clifiles,
        windfiles,
        soilfiles,
        manfiles,
        region_angles,
        tillage_direction,
    )
    progress = tqdm(
        total=len(clifiles)
        * len(windfiles)
        * len(soilfiles)
        * len(manfiles)
        * len(region_angles)
        * len(tillage_direction)
    )
    for result in pool.imap_unordered(
        make_run,
        (
            WEPSRun(
                climate_file=os.path.basename(climate_file),
                wind_file=os.path.basename(wind_file),
                soil_file=os.path.basename(soil_file),
                man_file=os.path.basename(man_file),
                region_angle=region_angle,
                tillage_direction=tillage_direction,
                field_xlength=100,
                field_ylength=200,
            )
            for (
                climate_file,
                wind_file,
                soil_file,
                man_file,
                region_angle,
                tillage_direction,
            ) in jobs
        ),
    ):
        if result:
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
