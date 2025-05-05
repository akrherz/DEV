"""Sigh."""

import httpx
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper


def main():
    """GO Main."""
    fn = "/home/akrherz/projects/pyIEM/src/pyiem/data/reference/igra2icao.txt"
    pyiem_xref = pd.read_csv(fn, sep=" ", names=["igra2", "icao"])

    with get_sqlalchemy_conn("mesosite") as conn:
        icao_xref = pd.read_sql(
            sql_helper(
                """
    select id, synop, country from stations where network = 'RAOB'
    and synop is not null
    """
            ),
            conn,
        )
    url = (
        "https://www.ncei.noaa.gov/data/integrated-global-radiosonde-archive/"
        "doc/igra2-station-list.txt"
    )
    resp = httpx.get(url)
    for line in resp.text.split("\n"):
        if line.strip() == "":
            continue
        igra2 = line[:11]
        igra2_state = line[38:40]
        igra2_country = igra2[:2]
        last_year = int(line[77:81])
        if not all(line[x].isdigit() for x in range(6, 11)):
            # print(f"Skipping: {line.strip()}")
            continue
        synop = int(line[6:11])
        if synop in icao_xref["synop"].values:
            iem_country = icao_xref.loc[
                icao_xref["synop"] == synop, "country"
            ].values[0]
            if igra2_country != iem_country:
                print(
                    f"Mismatch: {synop} {iem_country} {igra2_country} "
                    f"{line.strip()}"
                )
        if igra2_country == "US" and igra2_state in ["AK", "HI"]:
            pyiem_icao = pyiem_xref.loc[pyiem_xref["igra2"] == igra2]["icao"]
            if pyiem_icao.empty:
                if last_year > 2020:
                    print(f"Missing ICAO: {igra2} {line.strip()}")
            else:
                pyiem_icao = pyiem_icao.values[0]
                if pyiem_icao.startswith("K"):
                    print(
                        f"ID starts with K: {pyiem_icao} "
                        f"{igra2} {line.strip()}"
                    )


if __name__ == "__main__":
    main()
