#!/usr/bin/env python
from __future__ import print_function
import datetime
import os

import requests


def main():
    # Generate series of images between 0z and 12z on the 3rd of August
    now = datetime.datetime(2017, 5, 11, 0, 0)
    ets = datetime.datetime(2017, 5, 12, 0, 0)
    interval = datetime.timedelta(minutes=5)

    uri = ("http://mesonet.agron.iastate.edu/"
           "c/tile.py/1.0.0/Ridge::USCOMP-N0R-%Y%m%d%H%M/4/3/6.png")

    # Change into a frames folder
    os.chdir("frames")
    stepi = 0
    timer = datetime.datetime.now()
    while now < ets:
        url = now.strftime(uri)
        sz = []
        for x in ['', '_2', '_3']:
            req = requests.get(url)
            print("%s %s %s %s %.3f" % (stepi, now.strftime("%d%H%M"),
                                     req.headers['X-IEM-ServerID'], len(req.content),
                                     (datetime.datetime.now() - timer).total_seconds()))
            timer = datetime.datetime.now()
            fp = open("%05d%s.png" % (stepi, x), 'wb')
            fp.write(req.content)
            fp.close()
            sz.append(len(req.content))
        if min(sz) != max(sz):
            print(sz)
            return
        stepi += 1
        now += interval

    os.system("ffmpeg -i %05d.png -qscale 0 out.mp4")


if __name__ == '__main__':
    main()
