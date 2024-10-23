"""For exerimenting with a fixed slope."""

import sys

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.util import logger
from sqlalchemy import text
from tqdm import tqdm

LOG = logger()


def edit_prj(row):
    """Edit the prj file."""
    prjfn = (
        f"/i/0/prj/{row['huc_12'][:8]}/{row['huc_12'][8:]}/"
        f"{row['huc_12']}_{row['fpath']}.prj"
    )
    with open(prjfn) as fh:
        lines = fh.readlines()
    if not lines[11].startswith("Profile"):
        LOG.warning("%s does not have Profile set, abort", prjfn)
        sys.exit()
    lines[10] = f"Length = {row['real_length']:.4f}\n"
    lines[14] = f"  3 {row['real_length']:.4f}\n"
    bs = f"{row['bulk_slope']:0.6f}"
    lines[15] = f"  0.00, {bs} 0.50, {bs} 1.00, {bs}\n"
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
        edit_prj(row)


if __name__ == "__main__":
    main()
