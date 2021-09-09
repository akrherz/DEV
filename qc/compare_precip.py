"""Do some checks on some on-site precip."""

import pandas as pd


def main():
    """Go Main Go."""
    df = pd.read_csv("sed2.csv")
    df["date_time"] = pd.to_datetime(df["date_time"])
    print(df.groupby("watershed")["date_time"].agg(["min", "max"]))
    df = pd.read_csv("dayrainflowsed.csv")
    print(df.groupby("sitename")["rainday (in)"].sum())


if __name__ == "__main__":
    main()
