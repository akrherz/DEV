"""MRMS Plotting util for zoomed in areas"""

import pygrib
from sqlalchemy import text

from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import MapPlot, nwsprecip
from pyiem.reference import Z_OVERLAY2
from pyiem.util import mm2inch


def get_data():
    """Get data"""
    lons = []
    lats = []
    vals = []
    labels = []

    networks = ["IACOCORAHS"]
    with get_sqlalchemy_conn("iem") as conn:
        res = conn.execute(
            text("""
        SELECT id, st_x(geom), st_y(geom), sum(pday)
        from summary_2024 s JOIN stations t
        on (s.iemid = t.iemid) WHERE s.day = '2024-07-23'
        and t.network = ANY(:networks)
        and pday > 0 GROUP by id, st_x, st_y
        ORDER by sum DESC
        """),
            {"networks": networks},
        )
        for row in res:
            lons.append(row[1])
            lats.append(row[2])
            vals.append("%.2f" % (row[3],))
            labels.append(row[0])
    return lons, lats, vals, labels


def main():
    """Go!"""
    title = "NOAA MRMS: RADAR + Guage Corrected Rainfall Estimates"
    mp = MapPlot(
        sector="spherical_mercator",
        north=42.1,
        east=-93.55,
        south=41.95,
        west=-93.7,
        titlefontsize=14,
        title=title,
        subtitle=(
            "MRMS 24h Ending: 7 AM 23 July 2024, Morning CoCoRaHS Reports"
        ),
    )

    grbs = pygrib.open("MultiSensor_QPE_24H_Pass2_00.00_20240723-120000.grib2")
    grb = grbs.message(1)
    pcpn = mm2inch(grb["values"])
    lats, lons = grb.latlons()
    lons -= 360.0
    clevs = [0.01, 0.05, 0.2, 0.5, 1, 1.5]
    cmap = nwsprecip()
    cmap.set_over("k")

    mp.pcolormesh(
        lons,
        lats,
        pcpn,
        clevs,
        cmap=cmap,
        latlon=True,
        units="inch",
        spacing="proportional",
        alpha=0.1,
    )
    mp.drawcounties()
    lons, lats, vals, _labels = get_data()
    mp.plot_values(
        lons,
        lats,
        vals,
        "%s",
        # labels=labels,
        labelbuffer=1,
        zorder=Z_OVERLAY2,
        labelcolor="white",
    )
    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
