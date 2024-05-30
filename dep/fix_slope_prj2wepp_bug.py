"""Fix prj2wepp bug."""

from sqlalchemy import text
from tqdm import tqdm

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.util import logger

LOG = logger()


def edit_slp(row):
    """Edit the prj file."""
    prjfn = (
        f"/i/0/slp/{row['huc_12'][:8]}/{row['huc_12'][8:]}/"
        f"{row['huc_12']}_{row['fpath']}.slp"
    )
    with open(prjfn) as fh:
        lines = fh.readlines()
    hit = False
    for linenum in range(7, 22, 2):
        if linenum >= len(lines):
            break
        if lines[linenum].startswith("3 "):
            lines[linenum] = f"2 {lines[linenum][2:]}"
            nl = lines[linenum + 1]
            lines[linenum + 1] = f"{nl[:20]} {nl[39:]}"
            hit = True
    if not hit:
        return

    with open(prjfn, "w") as fh:
        fh.write("".join(lines))


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("idep") as conn:
        flowpaths = pd.read_sql(
            text("""
            select huc_12, fpath, real_length, bulk_slope from flowpaths
            where scenario = 0
                 """),
            conn,
        )
    for _, row in tqdm(flowpaths.iterrows(), total=len(flowpaths.index)):
        edit_slp(row)


if __name__ == "__main__":
    main()
