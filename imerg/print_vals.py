"""Simple printing of values."""

import datetime

import osgeo.gdal as gdal
import requests


def main():
    """Go Main Go."""
    # Ankeny 41.74373,-93.5909
    y = 900 - 417
    x = 1800 - 936
    sts = datetime.datetime(2018, 6, 30, 22)
    ets = sts + datetime.timedelta(hours=7)
    now = sts
    accum = 0
    while now < ets:
        uri = now.strftime(
            "https://mesonet.agron.iastate.edu/archive/data/%Y/%m/%d/"
            "GIS/imerg/p30m_%Y%m%d%H%M.png"
        )
        req = requests.get(uri)
        with open("/tmp/bah.png", "wb") as fh:
            fh.write(req.content)
        data = gdal.Open("/tmp/bah.png").ReadAsArray()
        localvalid = now - datetime.timedelta(hours=5)
        dt = "%s.%02.0f" % (localvalid.hour, localvalid.minute / 60.0 * 100.0)
        # HACK as all data is below a threshold and need not translated
        accum += data[y, x] * 0.25
        print("%s %.2f" % (dt, accum))

        now += datetime.timedelta(minutes=30)


if __name__ == "__main__":
    main()
