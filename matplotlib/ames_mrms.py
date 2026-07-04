"""MRMS Plotting util for zoomed in areas"""

import pandas as pd
import pygrib
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import MapPlot, nwsprecip
from pyiem.reference import Z_OVERLAY2
from pyiem.util import mm2inch
from sqlalchemy import text


def get_data() -> pd.DataFrame:
    """Get data"""
    lons = []
    lats = []
    vals = []
    labels = []

    networks = ["IA_COOP"]
    with get_sqlalchemy_conn("iem") as conn:
        res = conn.execute(
            text("""
        SELECT id, st_x(geom), st_y(geom), sum(pday)
        from summary_2026 s JOIN stations t
        on (s.iemid = t.iemid) WHERE s.day = '2026-07-03'
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
    networks = ["IA_COCORAHS"]
    with get_sqlalchemy_conn("coop") as conn:
        res = conn.execute(
            text("""
        SELECT id, st_x(geom), st_y(geom), sum(precip)
        from cocorahs_2026 s JOIN stations t
        on (s.iemid = t.iemid) WHERE s.day = '2026-07-03'
        and t.network = ANY(:networks)
        and precip > 0 GROUP by id, st_x, st_y
        ORDER by sum DESC
        """),
            {"networks": networks},
        )
        for row in res:
            lons.append(row[1])
            lats.append(row[2])
            vals.append("%.2f" % (row[3],))
            labels.append(row[0])

    with get_sqlalchemy_conn("postgis") as conn:
        res = conn.execute(
            text("""
        SELECT ctid, st_x(geom), st_y(geom), magnitude
        from lsrs_2026 s WHERE valid > '2026-07-03 06:00'
        and valid < '2026-07-03 20:00' and type = 'R'
        and magnitude > 0 ORDER by magnitude desc
        """),
            {"networks": networks},
        )
        for row in res:
            lons.append(row[1])
            lats.append(row[2])
            vals.append("%.2f" % (row[3],))
            labels.append(row[0])
    return pd.DataFrame(
        {
            "lon": lons,
            "lat": lats,
            "val": vals,
            "label": labels,
        }
    ).sort_values("val", ascending=False)


def main():
    """Go!"""
    title = "NOAA MRMS: RADAR + Gauge Corrected Rainfall Estimates"
    mp = MapPlot(
        sector="spherical_mercator",
        north=41.9,
        east=-93.35,
        south=41.55,
        west=-93.7,
        titlefontsize=14,
        title=title,
        subtitle=(
            "MRMS 24h Ending: 10 AM 3 July 2026, "
            "Morning CoCoRaHS/COOP Reports, NWS Local Storm Reports"
        ),
    )

    grbs = pygrib.open("MultiSensor_QPE_24H_Pass2_00.00_20260703-150000.grib2")
    grb = grbs.message(1)
    pcpn = mm2inch(grb["values"])
    lats, lons = grb.latlons()
    lons -= 360.0
    clevs = [0.01, 0.25, 0.5, 1, 2, 3, 5, 7, 10]
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
    obsdf = get_data()
    mp.plot_values(
        obsdf["lon"].to_numpy(),
        obsdf["lat"].to_numpy(),
        obsdf["val"].to_numpy(),
        "%s",
        # labels=labels,
        labelbuffer=1,
        zorder=Z_OVERLAY2,
        labelcolor="white",
    )
    mp.postprocess(filename="260704.png")


if __name__ == "__main__":
    main()
