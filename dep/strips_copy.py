"""
Copy over the DEP files for the Strips sites.
"""

import glob
import os
import shutil
import subprocess

from pyiem.util import get_dbconn

XREF = {
    "ARM_TRT": ["102400030406", "10005"],
    "ARM_CTL": ["102400030602", "10049"],
    "MCN_TRT": ["102802010203", "10120"],
    "MCN_CTL": ["102802010203", "20120"],
    "RHO_TRT": ["070801050702", "10072"],
    "RHO_CTL": ["070801050702", "20072"],
    "SPIRIT_TRT": ["102300030203", "10751"],
    "SPIRIT_CTL": ["102300030203", "10324"],
    "WHI_TRT": ["071000070104", "10249"],
    "WHI_CTL": ["071000070104", "10123"],
    "WOR_TRT": ["070801050307", "10667"],
    "WOR_CTL": ["070801050307", "10073"],
}


def main():
    """Go main."""
    os.makedirs("/tmp/strips_files", exist_ok=True)
    pgconn = get_dbconn("idep")
    cursor = pgconn.cursor()
    for sid, (huc12, fp) in XREF.items():
        for cat in ["man", "slp", "sol", "prj"]:
            shutil.copyfile(
                f"/i/2000/{cat}/{huc12[:8]}/{huc12[8:]}/{huc12}_{fp}.{cat}",
                f"/tmp/strips_files/{sid}.{cat}",
            )
        for fn in glob.glob(
            f"/i/2000/rot/{huc12[:8]}/{huc12[8:]}/{huc12}_{fp}*"
        ):
            shutil.copyfile(fn, f"/tmp/strips_files/{sid}_{fn[-5:]}")
        cursor.execute(
            """
            SELECT climate_file from flowpaths where huc_12 = %s and
            fpath = %s and scenario = 2000
            """,
            (huc12, fp),
        )
        clifn = cursor.fetchone()[0]
        subprocess.call(
            [
                "scp",
                f"mesonet@iem12:{clifn.replace('2000', '0')}",
                f"/tmp/strips_files/{sid}.cli",
            ]
        )


if __name__ == "__main__":
    main()
