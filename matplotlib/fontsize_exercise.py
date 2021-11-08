"""What to do about fontsize in my plots."""

import matplotlib.pyplot as plt


def main():
    """Go Main Go."""
    figsize = (6, 4)
    dpi = 200
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    res = ax.text(0.5, 0.5, "Hello Daryl!", ha="center")
    print(res.get_fontsize())
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
