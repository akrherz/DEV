"""Lapse."""
import sys
import datetime

import requests


def main(argv):
    """Go Main"""
    # can't do jan 1 as the ramp changes for single day plots :/
    now = datetime.datetime(int(argv[2]), 1, 2)
    ets = datetime.datetime(int(argv[2]) + 1, 1, 1)
    interval = datetime.timedelta(days=1)
    scenario = argv[1]
    baseuri = (
        "http://depbackend.local/auto/%%s0101_%%s_%s_avg_delivery.png"
        "?iowa&progressbar&cruse"
    ) % (scenario,)

    stepi = 0
    while now < ets:
        print(now)
        url = baseuri % (now.year, now.strftime("%Y%m%d"))
        req = requests.get(url)
        with open(
            "images/%s_%05i_%s.png" % (now.year, stepi, scenario), "wb"
        ) as fh:
            fh.write(req.content)
        stepi += 1
        now += interval


if __name__ == "__main__":
    main(sys.argv)
