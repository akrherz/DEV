"""Shrug."""

import numpy as np
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    COOP = get_dbconn("coop")
    cursor = COOP.cursor()
    nt = NetworkTable(
        (
            "IACLIMATE",
            "MNCLIMATE",
            "NDCLIMATE",
            "SDCLIMATE",
            "NECLIMATE",
            "KSCLIMATE",
            "MOCLIMATE",
            "KYCLIMATE",
            "ILCLIMATE",
            "WICLIMATE",
            "INCLIMATE",
            "OHCLIMATE",
            "MICLIMATE",
        )
    )

    cursor.execute(
        """
    SELECT station, sum(case when precip >= 2 then precip else 0 end) /
    sum(precip) from alldata WHERE year > 1980 and precip > 0
    and year < 2011 GROUP by station
    """
    )

    lats = []
    lons = []
    vals = []
    for row in cursor:
        if row[0][2] == "C" or row[0][2:] == "0000":
            continue
        if row[0] not in nt.sts:
            continue
        if row[0][:2] == "MI" and row[1] > 0.2:
            print(row)
        lats.append(nt.sts[row[0]]["lat"])
        lons.append(nt.sts[row[0]]["lon"])
        vals.append(row[1] * 100.0)

    m = MapPlot(
        sector="midwest",
        title="Contribution of Daily 2+ inch Precip Events to Yearly Total",
        subtitle="1981-2010 based on IEM archive of NWS COOP Data",
    )
    m.contourf(lons, lats, vals, np.arange(0, 41, 2), units="%")
    m.postprocess(filename="twoinch_1981_2010.png")


if __name__ == "__main__":
    main()
