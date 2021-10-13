"""Plot of LSR sources."""

import numpy as np
from pyiem.util import get_dbconn
from pyiem.plot import get_cmap
from pyiem.plot.use_agg import plt
from pandas.io.sql import read_sql
from matplotlib.patches import Rectangle


def main():
    """Go Main Go."""
    POSTGIS = get_dbconn("postgis")

    df = read_sql(
        """
    SELECT extract(year from valid)::int as yr,
    upper(source) as up,
    count(*) from lsrs WHERE valid > '2006-01-01'
    and valid < '2021-01-01' and typetext in ('HAIL', 'TORNADO')
    GROUP by yr, up ORDER by yr ASC
    """,
        POSTGIS,
        index_col=None,
    )

    top10 = (
        df[df["yr"] == 2006]
        .sort_values("count", ascending=False)["up"]
        .values[:10]
    )
    yearly = df[["yr", "count"]].groupby("yr").sum()
    df2 = df.join(yearly, on="yr", rsuffix="_total")

    labels = []
    y = []

    for year in range(2006, 2021):
        row = []
        sums = 0
        for t in top10:
            p = df2[(df2["yr"] == year) & (df2["up"] == t)]
            if p.empty:
                val = 0
            else:
                sums += float(p["count"])
                val = float(p["count"] / p["count_total"] * 100.0)
            if year == 2020:
                labels.append("%s %.1f%%" % (t, val))
            row.append(val)
        val = 100.0 - float(sums / yearly.at[year, "count"] * 100.0)
        row.append(val)
        if year == 2020:
            labels.append("(OTHER) %.1f%%" % (val,))
        y.append(row)
    np.shape(y)

    y = np.array(y)
    cmap = get_cmap("terrain")
    colors = cmap(np.linspace(0, 1, 11))
    fig, ax = plt.subplots(1, 1, figsize=(10.24, 7.68))
    ax.set_position([0.1, 0.1, 0.5, 0.8])
    stack_coll = ax.stackplot(
        range(2006, 2021),
        y[:, 0],
        y[:, 1],
        y[:, 2],
        y[:, 3],
        y[:, 4],
        y[:, 5],
        y[:, 6],
        y[:, 7],
        y[:, 8],
        y[:, 9],
        y[:, 10],
        colors=colors,
    )
    # make proxy artists
    proxy_rects = [
        Rectangle((0, 0), 1, 1, fc=pc.get_facecolor()[0])
        for pc in stack_coll[::-1]
    ]
    # make the legend
    ax.legend(proxy_rects, labels[::-1], ncol=1, fontsize=14, loc=(1, 0.0))
    ax.set_xticks(range(2006, 2021, 2))
    ax.set_xlim(2005.9, 2020.1)
    ax.set_xticklabels([str(s) for s in range(2006, 2021, 2)], fontsize=18)
    ax.set_ylim(0, 100)
    ax.set_yticks(range(0, 101, 10))
    fig.text(
        0.5,
        0.95,
        (
            "1 Jan 2006 - 24 Sep 2020 NWS Local Storm Report Source Type "
            "(2020 % labelled)\nOnly considering HAIL and TORNADO "
            "reports"
        ),
        ha="center",
        va="center",
        size=16,
    )
    ax.set_xlabel(
        "Based on unofficial Iowa Environmental Mesonet Archives @akrherz"
    )
    ax.set_ylabel("Percentage of Reports for Year [%]", fontsize=18)
    ax.grid(True)
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
