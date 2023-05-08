"""Tornado Warnings for RDAs."""

from tqdm import tqdm

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot
from pyiem.util import get_dbconn


def plot_data():
    """Make the plot."""
    df = pd.read_csv("radar_tors.csv", index_col=None)
    df = df.sort_values("events", ascending=False)
    print(df)
    mp = MapPlot(
        sector="conus",
        title=(
            "2001 - 14 Jul 2020 NWS Tornado Warnings "
            "covering Forecast Office Locations"
        ),
        subtitle="Based on unofficial IEM archives",
    )
    mp.plot_values(
        df["lon"],
        df["lat"],
        df["events"],
        labelbuffer=0,
        labels=df["radar"],
        textsize=12,
        labeltextsize=8,
    )
    mp.postprocess(filename="radar_tors.png")


def get_data():
    """Figure out our data."""
    nt = NetworkTable("WFO")
    pgconn = get_dbconn("postgis")
    rows = []
    progress = tqdm(nt.sts)
    for sid in progress:
        progress.set_description(sid)
        df = read_sql(
            "SELECT issue, date(issue) from sbw "
            "WHERE issue > '2001-01-01' and "
            "phenomena = 'TO' and significance = 'W' and status = 'NEW' and "
            "ST_Contains(geom, ST_GeomFromEWKT('SRID=4326;POINT(%s %s)')) "
            "ORDER by issue ASC",
            pgconn,
            params=(nt.sts[sid]["lon"], nt.sts[sid]["lat"]),
        )
        rows.append(
            {
                "radar": sid,
                "lat": nt.sts[sid]["lat"],
                "lon": nt.sts[sid]["lon"],
                "events": len(df.index),
                "dates": len(df["date"].unique()),
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv("radar_tors.csv", index=False)


if __name__ == "__main__":
    plot_data()
