"""Make a plot."""

import matplotlib.pyplot as plt


def main():
    """Go Main Go."""
    counts = []
    xticks = []
    xticklabels = []

    for linenum, line in enumerate(open("data.csv", encoding="utf8")):
        (year, month, count) = line.split(",")
        counts.append(float(count))
        if month == "1" and int(year) % 2 == 0:
            xticks.append(linenum)
            xticklabels.append(year)
    (fig, ax) = plt.subplots(1, 1)

    ax.bar(range(len(counts)), counts, fc="g", ec="g")
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.set_xlim(0, len(counts) + 1)
    ax.grid(True)
    ax.set_title("May 2001 - Aug 2018 :: Spam emails sent by daryl per month")
    ax.set_ylabel("email messages saved to sent-mail")

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
