"""Simple."""

import datetime

import requests

from pyiem.util import utc


def main():
    """Go Main Go."""
    sts = utc(2024, 1, 1)
    ets = utc(2025, 1, 1)
    interval = datetime.timedelta(hours=24)
    i = 0
    now = sts
    while now < ets:
        t2 = now + datetime.timedelta(days=21)
        uri = f"http://iem.local/plotting/auto/plot/21/csector:conus::date1:{now:%Y-%m-%d}::date2:{t2:%Y-%m-%d}::varname:precip::cmap:RdBu::_r:43::_cb:1.png"
        req = requests.get(uri)
        with open("images/%05i.png" % (i,), "wb") as fh:
            fh.write(req.content)
        now += interval
        i += 1


if __name__ == "__main__":
    main()
