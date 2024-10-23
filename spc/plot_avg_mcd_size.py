"""Plot of Average MCD Size."""

# third party
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import figure_axes
from sqlalchemy import text


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("postgis") as conn:
        yearly = pd.read_sql(
            text("""
            select year, avg(ST_Area(geom::geography)) from mcd
            where issue > '2003-01-01' GROUP by year order by year
            """),
            conn,
            index_col="year",
        )
    print(yearly.loc[2008])
    yearly["norm"] = yearly["avg"] / yearly["avg"].max() * 100.0
    title = (
        "Storm Prediction Center :: Mesoscale Discussion Area Size\n"
        "Relative to year 2008 maximum of ~86,000 sq km"
    )
    (fig, ax) = figure_axes(title=title, apctx={"_r": "43"})
    ax.bar(yearly.index, yearly["norm"].values)
    for year, row in yearly.iterrows():
        ax.text(
            year,
            row["norm"] + 1,
            f"{row['norm']:.0f}%",
            ha="center",
        )
    ax.set_ylabel("Normalized MCD Size Relative to 2005 Max [%]")
    ax.grid(True)
    ax.set_ylim(60, 104)
    ax.set_yticks(range(60, 101, 5))
    ax.set_xticks(range(2004, 2024, 4))
    ax.set_xlim(2002.2, 2024.7)
    ax.set_xlabel(
        "@akrherz, based on unofficial IEM archives, thru 29 May 2024"
    )
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
