"""HRRR reflectivity frequency."""
import datetime
import os

from pyiem.plot import MapPlot
from pyiem.util import utc
import requests
import pytz
import pygrib
import numpy as np


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
    prob = None
    for hr in range(-15, 0):
        ts = valid + datetime.timedelta(hours=hr)
        fn = ts.strftime("/tmp/hrrr.ref.%Y%m%d%H00.grib2")
        if not os.path.isfile(fn):
            print("Missing %s" % (fn,))
            continue

        grbs = pygrib.open(fn)
        try:
            gs = grbs.select(level=1000, forecastTime=(-1 * hr * 60))
        except KeyError:
            print("Fail %s" % (fn,))
            continue
        ref = gs[0]["values"]
        # ref = generic_filter(gs[0]['values'], np.max, size=10)
        if prob is None:
            lats, lons = gs[0].latlons()
            prob = np.zeros(np.shape(ref))

        prob = np.where(ref > 29, prob + 1, prob)

    prob = np.ma.array(prob / 15.0 * 100.0)
    prob.mask = np.ma.where(prob < 1, True, False)

    m = MapPlot(
        sector="iowa",
        title="HRRR Composite Forecast 4 PM 14 Sep 2019 30+ dbZ Reflectivity",
        subtitle=("frequency of previous 15 NCEP model runs all valid at %s")
        % (
            valid.astimezone(pytz.timezone("America/Chicago")).strftime(
                "%-d %b %Y %I:%M %p %Z"
            ),
        ),
    )

    m.pcolormesh(
        lons,
        lats,
        prob,
        np.arange(0, 101, 10),
        units="% of runs",
        clip_on=False,
    )
    m.drawcounties()
    m.postprocess(filename="test.png")
    m.close()


def main():
    """Go Main Go."""
    valid = utc(2019, 9, 14, 21)
    dl(valid)
    compute(valid)


if __name__ == "__main__":
    main()
