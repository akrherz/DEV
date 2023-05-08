"""Create a histogram of precip intensity."""

import numpy as np
import requests
from tqdm import tqdm

import pandas as pd
from pyiem.plot import figure_axes
from pyiem.util import convert_value


def plot():
    """Plot the data."""
    df = pd.read_csv("/tmp/data.csv", parse_dates=["date"])
    df = df[df["daily_precip_in"] > 0]
    df["pcpn"] = convert_value(df["daily_precip_in"], "inch", "mm")
    bins = np.arange(0, 101, 5)
    bins[0] = 0.1
    df2 = df[df["date"].dt.year < 2010]
    hist1, edges = np.histogram(df2["pcpn"], bins=bins)
    df2 = df[df["date"].dt.year >= 2010]
    hist2, edges = np.histogram(df2["pcpn"], bins=bins)
    # We want days per year
    hist1 = hist1 / float(2010 - 1997)
    hist2 = hist2 / float(2022 - 2010)
    fig, ax = figure_axes(
        apctx={"_r": "43"},
        title="1997-2021 Daily Precipitation Frequency for Ames, IA",
        subtitle="Based bias corrected NCEP Stage IV by Oregon State PRISM",
        logo="dep",
    )
    ax.set_yscale("log")
    cs1 = np.cumsum(hist1[::-1])
    ax.scatter(edges[:-1], cs1[::-1], color="r", label="1997-2009")
    cs2 = np.cumsum(hist2[::-1])
    ax.scatter(edges[:-1], cs2[::-1], color="b", label="2010-2021")
    ax.legend()
    ax.set_xlabel(r"Precipitation $mm$ $d^{-1}$")
    ax.set_xticks(np.arange(0, 101, 10))
    ax.set_ylabel(r"Frequency $d$ $yr^{-1}$")
    ax.grid(True)
    fig.savefig("test.png")


def main():
    """Get data."""
    dfs = []
    for year in tqdm(range(1997, 2022)):
        uri = (
            f"https://mesonet.agron.iastate.edu/iemre/multiday/{year}-01-01/"
            f"{year}-12-31/42/-93.5/json"
        )
        req = requests.get(uri)
        data = req.json()
        dfs.append(pd.DataFrame(data["data"]))
    df = pd.concat(dfs)
    df.to_csv("/tmp/data.csv")


if __name__ == "__main__":
    # main()
    plot()
