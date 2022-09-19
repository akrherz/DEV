"""Generate a file of Cow Stats via API calls."""

from pyiem.network import Table as NetworkTable
from tqdm import tqdm
import requests
import pandas as pd


def main():
    """Our main method."""
    nt = NetworkTable("WFO")
    progress = tqdm(list(nt.sts.keys()))
    res = []
    for wfo in progress:
        progress.set_description(wfo)
        url = (
            f"http://iem.local/api/1/cow.json?wfo={wfo}&"
            "begints=2015-01-01T00:00Z&endts=2020-01-01T00:00Z&"
            "phenomena=SV&lsrtype=SV&"
        )
        reg = requests.get(url, timeout=300)
        jsobj = reg.json()
        jsobj["stats"]["wfo"] = wfo
        res.append(jsobj["stats"])

    df = pd.DataFrame(res)
    df = df.set_index("wfo")
    df.to_csv("allwfo.csv")


if __name__ == "__main__":
    main()
