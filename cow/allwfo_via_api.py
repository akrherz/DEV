"""Generate a file of Cow Stats via API calls."""

import httpx
from tqdm import tqdm

import pandas as pd
from pyiem.network import Table as NetworkTable


def main():
    """Our main method."""
    nt = NetworkTable("WFO")
    progress = tqdm(list(nt.sts.keys()))
    res = []
    for wfo in progress:
        progress.set_description(wfo)
        url = (
            f"http://mesonet.agron.iastate.edu/api/1/cow.json?wfo={wfo}&"
            "begints=2019-01-01T00:00Z&endts=2024-05-08T00:00Z&"
            "phenomena=SV&phenomena=TO&"  # lsrtype=SV&"
        )
        try:
            reg = httpx.get(url, timeout=300)
        except Exception:
            print("FAIL, try again")
            reg = httpx.get(url, timeout=300)
        jsobj = reg.json()
        jsobj["stats"]["wfo"] = wfo
        res.append(jsobj["stats"])

    df = pd.DataFrame(res)
    df = df.set_index("wfo")
    df.to_csv("allwfo.csv")


if __name__ == "__main__":
    main()
