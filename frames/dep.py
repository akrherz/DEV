"""Lapse"""
from __future__ import print_function
import datetime

import requests


def main():
    """Go Main"""
    # can't do jan 1 as the ramp changes for single day plots :/
    now = datetime.datetime(2018, 1, 2)
    ets = datetime.datetime(2019, 1, 1)
    interval = datetime.timedelta(days=1)

    baseuri = "http://dailyerosion.local/auto/%s0101_%s_0_avg_delivery.png?iowa&progressbar"

    stepi = 0
    while now < ets:
        print(now)
        url = baseuri % (now.year, now.strftime("%Y%m%d"))
        req = requests.get(url)
        output = open('images/%05i.png' % (stepi, ), 'wb')
        output.write(req.content)
        output.close()
        stepi += 1
        now += interval


if __name__ == '__main__':
    main()
