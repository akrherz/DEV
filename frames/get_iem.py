"""Lapse"""
import datetime

import requests


def main():
    """Go Main"""
    # Generate series of images between 0z and 12z on the 3rd of August
    now = datetime.datetime(2020, 8, 10, 11, 0)
    ets = datetime.datetime(2020, 8, 10, 21, 0)
    interval = datetime.timedelta(minutes=5)

    stepi = 0
    while now <= ets:
        uri = now.strftime(
            "https://mesonet.agron.iastate.edu/archive/data/%Y/%m/%d/comprad/n0r_%Y%m%d_%H%M.png"
        )
        req = requests.get(uri)
        with open("images/%05i.png" % (stepi,), "wb") as fp:
            fp.write(req.content)
        stepi += 1
        now += interval


if __name__ == "__main__":
    main()
