"""Generate a feature plot."""

import numpy as np
from PIL import Image
from pyiem.database import get_dbconn
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot, nwsprecip


def main():
    """Go Main Go."""
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor()

    cursor.execute(
        """SELECT ST_x(geom) as lon, ST_y(geom) as lat,
    pday from summary_2025 s JOIN stations t on (s.iemid = t.iemid)
    where day = '2025-07-23' and network in
    ('WI_COOP', 'MN_COOP', 'IA_COOP')
    and pday is not null ORDER by pday DESC"""
    )
    llons = []
    llats = []
    vals = []
    for row in cursor:
        llons.append(row[0])
        llats.append(row[1])
        vals.append("%.2f" % (row[2],))
    pgconnc = get_dbconn("coop")
    ccursor = pgconnc.cursor()
    ccursor.execute(
        """SELECT ST_x(geom) as lon, ST_y(geom) as lat,
    precip from cocorahs_2025 s JOIN stations t on (s.iemid = t.iemid)
    where day = '2025-07-23' and network in
    ('IA_COCORAHS')
    and precip is not null ORDER by precip DESC"""
    )
    for row in ccursor:
        llons.append(row[0])
        llats.append(row[1])
        vals.append("%.2f" % (row[2],))

    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()

    cursor.execute(
        """SELECT ST_x(geom) as lon, ST_y(geom) as lat,
    max(magnitude) from lsrs_2025
    where wfo in ('DMX', 'DVN', 'ARX') and typetext = 'HEAVY RAIN' and
    valid > '2025-07-23' GROUP by lon, lat ORDER by max DESC"""
    )
    for row in cursor:
        llons.append(row[0])
        llats.append(row[1])
        vals.append("%.2f" % (row[2],))

    img = Image.open("/tmp/p24h_202507231300.png")
    data = np.flipud(np.asarray(img))
    # 7000,3500 == -130,-60,55,25 ===  -100 to -90 then 38 to 45
    sample = data[1800:2501, 3000:4501]
    sample = np.where(sample == 255, 0, sample)
    data = sample * 0.01
    data = np.where(sample > 100, 1.0 + (sample - 100) * 0.05, data)
    data = np.where(sample > 180, 5.0 + (sample - 180) * 0.2, data)
    lons = np.arange(-100, -84.99, 0.01)
    lats = np.arange(38, 45.01, 0.01)

    x, y = np.meshgrid(lons, lats)

    mp = MapPlot(
        sector="custom",
        west=-92.3,
        east=-91.4,
        south=42.2,
        north=42.6,
        title="NOAA MRMS 24 Hour RADAR-Only Precipitation Estimate",
        subtitle=(
            "Buchanan County, IA. MRMS valid 8 AM 23 Jul 2025, "
            "NWS Local Storm, COOP, and CoCoRaHS Reports Overlaid"
        ),
    )
    clevs = [
        0.01,
        0.1,
        0.25,
        0.5,
        0.75,
        1,
        1.5,
        2,
        2.5,
        3,
        3.5,
        4,
        5,
        6,
        8,
        10,
    ]

    mp.contourf(x[:, :-1], y[:, :-1], data, clevs, cmap=nwsprecip())

    nt = NetworkTable("IA_ASOS")
    lo = []
    la = []
    va = []
    for sid in nt.sts.keys():
        lo.append(nt.sts[sid]["lon"])
        la.append(nt.sts[sid]["lat"])
        va.append(nt.sts[sid]["name"])

    # m.plot_values(lo, la, va, fmt='%s', textsize=10, color='black')
    mp.drawcounties()
    mp.drawcities(
        labelbuffer=25, textsize=10, color="white", outlinecolor="#000000"
    )
    mp.textmask[:, :] = 0
    mp.plot_values(llons, llats, vals, fmt="%s", labelbuffer=1)

    mp.postprocess(filename="250724.png")


if __name__ == "__main__":
    main()
