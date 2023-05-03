"""
Copy over the DEP files for the Strips sites.
"""
import glob
import os
import shutil
import subprocess

from pyiem.util import get_dbconn

XREF = {
    "ARM": ["102400030406", "5"],
    "MCN": ["102802010203", "239"],
    "RHO": ["070801050702", "72"],
    "SPIRIT": ["102300030203", "199"],
    "WHI": ["071000070104", "256"],
    "WOR": ["070801050307", "249"],
}


def main():
    """Go main."""
    os.makedirs("/tmp/strips_files", exist_ok=True)
    pgconn = get_dbconn("idep")
    cursor = pgconn.cursor()
    for sid, (huc12, fp) in XREF.items():
        for cat in ["man", "slp", "sol", "prj"]:
            shutil.copyfile(
                f"/i/0/{cat}/{huc12[:8]}/{huc12[8:]}/{huc12}_{fp}.{cat}",
                f"/tmp/strips_files/{sid}.{cat}",
            )
        for fn in glob.glob(f"/i/0/rot/{huc12[:8]}/{huc12[8:]}/{huc12}_{fp}*"):
            shutil.copyfile(fn, f"/tmp/strips_files/{sid}_{fn[-5:]}")
        cursor.execute(
            """
            SELECT climate_file from flowpaths where huc_12 = %s and
            fpath = %s and scenario = 0
            """,
            (huc12, fp),
        )
        clifn = cursor.fetchone()[0]
        subprocess.call(
            ["scp", f"mesonet@iem12:{clifn}", f"/tmp/strips_files/{sid}.cli"]
        )


if __name__ == "__main__":
    main()
