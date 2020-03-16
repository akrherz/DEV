"""Dump out a table."""
from pyiem.util import get_dbconn
from pandas.io.sql import read_sql

VALS = [
    ("Headwaters Cedar Creek", "071000060202"),
    ("Outlet Creek", "071000060307"),
    ("Bear Creek-Cedar River", "070802051004"),
    ("Lime Creek", "070802051003"),
    ("Hinkle Creek", "070802051102"),
    ("Mud Creek", "070802050907"),
    ("Opossum Creek", "070802051201"),
    ("Wildcat Creek", "070802051202"),
    ("Devils Run-Wolf Creek", "070802050808"),
    ("Twelvemile Creek", "070802050807"),
    ("Headwaters North English", "070802090401"),
    ("Upper Clear Creek", "070802090101"),
    ("Middle Clear Creek", "070802090102"),
    ("Lower Clear Creek", "070802090103"),
    ("Middle North English River", "070802090406"),
    ("Middle English River", "070802090302"),
    ("Gritter Creek", "070802090301"),
]


def main():
    """Go Main Go."""
    pgconn = get_dbconn("idep")
    df = read_sql(
        """
        SELECT
        max('') as name,
        huc_12,
        sum(qc_precip) as "Precipitation (mm)",
        sum(avg_runoff) as "Runoff (mm)",
        sum(avg_loss) as "Detachment (kg/m^2)",
        sum(avg_delivery) as "Hillslope Soil Loss (kg/m^2)"
        from results_by_huc12 WHERE scenario = 0 and
        valid >= '2020-01-01' and valid < '2020-03-15'
        GROUP by huc_12
    """,
        pgconn,
        index_col="huc_12",
    )
    df["Precipitation (in)"] = df["Precipitation (mm)"] / 25.4
    df["Runoff (in)"] = df["Runoff (mm)"] / 25.4
    df["Detachment (ton/acre)"] = df["Detachment (kg/m^2)"] * 4.463
    df["Hillslope Soil Loss (ton/acre)"] = (
        df["Hillslope Soil Loss (kg/m^2)"] * 4.463
    )
    hucs = []
    for (name, huc12) in VALS:
        hucs.append(huc12)
        df.at[huc12, "name"] = name

    df2 = df.loc[hucs]
    df2.to_excel("report.xlsx")


if __name__ == "__main__":
    main()
