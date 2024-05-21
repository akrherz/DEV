"""Plot ISU sounding."""

import sounderpy as spy

import pandas as pd
from metpy.calc import dewpoint_from_relative_humidity, wind_components
from metpy.units import units


def main():
    """Go to main."""
    df = pd.read_csv("2024-05-20_1813.sounding.csv")
    df = df.rename(
        columns={
            "Height (m AGL)": "z",
            " Pressure (mb)": "p",
            " Temperature (C)": "T",
            " Relative humidity (%)": "rh",
            " Wind speed (m/s)": "ws",
            " Wind direction (true deg)": "drct",
        }
    )
    clean_data = {
        "site_info": {
            "source": "ISU 2024-05-20 18:13:00",
            "state": "IA",
            "time": "2024-05-19 15:35:00",
            "elevation": 300,
        },
        "z": df["z"].values * units.meter,
        "p": df["p"].values * units.mbar,
        "T": df["T"].values * units.degC,
        "Td": dewpoint_from_relative_humidity(
            df["T"].values * units.degC, df["rh"].values * units.percent
        ),
        "ws": df["ws"].values,
        "drct": df["drct"].values,
    }
    clean_data["u"], clean_data["v"] = wind_components(
        df["ws"].values * units("m/s"), df["drct"].values * units.degrees
    )

    spy.metpy_sounding(clean_data, method="save", filename="test.png")


if __name__ == "__main__":
    main()
