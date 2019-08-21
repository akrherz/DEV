"""Simple."""
import datetime

import requests
from pyiem.util import utc


def main():
    """Go Main Go."""
    sts = utc(2019, 8, 20, 3)
    ets = utc(2019, 8, 20, 21)
    interval = datetime.timedelta(minutes=5)
    i = 0
    now = sts
    while now < ets:
        uri = now.strftime((
            'https://mesonet.agron.iastate.edu/archive/data/%Y/%m/%d/'
            'comprad/n0r_%Y%m%d_%H%M.png'
        ))
        req = requests.get(uri)
        with open('images/%05i.png' % (i, ), 'wb') as fh:
            fh.write(req.content)
        now += interval
        i += 1


if __name__ == '__main__':
    main()
