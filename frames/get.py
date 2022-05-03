"""Lapse"""
import datetime

import requests


def main():
    """Go Main"""
    now = datetime.datetime(2022, 4, 1, 0, 0)
    ets = datetime.datetime(2022, 5, 1, 0, 0)
    interval = datetime.timedelta(minutes=1440)

    stepi = 0
    while now < ets:
        uri = now.strftime(
            (
                "http://mtarchive.geol.iastate.edu/%Y/%m/%d/cod/sat/goes16/"
                "regional/northcentral/abi11/000index.txt"
            )
        )
        req = requests.get(uri)
        if req.status_code != 200:
            print(uri)
            continue
        for line in req.content.decode("ascii").split("\n"):
            tokens = line.split("_")
            if len(tokens) != 3:
                continue
            uri = now.strftime(
                (
                    "http://mtarchive.geol.iastate.edu/%Y/%m/%d/cod/sat/goes16/"
                    f"regional/northcentral/abi11/{line}"
                )
            )
            req = requests.get(uri)
            with open(f"images/{stepi:05.0f}.jpg", "wb") as fp:
                fp.write(req.content)
            stepi += 1

        now += interval


if __name__ == "__main__":
    main()
