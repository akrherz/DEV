"""Plot of Average MCD Size."""

# third party
from pyiem.plot import figure_axes
from pyiem.util import get_dbconn
from pandas.io.sql import read_sql


def main():
    """Go Main Go."""
    pgconn = get_dbconn("postgis")
    df = read_sql(
        "select year, "
        "avg(ST_Area(geom::geography)) from mcd where issue > '2003-01-01' "
        "GROUP by year ORDER by year",
        pgconn,
    )
    df["norm"] = df["avg"] / df["avg"].max() * 100.0
    title = (
        "Storm Prediction Center :: Mesoscale Discussion Area Size\n"
        "Relative to year 2005 maximum of 86,000 sq km"
    )
    (fig, ax) = figure_axes(title=title)
    ax.bar(df["year"].values, df["norm"].values)
    for _, row in df.iterrows():
        ax.text(
            row["year"],
            row["norm"] + 1,
            "%.0f%%" % (row["norm"],),
            ha="center",
        )
    ax.set_ylabel("Normalized MCD Size Relative to 2005 Max [%]")
    ax.grid(True)
    ax.set_ylim(60, 104)
    ax.set_yticks(range(60, 101, 5))
    ax.set_xticks(range(2004, 2024, 4))
    ax.set_xlim(2002.2, 2021.7)
    ax.set_xlabel(
        "@akrherz, based on unofficial IEM archives, 2021 data to 1 April"
    )
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
