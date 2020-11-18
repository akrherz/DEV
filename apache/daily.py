"""barplot of daily requests"""
import datetime

from pyiem.plot.use_agg import plt
import matplotlib.dates as mdates


def main():
    """Plot"""
    hits = {}
    for line in open("KBRO.log"):
        tokens = line.split()
        ts = datetime.datetime.strptime(
            tokens[3].split()[0], "[%d/%b/%Y:%H:%M:%S"
        )
        yyyymmdd = ts.strftime("%Y%m%d")
        if yyyymmdd not in hits:
            hits[yyyymmdd] = 0
        hits[yyyymmdd] += 1

    keys = hits.keys()
    keys.sort()
    xs = []
    ys = []
    for yyyymmdd in keys:
        if yyyymmdd == "20170825":
            continue
        date = datetime.datetime.strptime(yyyymmdd, "%Y%m%d")
        xs.append(date)
        ys.append(hits[yyyymmdd])

    (fig, ax) = plt.subplots(1, 1)
    ax.bar(xs, ys)
    ax.grid(True)
    ax.set_ylabel("Website Requests")
    ax.set_xlim(
        datetime.datetime(2017, 7, 23, 12), datetime.datetime(2017, 8, 25)
    )
    ax.set_title(
        "IEM NEXRAD Level II Download Website (24 Jul - 24 Aug 2017)\n"
        "Daily Requests for KBRO Brownsville Level II Data"
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-d\n%b"))
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
