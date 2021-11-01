"""Humor is the best medicine."""

import matplotlib.pyplot as plt


def main():
    """Go Main Go."""
    fig = plt.figure(figsize=(15, 5), dpi=100)
    ax = fig.add_axes(
        (0.1, 0.2, 0.8, 0.7),
        aspect="auto",
        adjustable="datalim",
    )
    ax.autoscale(False)
    ax.plot([0, 1, 2, 3])
    bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    aspect = bbox.width / bbox.height
    print(f"{aspect=} {ax.get_aspect()=}")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
