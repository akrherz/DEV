"""Look at the soil files we carry and sample out some for range of sand."""

import glob
import shutil
from pathlib import Path

from proctor import add_soil_meta


def main():
    """Go Main Go."""
    # Try to get sand values modulo 2, so to yield 50 of 'em
    slots = [False] * 50
    for fn in glob.glob("/i/0/weps_soil_fy2024/*"):
        try:
            meta = add_soil_meta(fn)
        except Exception:
            print("BAD-> ", fn)
            continue
        sand = int(float(meta["sand"]) * 100.0) // 2 - 1
        if slots[sand]:
            continue
        slots[sand] = True
        shutil.copyfile(fn, Path("soil_files") / Path(fn).name)


if __name__ == "__main__":
    main()
