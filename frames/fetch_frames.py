"""Simple."""
import datetime

import requests
from pyiem.util import utc


def main():
    """Go Main Go."""
    sts = utc(2019, 11, 6, 2)
    ets = utc(2019, 11, 6, 22)
    interval = datetime.timedelta(minutes=5)
    i = 0
    now = sts
    while now < ets:
        uri = now.strftime(
            ("http://iem.local/roads/iem.php?trucks&valid=%Y-%m-%d%%20%H:%M")
        )
        req = requests.get(uri)
        with open("images/%05i.png" % (i,), "wb") as fh:
            fh.write(req.content)
        now += interval
        i += 1


if __name__ == "__main__":
    main()
