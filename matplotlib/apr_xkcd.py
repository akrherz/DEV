"""Humor is the best medicine."""

import matplotlib.pyplot as plt
from pyiem.reference import TWITTER_RESOLUTION_INCH as T


def main():
    """Go Main Go."""
    y = [0.5, 0.86, 0.2, 0.1, 0.8, 0.7, 0.8, 0.6, 0.6, 2.5]
    y.extend([4.5, 4.2, 4.1, 4.8, 3, 0.6, 0.7, 0.1, 0.4, 0.5])
    fig = plt.figure(figsize=(T[0] / 2, T[1] / 2))
    ax = fig.add_axes((0.1, 0.2, 0.8, 0.7))
    ax.spines.right.set_color("none")
    ax.spines.top.set_color("none")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_ylabel("Temperature")
    ax.set_title("Ames Weather")
    ax.axhspan(4, 5, fc="r", alpha=0.3)
    ax.text(17, 4.5, "Too Hot!", ha="center", color="r")
    ax.axhspan(1, 4, fc="g", alpha=0.3)
    ax.text(14, 2.0, "Just Right!", ha="center", color="g")
    ax.axhspan(0, 1, fc="b", alpha=0.3)
    ax.text(12, 0.5, "Too Cold!", ha="center", color="b")
    ax.scatter(range(20), y)
    ax.set_xlabel("Days This Year or Any Year")

    fig.savefig("210401.png")


if __name__ == "__main__":
    with plt.xkcd():
        main()
