"""Plot of Average MCD Size."""

# third party
from pandas import read_sql
from pyiem.plot import figure_axes
from pyiem.util import get_dbconnstr


def main():
    """Go Main Go."""
    df = read_sql(
        "select year, "
        "avg(ST_Area(geom::geography)) from mcd where issue > '2003-01-01' "
        "and year < 2022 GROUP by year ORDER by year",
        get_dbconnstr("postgis"),
    )
    df["norm"] = df["avg"] / df["avg"].max() * 100.0
    title = (
        "Storm Prediction Center :: Mesoscale Discussion Area Size\n"
        "Relative to year 2005 maximum of 86,000 sq km"
    )
    (fig, ax) = figure_axes(title=title, apctx={"_r": "43"})
    ax.bar(df["year"].values, df["norm"].values)
    for _, row in df.iterrows():
        ax.text(
            row["year"],
            row["norm"] + 1,
            f"{row['norm']:.0f}%",
            ha="center",
        )
    ax.set_ylabel("Normalized MCD Size Relative to 2005 Max [%]")
    ax.grid(True)
    ax.set_ylim(60, 104)
    ax.set_yticks(range(60, 101, 5))
    ax.set_xticks(range(2004, 2024, 4))
    ax.set_xlim(2002.2, 2021.7)
    ax.set_xlabel(
        "@akrherz, based on unofficial IEM archives, thru 31 Dec 2021"
    )
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
