"""Lapse"""
from __future__ import print_function
import datetime
import os

import requests


def main():
    """Go Main"""
    # Generate series of images between 0z and 12z on the 3rd of August
    now = datetime.datetime(2017, 6, 12, 20, 0)
    ets = datetime.datetime(2017, 6, 13, 2, 0)
    interval = datetime.timedelta(minutes=1)

    baseuri = "http://mesonet.agron.iastate.edu/GIS/radmap.php?"
    baseuri += ("width=720&height=486&layers[]=ridge&ridge_radar=DVN&"
                "ridge_product=N0Q&bbox=-91.6,41.2,-88.6,41.3&"
                "layers[]=uscounties")

    stepi = 0
    while now < ets:
        url = "%s&ts=%s" % (baseuri, now.strftime("%Y%m%d%H%M"))
        req = requests.get(url)
        output = open('images/%05i.png' % (stepi, ), 'wb')
        output.write(req.content)
        output.close()
        stepi += 1
        now += interval


if __name__ == '__main__':
    main()
