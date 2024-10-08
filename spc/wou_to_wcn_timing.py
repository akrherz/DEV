"""How quickly does an office issue the WCN after the WOU."""

import pandas as pd
from pyiem.database import get_dbconn
from pyiem.nws.products.vtec import parser
from pyiem.plot import get_cmap
from pyiem.plot.geoplot import MapPlot


def plotter():
    """Make something pretty."""
    df = pd.read_csv("timing.csv")
    for col in ["wcn", "wou"]:
        df[col] = pd.to_datetime(df[col])
    df["delta"] = df["wmo_seconds"] / 60.0
    df = df[df["delta"] > -5]
    df = df[df["delta"] < 30]
    gdf = df[["wfo", "delta"]].groupby("wfo").describe()
    gdf = gdf[gdf["delta", "count"] > 4]
    print(gdf)
    mp = MapPlot(
        sector="conus",
        title=(
            "Average Time (Minutes) between SPC WOU Issuance and "
            "WFO WCN Issuance"
        ),
        subtitle=(
            "2006-2020, based on unofficial IEM archives with WFO having at "
            "least 5 watches."
        ),
    )
    mp.fill_cwas(
        gdf["delta", "mean"].to_dict(),
        cmap=get_cmap("plasma"),
        extend="max",
        bins=range(0, 11, 1),
        ilabel=True,
        lblformat="%.1f",
    )
    mp.postprocess(filename="test.png")


def dump_data():
    """Go Main Go."""
    afosdb = get_dbconn("afos")
    postgisdb = get_dbconn("postgis")
    cursor = afosdb.cursor()
    cursor.execute(
        "SELECT data from products where source = 'KWNS' and "
        "entered > '2006-01-01' and substr(pil, 1, 3) = 'WOU' and "
        "data ~* '.NEW.' ORDER by entered ASC"
    )
    dfs = []
    for row in cursor:
        try:
            prod = parser(row[0])
        except Exception as exp:
            print(exp)
            continue
        ugcs = []
        etn = None
        wou_issue = None
        phenomena = None
        for segment in prod.segments:
            if not segment.vtec or segment.vtec[0].action != "NEW":
                continue
            ugcs.extend([str(x) for x in segment.ugcs])
            etn = segment.vtec[0].etn
            wou_issue = segment.vtec[0].begints.replace(tzinfo=None)
            phenomena = segment.vtec[0].phenomena
        if etn is None:
            continue
        # Go find in the database
        df = pd.read_sql(
            "SELECT wfo, min(issue at time zone 'UTC') as wcn "
            f"from warnings_{wou_issue.year} "
            "where ugc in %s and phenomena = %s and significance = 'A' and "
            "eventid = %s GROUP by wfo ORDER by wcn ASC",
            postgisdb,
            params=(tuple(ugcs), phenomena, etn),
        )
        df["wou"] = wou_issue
        df["wou_header_time"] = prod.wmo_valid.replace(tzinfo=None)
        df["eventid"] = etn
        df["year"] = wou_issue.year
        dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)
    df["vtec_seconds"] = (df["wcn"] - df["wou"]).dt.total_seconds()
    df["wmo_seconds"] = (df["wcn"] - df["wou_header_time"]).dt.total_seconds()
    df.to_csv("timing.csv", index=False)
    print(df)


if __name__ == "__main__":
    # dump_data()
    plotter()
