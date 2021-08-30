"""HRRR reflectivity frequency."""
import datetime
import os

from pyiem.plot import MapPlot
from pyiem.util import utc, logger
import requests
import pygrib
import pandas as pd
from PIL import Image
import numpy as np
import matplotlib.colors as mpcolors

LOG = logger()
FONTSIZE = 32


def dl(valid):
    """Get me files"""
    for hr in range(-15, 0):
        ts = valid + datetime.timedelta(hours=hr)
        fn = ts.strftime("/tmp/hrrr.ref.%Y%m%d%H00.grib2")
        if os.path.isfile(fn):
            continue
        uri = ts.strftime(
            "http://mesonet.agron.iastate.edu/archive/data/"
            "%Y/%m/%d/model/hrrr/%H/hrrr.t%Hz.refd.grib2"
        )
        try:
            with open(fn, "wb") as fh:
                fh.write(requests.get(uri).content)
        except Exception as exp:
            print(uri)
            print(exp)


def compute(valid):
    """Get me files"""
    lats = None

    ramp = pd.read_csv(
        "/home/akrherz/projects/pyIEM/src/pyiem/data/ramps/"
        "composite_n0q.txt"
    )
    cmap = mpcolors.ListedColormap(ramp[["r", "g", "b"]].to_numpy() / 256)
    cmap.set_under((0, 0, 0, 0))

    for hr in range(-15, 0):
        ts = valid + datetime.timedelta(hours=hr)
        fn = ts.strftime("/tmp/hrrr.ref.%Y%m%d%H00.grib2")
        if not os.path.isfile(fn):
            print("Missing %s" % (fn,))
            continue

        grbs = pygrib.open(fn)
        try:
            gs = grbs.select(level=1000, forecastTime=(-1 * hr * 60))
        except ValueError:
            print("Fail %s" % (fn,))
            continue
        ref = gs[0]["values"]
        # HRRR anything below -9 is missing
        ref = np.where(ref < -9, -100, ref)
        if lats is None:
            lats, lons = gs[0].latlons()

        m = MapPlot(
            sector="iowa",
            nologo=True,
            continentalcolor="white",
        )
        m.fig.text(
            0.1,
            0.92,
            f"HRRR Init:{ts:%d/%H} Forecast Hour:{hr * -1}",
            fontsize=FONTSIZE,
        )
        m.pcolormesh(
            lons,
            lats,
            ref,
            ramp["value"].values,
            cmap=cmap,
            units="% of runs",
            clip_on=False,
            clevstride=20,
        )
        m.drawcounties()
        m.postprocess(filename=f"F{hr * -1}.png")
        m.close()


def plot(valid):
    """Generate something simple."""
    mp = MapPlot(
        sector="iowa",
        nologo=True,
    )
    mp.fig.text(
        0.05,
        0.92,
        "NEXRAD MOSAIC %s UTC" % (valid.strftime("%Y-%m-%d %H:%M"),),
        fontsize=FONTSIZE,
        bbox=dict(color="white"),
    )
    mp.overlay_nexrad(valid)
    mp.drawcounties()
    mp.postprocess(filename="F0.png")
    mp.close()


def stitch():
    """Put 16 images together."""
    width = 512
    height = 386
    out = Image.new("RGB", (width * 4, height * 4))
    # 4x4 is 480x270
    for i in range(16):
        row = i // 4
        col = i % 4
        fn = f"F{i}.png"
        if not os.path.isfile(fn):
            LOG.info("Missing %s", fn)
            continue
        frame = Image.open(fn).resize((512, 386))
        out.paste(frame, (width * col, height * row))
        del frame
    out.save("ensemble.png")
    del out


def main():
    """Go Main Go."""
    valid = utc(2021, 8, 26, 14)
    dl(valid)
    plot(valid)
    compute(valid)
    stitch()


if __name__ == "__main__":
    main()
