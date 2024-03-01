"""Why so slow."""

import datetime

import pandas as pd
from pyiem.plot.calendarplot import calendar_plot
from pyiem.util import logger

LOG = logger()


def main():
    """GO Main Go."""
    LOG.debug("fire")
    dates = pd.date_range("2000-01-01", "2000-12-31", freq="D")
    data = {}
    for date in dates:
        data[date] = {"val": "SLGT", "cellcolor": "r"}

    LOG.debug("calling")
    fig = calendar_plot(
        datetime.date(2000, 1, 1),
        datetime.date(2000, 12, 31),
        data,
    )
    LOG.debug("savefig")
    fig.savefig("test.png")
    LOG.debug("done")


if __name__ == "__main__":
    main()
