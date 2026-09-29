"""webfarm hits"""

import datetime

from pyiem.plot import figure_axes


def main():
    """Go Main"""
    xs = []
    ys = []
    for line in open("hits.txt"):
        tokens = line.split(":")
        ts = datetime.datetime.strptime(tokens[0], "%d %b %Y")
        xs.append(ts)
        ys.append(int(tokens[1]))

    fig, ax = figure_axes(
        figsize=(8, 6),
        title="IEM Daily Web Requests Milestones [17 Jun 2001-2026]",
    )
    ax.set_position((0.1, 0.2, 0.8, 0.7))

    ax.semilogy(xs, ys, lw=3)
    # ax.set_xlim( x[0].ticks(), x[-1].ticks() )
    xticks = []
    xticklabels = []
    ts0 = datetime.datetime(2001, 1, 1)
    ts1 = datetime.datetime(2026, 9, 24)
    interval = datetime.timedelta(days=1)
    now = ts0
    while now < ts1:
        if now.day == 1 and now.month == 1:
            xticks.append(now)
            xticklabels.append(now.strftime("%Y"))
        now += interval
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels, fontsize=18, rotation=90)
    ax.set_xlabel("Year", fontsize=18)
    ax.set_ylabel("Maximum Daily Web Requests", fontsize=20)
    ax.grid(True)
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
