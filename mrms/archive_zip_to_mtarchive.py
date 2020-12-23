"""Extract what we want to long term archive."""
# stdlib
from datetime import datetime
import sys
import os
import zipfile

CONUS_FIELDS = (
    "GaugeCorr_QPE_01H,GaugeCorr_QPE_24H,GaugeCorr_QPE_72H,MESH,"
    "MountainMapper_QPE_01H,MountainMapper_QPE_03H,MountainMapper_QPE_06H,"
    "MountainMapper_QPE_12H,MountainMapper_QPE_24H,MountainMapper_QPE_48H,"
    "MountainMapper_QPE_72H,PrecipFlag,PrecipRate,RadarOnly_QPE_01H,"
    "RadarOnly_QPE_24H,RadarOnly_QPE_72H,RadarQualityIndex,"
    "RotationTrack1440min,SeamlessHSR"
).split(",")


def main(argv):
    """Go Main Go."""
    zfp = zipfile.ZipFile(argv[1], "r")
    for name in zfp.namelist():
        tokens = name.split("/")
        if tokens[1] not in ["FLASH", "CONUS"]:
            continue
        if tokens[1] == "CONUS" and tokens[2] not in CONUS_FIELDS:
            continue
        if not tokens[-1].endswith(".gz"):
            continue
        # OK, we have something we want.
        valid = datetime.strptime(tokens[0], "%Y%m%d%H%M")
        finaldir = valid.strftime("/isu/mtarchive/data/%Y/%m/%d/mrms/ncep/")
        if tokens[1] == "FLASH":
            finaldir += "FLASH/" + tokens[2].replace("FLASH_", "") + "/"
        else:
            finaldir += tokens[2] + "/"
        if not os.path.isdir(finaldir):
            os.makedirs(finaldir)
        # Munge the filename
        fn = tokens[-1].replace("MRMS_", "").replace("FLASH_", "")
        print(f"{name} -> {finaldir}{fn}")
        with open(f"{finaldir}{fn}", "wb") as fh:
            fh.write(zfp.read(name))


if __name__ == "__main__":
    main(sys.argv)
