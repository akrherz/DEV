"""Plot of cow data."""

import requests
from tqdm import tqdm
import pandas as pd
from pyiem.network import Table as NetworkTable
from pyiem.plot.geoplot import MapPlot
from pyiem.plot.use_agg import plt


def plot_data():
    """Plot the data."""
    df = pd.read_csv("/tmp/wfodata.csv", index_col="wfo")
    mp = MapPlot(
        title=(
            "1 Jan 2015 - 14 May 2019 "
            "Svr T'Storm + Tornado Areal Verification [%]"
        ),
        subtitle="based on unofficial IEM Cow output, 15km LSR buffer used",
        sector="nws",
    )
    cmap = plt.get_cmap("jet")
    mp.fill_cwas(
        df["verif"],
        bins=range(0, 41, 5),
        cmap=cmap,
        units="%",
        ilabel=True,
        lblformat="%.0f",
    )
    mp.postprocess(filename="/tmp/150101_190514_areal_torsvr.png")
    mp.close()


def get_data():
    """Get data."""
    nt = NetworkTable("WFO")
    rows = []
    for wfo in tqdm(nt.sts):
        url = (
            "https://mesonet.agron.iastate.edu/api/1/cow.json?wfo=%s&"
            "begints=2015-01-01T00:00Z&endts=2019-05-15T00:00Z&"
            "phenomena=SV&lsrtype=SV&phenomena=TO&lsrtype=TO"
        ) % (wfo,)
        req = requests.get(url)
        js = req.json()
        rows.append(dict(wfo=wfo, verif=js["stats"]["area_verify[%]"]))
    df = pd.DataFrame(rows)
    df.to_csv("/tmp/wfodata.csv", index=False)


if __name__ == "__main__":
    # get_data()
    plot_data()
