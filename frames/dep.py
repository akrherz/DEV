"""Lapse."""
from __future__ import print_function
import sys
import datetime

import requests


def main(argv):
    """Go Main"""
    # can't do jan 1 as the ramp changes for single day plots :/
    now = datetime.datetime(2010, 10, 12)
    ets = datetime.datetime(2011, 1, 1)
    interval = datetime.timedelta(days=1)
    scenario = argv[1]
    baseuri = (
        "http://dailyerosion.local/auto/%%s0101_%%s_%s_avg_delivery.png"
        "?iowa&progressbar&averaged&cruse"
    ) % (scenario, )

    stepi = 283
    while now < ets:
        print(now)
        url = baseuri % (now.year, now.strftime("%Y%m%d"))
        req = requests.get(url)
        output = open('images/%05i_%s.png' % (stepi, scenario), 'wb')
        output.write(req.content)
        output.close()
        stepi += 1
        now += interval


if __name__ == '__main__':
    main(sys.argv)
