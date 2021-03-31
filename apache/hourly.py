"""Simple stats"""
import datetime

from pyiem.plot.use_agg import plt
import matplotlib.dates as mdates


def main():
    """Plot"""
    hits = [0] * 24
    bytes = [0] * 24
    ips = [[] for i in range(24)]
    bad = 0
    for line in open("today.log"):
        tokens = line.split()
        ts = datetime.datetime.strptime(
            tokens[3].split()[0], "[%d/%b/%Y:%H:%M:%S"
        )
        hits[ts.hour] += 1
        try:
            bytes[ts.hour] += float(tokens[9])
        except ValueError:
            bad += 1
        if not tokens[0] in ips[ts.hour]:
            ips[ts.hour].append(tokens[0])
    print(bad)
    for hr in range(24):
        print(
            "%02i %8s %7.3s %5s"
            % (hr, hits[hr], bytes[hr] / 1e9, len(ips[hr]))
        )


if __name__ == "__main__":
    main()
