"""Extract the day to day changes in GMD."""

from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd


def read_gmd() -> pd.DataFrame:
    """Figure out what the plot.out file has."""
    gmd_p_idx = None
    days = []
    gmd_p = []
    with open("plot.out", "r") as plot_file:
        for linenum, line in enumerate(plot_file):
            if linenum == 0:
                colnames = [s.strip() for s in line.strip().split("|")]
                gmd_p_idx = colnames.index("gmd_p")
                continue
            vals = line.strip().split()
            if len(vals) > 10 and gmd_p_idx is not None:
                days.append(
                    date(2000 + int(vals[4]), int(vals[3]), int(vals[2]))
                )
                gmd_p.append(float(vals[gmd_p_idx]))
    return pd.DataFrame(
        {
            "day": days,
            "gmd_p": gmd_p,
        }
    ).set_index("day")


def compute_operations() -> pd.DataFrame:
    """Figure out when operations happened..."""
    with open("weps.run") as fh:
        lines = fh.readlines()
    manfile = lines[43].strip()
    soilfile = lines[41].strip()
    dates = []
    operations = []
    with open(manfile) as fh:
        wantline = None
        for linenum, line in enumerate(fh.readlines()):
            if line.startswith("D "):
                tokens = line.split()[1].split("/")
                dates.append(
                    datetime.strptime(
                        f"20{tokens[2]}/{tokens[1]}/{tokens[0]}", "%Y/%m/%d"
                    ).date()
                )
                wantline = linenum + 1
            elif wantline is not None and linenum == wantline:
                operations.append(line.split(maxsplit=1)[1].strip())
                wantline = None
    opsdf = pd.DataFrame(
        {
            "date": dates,
            "manfile": [manfile] * len(dates),
            "soilfile": [soilfile] * len(dates),
            "operation": operations,
        }
    )
    # Now, the man file is two years and we are currently running ten, so
    # we need to duplicate things.
    newrows = []
    for _, row in opsdf.iterrows():
        dt = row["date"]
        for year_offset in [2, 4, 6, 8]:
            newrows.append(
                {
                    "date": dt.replace(year=dt.year + year_offset),
                    "manfile": row["manfile"],
                    "soilfile": row["soilfile"],
                    "operation": row["operation"],
                }
            )
    opsdf = pd.concat([opsdf, pd.DataFrame(newrows)], ignore_index=True)

    return opsdf


def main():
    """Go Main Go."""
    gmd_df = read_gmd()
    operation_dates = compute_operations()
    results = []
    for _, row in operation_dates.iterrows():
        # Filter out only 03 operations
        if not row["operation"].startswith("03"):
            continue
        results.append(
            {
                "date": row["date"],
                "manfile": row["manfile"],
                "soilfile": row["soilfile"],
                "operation": row["operation"],
                "gmd_p_before": gmd_df.loc[
                    row["date"] - timedelta(days=1), "gmd_p"
                ],
                "gmd_p_after": gmd_df.loc[row["date"], "gmd_p"],
            }
        )
    resultsdf = pd.DataFrame(results)
    csvfn = Path("gmd_changes.csv")
    if csvfn.exists():
        resultsdf = pd.concat(
            [pd.read_csv(csvfn), resultsdf],
            ignore_index=True,
        )
    resultsdf.to_csv("gmd_changes.csv", index=False)


if __name__ == "__main__":
    main()
