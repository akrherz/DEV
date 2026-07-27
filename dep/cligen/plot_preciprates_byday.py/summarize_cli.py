"""Dump some statistics per EDU request.

2008-2020 (inclusive)

• Solar Radiation: Mean
• Maximum Air Temperature: Mean
• Temperature Difference: Mean
• Wind Velocity: Mean

"""

from pathlib import Path

import pandas as pd
from dailyerosion.io.wepp import read_cli
from pyiem.database import get_sqlalchemy_conn, sql_helper
from tqdm import tqdm


def summarize_cli(clifn: Path) -> dict:
    """Do the work and return the data."""
    clidf = read_cli(clifn)
    filtered = clidf.loc[pd.Timestamp(2008, 1, 1) : pd.Timestamp(2020, 12, 31)]
    return {
        "rad": filtered["rad"].mean(),
        "tmax": filtered["tmax"].mean(),
        "tdiff": (filtered["tmax"] - filtered["tmin"]).mean(),
        "wind": filtered["wvl"].mean(),
    }


def main():
    """Go Main Go."""
    # Build the cross reference of climatefiles and flowpaths
    with get_sqlalchemy_conn("idep") as conn:
        flowpathdf = pd.read_sql(
            sql_helper("""
            SELECT f.fid, c.filepath, f.huc_12, f.fpath,
            0. as avg_srad_langleys,
            0. as avg_tmax_c,
            0. as avg_tdiff_c,
            0. as avg_windspeed_mps
            from flowpaths f, climate_files c where
            f.climate_file_id = c.id and f.scenario = 0
            """),
            conn,
            index_col="fid",
        )
    progress = tqdm(flowpathdf.iterrows(), total=len(flowpathdf))
    for idx, row in progress:
        progress.set_description(row["filepath"])
        clifn = Path(row["filepath"])
        if not clifn.is_file():
            continue
        data = summarize_cli(clifn)
        flowpathdf.at[idx, "avg_srad_langleys"] = data["rad"]
        flowpathdf.at[idx, "avg_tmax_c"] = data["tmax"]
        flowpathdf.at[idx, "avg_tdiff_c"] = data["tdiff"]
        flowpathdf.at[idx, "avg_windspeed_mps"] = data["wind"]

    flowpathdf.to_csv(
        "cli_summary_2008_2020.csv", float_format="%.2f", index=False
    )


if __name__ == "__main__":
    main()
