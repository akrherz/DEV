"""Lapse the USDM."""
import datetime

from pyiem.plot import MapPlot


def main():
    """Go Main Go."""
    now = datetime.date(2000, 1, 4)
    ets = datetime.date(2021, 5, 19)
    interval = datetime.timedelta(days=7)

    frame = 0
    while now < ets:
        print(now)
        mp = MapPlot(
            sector="conus",
            continentalcolor="white",
            title="%s US Drought Monitor" % (now.strftime("%b %d %Y")),
        )
        mp.draw_usdm(now)
        mp.postprocess(filename="images/%05d.png" % (frame,))
        mp.close()
        frame += 1
        now += interval


if __name__ == "__main__":
    main()
