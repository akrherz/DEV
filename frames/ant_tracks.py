"""Simple."""
import datetime

import requests
from pyiem.util import utc


def main():
    """Go Main Go."""
    sts = utc(2021, 1, 26, 16, 20)
    ets = utc(2021, 1, 26, 20, 46)
    interval = datetime.timedelta(minutes=5)
    i = 436
    now = sts
    while now < ets:
        uri = now.strftime(
            (
                "http://mesonet.agron.iastate.edu/roads/iem.php?"
                "trucks&nexrad&valid=%Y-%m-%d%%20%H:%M"
            )
        )
        req = requests.get(uri)
        with open("images/%05i.png" % (i,), "wb") as fh:
            fh.write(req.content)
        now += interval
        i += 1


if __name__ == "__main__":
    main()
