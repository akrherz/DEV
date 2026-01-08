"""Total up things using an autoplot."""

import pandas as pd


def main():
    """Go."""
    for yr in range(1991, 2021):
        for mo in range(1, 13):
            url = (
                "https://mesonet.agron.iastate.edu/plotting/auto/plot/167/"
                f"network:IN_ASOS::zstation:IND::month:{mo}::year:{yr}.csv"
            )
            try:
                df = pd.read_csv(url, parse_dates=["ts"])
            except Exception:
                continue
            for dt in df["ts"].dt.date.unique():
                subdf = df[df["ts"].dt.date == dt]
                vals = subdf[subdf["ts"].dt.hour > 10][
                    "flstatus"
                ].value_counts()
                all_vfr = len(vals.index) == 1 and vals.index[0] == "VFR"
                print(f"{dt:%Y-%m-%d},{'VFR' if all_vfr else 'NO'}")


if __name__ == "__main__":
    main()
