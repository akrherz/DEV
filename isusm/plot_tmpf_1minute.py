"""Generate a plot of 1minute srad."""

from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn
from metpy.units import units
from pandas.io.sql import read_sql


def main():
    """Go Main Go."""
    pgconn = get_dbconn("isuag")
    df = read_sql(
        """
        SELECT valid, tair_c_avg,
        extract(day from valid) as day,
        extract(minute from valid) + extract(hour from valid) * 60. as minute
        from sm_minute where station = 'CIRI4'
        and valid >= '2020-05-09' and valid < '2020-05-10' ORDER by valid ASC
    """,
        pgconn,
        index_col="valid",
    )
    df["tmpf"] = (df["tair_c_avg"].values * units("degC")).to(units("degF")).m
    (fig, axes) = plt.subplots(2, 1, sharex=True)
    ax = axes[0]
    ax.plot(df["minute"].values, df["tmpf"].values, label="1 minute obs")
    df2 = df[df["minute"] % 60 == 0]
    df3 = df2.resample("1T").interpolate("linear")
    df["delta"] = df["tmpf"] - df3["tmpf"]
    print(df)
    ax.plot(df3["minute"].values, df3["tmpf"].values, label="60 minute sample")
    ax.grid(True)
    ax.legend()
    ax.set_ylim(20, 45)
    ax.set_ylabel(r"Air Temperature [$^\circ$F]")
    ax.set_title("ISU Soil Moisture 9 May 2020 -- Cedar Rapids")

    # ------------------
    ax = axes[1]
    ax.plot(
        df["minute"].values, df["delta"], label="1min - 60 min interpolated"
    )
    ax.set_xlim(0, 8 * 60)
    ax.set_xticks(range(0, 8 * 60 + 1, 60))
    ax.set_xticklabels(
        ["Mid", "1 AM", "2 AM", "3 AM", "4 AM", "5 AM", "6 AM", "7 AM", "8 AM"]
    )
    ax.set_xlabel("Central Daylight Time")
    ax.grid(True)
    ax.legend()
    ax.set_ylim(-4, 4)
    ax.axhline(0, color="r", lw=1.5)
    ax.set_yticks(range(-4, 5))
    ax.set_ylabel(r"Temperature Difference [$^\circ$F]")

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
