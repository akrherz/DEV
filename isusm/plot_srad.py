"""Generate a plot of 1minute srad."""


from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn
from pandas.io.sql import read_sql


def main():
    """Go Main Go."""
    pgconn = get_dbconn("isuag")
    df = read_sql(
        """
        SELECT valid, slrkj_tot * 1000. / 60. as wmps,
        extract(day from valid) as day,
        extract(minute from valid) + extract(hour from valid) * 60. as minute
        from sm_minute where station = 'NWLI4'
        and valid > '2021-08-14' ORDER by valid ASC
    """,
        pgconn,
        index_col=None,
    )

    (fig, ax) = plt.subplots(1, 1)
    df2 = df[df["day"] == 14]
    ax.plot(df2["minute"].values, df2["wmps"].values, label="14 August 2021")
    df2 = df[df["day"] == 15]
    ax.plot(df2["minute"].values, df2["wmps"].values, label="15 August 2021")
    ax.grid(True)
    ax.set_xlim(300, 22 * 60)
    ax.set_xticks(range(360, 22 * 60 + 1, 120))
    ax.set_xticklabels(
        [
            "6 AM",
            "8 AM",
            "10 AM",
            "Noon",
            "2 PM",
            "4 PM",
            "6 PM",
            "8 PM",
            "10 PM",
        ]
    )
    ax.set_xlabel("Central Daylight Time")
    ax.legend()
    ax.set_ylabel("One Minute Averaged Solar Rad [W m-2]")
    ax.set_title("ISU Soil Moisture -- Newell: Allee ISU Research Farm")
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
