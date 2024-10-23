"""Plot WPC"""

import datetime
import os

import numpy as np
import pygrib
from pyiem.plot import MapPlot
from pyiem.plot.use_agg import plt
from pyiem.util import logger

LOG = logger()


def main():
    """Go Main"""
    sts = datetime.date(2019, 12, 2)
    ets = datetime.date(2019, 9, 14)
    interval = datetime.timedelta(days=-1)
    now = sts
    total = None
    count = 1
    while now > ets:
        fn = now.strftime(
            "/mesonet/ARCHIVE/data/%Y/%m/%d/model/wpc/p168m_%Y%m%d00f168.grb"
        )
        if not os.path.isfile(fn):
            LOG.info("Missing %s", fn)
            now += interval
            continue
        grbs = pygrib.open(fn)
        grb = grbs[1]
        data = grb["values"]
        if total is None:
            total = np.zeros(data.shape)
            lats, lons = grb.latlons()
        grbs.close()
        total = np.where(data < (25.4 * 0.05), total + 1, total)
        LOG.debug("%s min:%s max:%s", now, np.min(total), np.max(total))
        count += 1
        now += interval

    mp = MapPlot(
        sector="conus",
        title=(
            "15 Sep - 2 Dec 2019 WPC "
            "Percent of 7 Day Precip Forecasts < 0.05 inch"
        ),
        subtitle=(
            "Based on daily 0z Weather Prediction Center (WPC) "
            "forecasts each out seven days."
        ),
    )
    cmap = plt.get_cmap("terrain")
    # cmap.set_under('white')
    # cmap.set_over('red')
    levs = np.arange(0, 100.1, 10.0)
    mp.pcolormesh(
        lons,
        lats,
        total / count * 100.0,
        levs,
        cmap=cmap,
        units="%",
        extend="neither",
    )

    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
