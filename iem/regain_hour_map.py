"""Plot the scam that is DST"""

import ephem
import mx.DateTime
import tqdm
from pyiem.plot import MapPlot


def compute_sunrise(lat, long):
    arr = []
    sun = ephem.Sun()
    ames = ephem.Observer()
    ames.lat = lat
    ames.long = long
    sts = mx.DateTime.DateTime(2018, 3, 10)
    interval = mx.DateTime.RelativeDateTime(days=1)
    now = sts
    doy = []
    returnD = 0
    ames.date = now.strftime("%Y/%m/%d")
    rise = mx.DateTime.strptime(
        str(ames.next_rising(sun)), "%Y/%m/%d %H:%M:%S"
    )
    rise = rise.localtime()
    delta = rise.hour * 60 + rise.minute
    now += interval
    while True:
        ames.date = now.strftime("%Y/%m/%d")
        rise2 = mx.DateTime.strptime(
            str(ames.next_rising(sun)), "%Y/%m/%d %H:%M:%S"
        )
        rise2 = rise2.localtime()
        delta2 = rise2.hour * 60 + rise2.minute
        if delta2 < delta:
            return (rise2 - rise).days

        now += interval

    return doy, arr, returnD


def main():
    """Go Main Go."""
    lats = []
    lons = []
    vals = []
    for lon in tqdm.tqdm(range(-130, -60, 2)):
        for lat in range(20, 55, 1):
            lats.append(lat)
            lons.append(lon)
            vals.append(compute_sunrise(str(lat), str(lon)))

    m = MapPlot(
        sector="conus",
        title="Days to Recover Morning Hour after Spring Saving Time Change",
        subtitle=(
            "days until local time of sunrise is earlier "
            "than on 10 March, local DST rules ignored for plot"
        ),
    )
    m.contourf(lons, lats, vals, range(27, 78, 3), units="days")
    m.postprocess(filename="180313.png")


if __name__ == "__main__":
    main()
