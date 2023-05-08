"""Generate a feature plot."""

import numpy as np
from PIL import Image

from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot, nwsprecip
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor()

    cursor.execute(
        """SELECT ST_x(geom) as lon, ST_y(geom) as lat,
    pday from summary_2022 s JOIN stations t on (s.iemid = t.iemid)
    where day = '2022-06-15' and network in
    ('IACOCORAHS', 'WI_COOP', 'MN_COOP', 'IA_COOP')
    and pday > 0 ORDER by pday DESC"""
    )
    llons = []
    llats = []
    vals = []
    for row in cursor:
        llons.append(row[0])
        llats.append(row[1])
        vals.append("%.2f" % (row[2],))

    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()

    cursor.execute(
        """SELECT ST_x(geom) as lon, ST_y(geom) as lat,
    max(magnitude) from lsrs_2022
    where wfo in ('DMX', 'DVN', 'ARX') and typetext = 'HEAVY RAIN' and
    valid > '2022-06-15' GROUP by lon, lat ORDER by max DESC"""
    )
    for row in cursor:
        llons.append(row[0])
        llats.append(row[1])
        vals.append("%.2f" % (row[2],))

    img = Image.open("/tmp/p24h_202206151700.png")
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
        west=-94.2,
        east=-93.1,
        south=41.7,
        north=42.2,
        title="NOAA MRMS 24 Hour RADAR-Only Precipitation Estimate",
        subtitle=(
            "MRMS valid 12 PM 14 Jun 2022 to 12 PM 15 Jun 2022, "
            "NWS Local Storm + COOP Reports Overlaid"
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

    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
