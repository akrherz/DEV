"""Check over our SWAT files for irregularities."""

import calendar
import datetime
import sys

import pandas as pd
import seaborn as sns
from pyiem.plot.use_agg import plt


def main(argv):
    """Run main Run."""
    fn = argv[1]
    df = pd.read_csv(fn)
    sdate = datetime.datetime.strptime(df.columns[0], "%Y%m%d")
    df.columns = ["precip_mm"]
    df["date"] = pd.date_range(sdate, periods=len(df.index))
    df.set_index("date", inplace=True)
    gdf = df.groupby([df.index.year, df.index.month]).sum().copy()
    gdf.reset_index(level=1, inplace=True)
    gdf.columns = ["month", "precip_mm"]
    gdf.reset_index(inplace=True)
    gdf.columns = ["year", "month", "precip_mm"]
    gdf = pd.pivot_table(
        gdf, index="year", values="precip_mm", columns="month"
    )
    print(gdf)
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.heatmap(
        gdf, annot=True, fmt=".0f", cmap="YlGnBu", linewidths=0.5, ax=ax
    )
    ax.set_xticklabels(calendar.month_abbr[1:])
    tokens = fn.split("/")
    ax.set_title("Monthly Precipitation [mm] %s %s" % (tokens[-3], tokens[-1]))
    fig.savefig("%s_monthly_total.png" % (tokens[-1][:-4],))
    plt.close()

    # -------------------------------------
    for threshold in [0.25, 25]:
        df2 = df[df["precip_mm"] > threshold]
        gdf = df2.groupby([df2.index.year, df2.index.month]).count().copy()
        gdf.reset_index(level=1, inplace=True)
        gdf.columns = ["month", "precip_mm"]
        gdf.reset_index(inplace=True)
        gdf.columns = ["year", "month", "precip_mm"]
        gdf = pd.pivot_table(
            gdf, index="year", values="precip_mm", columns="month"
        )
        print(gdf)
        fig, ax = plt.subplots(figsize=(9, 6))
        sns.heatmap(
            gdf, annot=True, fmt=".0f", cmap="YlGnBu", linewidths=0.5, ax=ax
        )
        ax.set_xticklabels(calendar.month_abbr[1:])
        tokens = fn.split("/")
        ax.set_title(
            "Daily Events >= %smm %s %s" % (threshold, tokens[-3], tokens[-1])
        )
        fig.savefig("%s_%s_counts.png" % (tokens[-1][:-4], threshold))
        plt.close()

    # -------------------------------------
    gdf = df.groupby([df.index.year, df.index.month]).max().copy()
    gdf.reset_index(level=1, inplace=True)
    gdf.columns = ["month", "precip_mm"]
    gdf.reset_index(inplace=True)
    gdf.columns = ["year", "month", "precip_mm"]
    gdf = pd.pivot_table(
        gdf, index="year", values="precip_mm", columns="month"
    )
    print(gdf)
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.heatmap(
        gdf, annot=True, fmt=".0f", cmap="YlGnBu", linewidths=0.5, ax=ax
    )
    ax.set_xticklabels(calendar.month_abbr[1:])
    tokens = fn.split("/")
    ax.set_title("Max Daily Precip [mm] %s %s" % (tokens[-3], tokens[-1]))
    fig.savefig("%s_monthly_max.png" % (tokens[-1][:-4],))
    plt.close()


if __name__ == "__main__":
    main(sys.argv)
