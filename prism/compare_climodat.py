"""See how our statewide estimates compare with PRISM."""

import pandas as pd
from pyiem.plot import figure
from pyiem.util import get_sqlalchemy_conn, c2f


def main():
    """Go Main Go."""
    df = pd.read_csv("/tmp/iowa.txt", parse_dates=["date"], index_col="date")
    with get_sqlalchemy_conn("coop") as conn:
        iem = pd.read_sql(
            "SELECT day, high, low from alldata_ia where station = 'IA0000' "
            "and day >= '1981-01-01' ORDER by day ASC",
            conn,
            index_col="day",
        )
    df["high"] = c2f(df["tmax"].values)
    df["low"] = c2f(df["tmin"].values)
    for col in ["high", "low"]:
        df[f"iem_{col}"] = iem[col]
        df[f"iem_{col}_bias"] = df[f"iem_{col}"] - df[col]
    # df = df.dropna().resample("M").mean()
    df = df.loc[pd.Timestamp("1981/01/01") : pd.Timestamp("2022/12/31")]
    # print(df.describe())
    print(df.sort_values("iem_low_bias", ascending=False).head(10))

    fig = figure(
        title="(1981-2022) Iowa Daily Temperature Bias",
        subtitle="IEM Areal Average minus PRISM Areal Average",
    )
    ax = fig.add_axes([0.1, 0.52, 0.8, 0.32])
    dd = df[df["iem_high_bias"] >= 0]
    ax.scatter(dd.index, dd["iem_high_bias"], color="r")
    dd = df[df["iem_high_bias"] < 0]
    ax.scatter(dd.index, dd["iem_high_bias"], color="b")
    ax.grid(True)
    ax.set_title("High Temperature")
    ax.set_ylabel("IEM Bias [F]")
    ax.set_ylim(-15, 25)

    ax = fig.add_axes([0.1, 0.1, 0.8, 0.32])
    dd = df[df["iem_low_bias"] >= 0]
    ax.scatter(dd.index, dd["iem_low_bias"], color="r")
    dd = df[df["iem_low_bias"] < 0]
    ax.scatter(dd.index, dd["iem_low_bias"], color="b")
    ax.grid(True)
    ax.set_title("Low Temperature")
    ax.set_ylabel("IEM Bias [F]")
    ax.set_ylim(-15, 25)

    fig.savefig("/tmp/bias.png")


if __name__ == "__main__":
    main()
