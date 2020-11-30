"""Count Words."""
# 3rd Party
from pyiem.util import get_dbconn
from pyiem.plot.use_agg import plt
from pyiem.reference import wfo_dict
import pandas as pd
from pandas.io.sql import read_sql

LABELS = {
    "ER": "Eastern",
    "SR": "Southern",
    "PR": "Pacific/Alaska",
    "WR": "Western",
    "CR": "Central",
}


def main():
    """Go Main Go."""
    pgconn = get_dbconn("afos")
    wfos = []
    for wfo in wfo_dict:
        wfos.append({"wfo": wfo, "region": wfo_dict[wfo]["region"]})
    wfos = pd.DataFrame(wfos)
    df = read_sql(
        "select to_char(entered, 'YYYYmm') as datum, "
        "substr(source, 2, 3) as wfo, "
        "count(*) as products, sum(wordcount) as words, "
        "sum(charcount) as chars "
        "from afd WHERE entered > '2004-01-01' "
        "GROUP by datum, wfo ORDER by datum, wfo ASC",
        pgconn,
        index_col=None,
    )
    df = pd.merge(df, wfos, how="outer", on="wfo")

    fig, ax = plt.subplots(1, 1, figsize=(12, 6.75))
    gdf = df.groupby(["datum", "region"]).agg(["sum", "count"]).reset_index()
    for region in ["ER", "SR", "CR", "WR", "PR"]:
        df2 = gdf[gdf["region"] == region].copy()
        df2["date"] = pd.to_datetime(df2["datum"], format="%Y%m")
        ax.plot(
            df2["date"],
            df2[("products", "sum")] / df2[("products", "count")] / 30.25,
            label=LABELS[region],
        )
    # All
    df2 = df.groupby("datum").agg(["sum", "count"]).reset_index()
    df2["date"] = pd.to_datetime(df2["datum"], format="%Y%m")
    ax.plot(
        df2["date"],
        df2[("products", "sum")] / df2[("products", "count")] / 30.25,
        label="ALL",
        color="k",
        lw=2,
    )
    ax.grid()
    ax.legend(loc=2)
    ax.set_title(
        "\n".join(
            [
                "1 Jan 2004- 30 Nov 2020 Monthly Average Area Forecast Discussions"
                " issued per Day per Office",
                "Based on unofficial IEM Archives.",
            ]
        )
    )
    ax.set_ylabel("Products per Day")
    fig.text(0.05, 0.02, "@akrherz, Generated: 30 Nov 2020")
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
