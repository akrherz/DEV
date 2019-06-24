"""Lapse"""
import datetime

import requests


def main():
    """Go Main"""
    # Generate series of images between 0z and 12z on the 3rd of August
    now = datetime.datetime(2019, 4, 21, 0, 0)
    ets = datetime.datetime(2019, 6, 24, 0, 0)
    interval = datetime.timedelta(minutes=1440)


    stepi = 0
    while now < ets:
        uri = now.strftime((
            "http://mtarchive.geol.iastate.edu/%Y/%m/%d/cod/sat/goes16/"
            "global/fulldiskeast/abi08/000index.txt"
        ))
        req = requests.get(uri)
        if req.status_code != 200:
            print(uri)
            continue
        fns = [None]*24
        for line in req.content.decode('ascii').split("\n"):
            tokens = line.split("_")
            if len(tokens) != 3:
                continue
            hr = int(tokens[2][8:10])
            if fns[hr] is None:
                fns[hr] = line
        for fn in fns:
            if fn is None:
                continue
            uri = now.strftime((
                "http://mtarchive.geol.iastate.edu/%Y/%m/%d/cod/sat/goes16/"
                "global/fulldiskeast/abi08/" + fn
            ))
            req = requests.get(uri)
            fp = open('images/%05i.jpg' % (stepi, ), 'wb')
            fp.write(req.content)
            fp.close()
            stepi += 1

        now += interval


if __name__ == '__main__':
    main()
