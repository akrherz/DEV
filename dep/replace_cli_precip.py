"""Forklift a CLI file's precip data."""
from datetime import date

import pytz
import pandas as pd

print("DOUBLE CHECK THE TIMING!  30 MIN vs 1 HOUR....")


def compute_breakpoints(df):
    """Turn a day's worth of data into breakpoints."""
    if df["precip_mm"].sum() < 0.25:
        return []
    curval = 0
    res = []
    # Assume we have 48 items per day, close enough
    for idx, val in enumerate(df["precip_mm"].cumsum()):
        if idx >= 24:  # fall leap hour
            continue
        if val > curval:
            hr = idx // 1
            mi = ".00"  # if idx % 2 == 0 else ".50"
            res.append(f"{hr}{mi} {val:.2f}")
            curval = val
    if len(res) == 1:
        res.append(f"23.75 {curval:.2f}")
    return res


def do(scenario, huc12):
    """Make the replacement."""
    obs = pd.read_csv(f"{huc12}.csv")
    # Timestamps are in UTC
    obs["valid"] = (
        pd.to_datetime(obs["valid"])
        .dt.tz_localize(pytz.UTC)
        .dt.tz_convert(pytz.timezone("America/Chicago"))
    )
    obs["date"] = obs["valid"].dt.date
    clifn = f"/i/{scenario}/cli/{huc12}.cli"
    with open(f"{clifn}.new", "w") as fh:
        lines = open(clifn).readlines()
        linenum = 0
        while linenum < len(lines):
            if linenum < 15:
                fh.write(lines[linenum])
                linenum += 1
                continue
            tokens = lines[linenum].strip().split("\t")
            breakpoints = int(tokens[3])
            valid = date(int(tokens[2]), int(tokens[1]), int(tokens[0]))
            # Skip reader ahead
            linenum += breakpoints + 1
            bpdata = compute_breakpoints(obs[obs["date"] == valid])
            tokens[3] = str(len(bpdata))
            fh.write("\t".join(tokens) + "\n")
            for bp in bpdata:
                fh.write(f"{bp}\n")


def main():
    """Go Main Go."""
    scenario = 141
    hucs = [x.strip() for x in open("myhucs.txt")]
    for huc12 in hucs:
        do(scenario, huc12)


if __name__ == "__main__":
    main()
