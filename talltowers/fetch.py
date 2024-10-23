"""Get the hourly data."""

import httpx
import pandas as pd


def main():
    """Go Main Go."""
    for dt in pd.date_range("2016/04/05", "2021/09/22", freq="1D"):
        uri = (
            "http://iem.local/cgi-bin/request/talltowers.py?tz=UTC&"
            f"sts={dt:%Y-%m-%d}T00:00:00Z&ets={dt:%Y-%m-%d}T23:59:59Z&"
            "var=ws_s,ws_nw&z=5,10,20,40,80,120&agg=avg&window=60&format=comma"
            "&station=ETTI4,MCAI4"
        )
        print(uri)
        resp = httpx.get(uri, timeout=60)
        if resp.status_code != 200:
            print(f"Failed to fetch {resp.content}")
            return
        with open("dl.csv", "a") as fh:
            fh.write(resp.text)


if __name__ == "__main__":
    main()
