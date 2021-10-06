"""Do some checks on some on-site precip."""

import pandas as pd


def main():
    """Go Main Go."""
    df = pd.read_csv("sed2.csv")
    df["rain"] = df["rain"] * 1000.0 / 25.4
    df["date_time"] = pd.to_datetime(df["date_time"])
    print(df.groupby("watershed")["date_time"].agg(["min", "max"]))
    print(df.groupby("watershed")["rain"].sum())
    df = pd.read_csv("dayrainflowsed.csv")
    print(df.groupby("sitename")["rain"].sum())


if __name__ == "__main__":
    main()
