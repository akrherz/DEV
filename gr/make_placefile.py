"""Make a simple? placefile of turbine locations."""

import pandas as pd


def main():
    """Go Main Go."""
    df = pd.read_csv("uswtdb_v5_1_20220729.csv", encoding_errors="ignore")
    with open("uswtdb.txt", "w", encoding="ascii") as fh:
        fh.write("Title: US Wind Turbines 29 Jul 2022\n")
        fh.write("IconFile: 1, 25, 25, 12, 12, dot.png\n")
        for _, row in df.iterrows():
            fh.write(f"Object: {row['ylat']}, {row['xlong']}\n")
            fh.write("Icon: 0, 0, 0, 1, 1, hoverText\n")
            fh.write("End:\n")


if __name__ == "__main__":
    main()
