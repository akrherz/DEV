"""DEV."""
import matplotlib.colorbar as mpcolorbar
import matplotlib.colors as mpcolors
import matplotlib.pyplot as plt


def main():
    """Go Main Go."""
    cpool = [
        "#cbcb97",
        "#646464",
        "#00ebe7",
        "#00a0f5",
        "#000df5",
        "#00ff00",
        "#00c600",
        "#008e00",
        "#fef700",
        "#e5bc00",
        "#ff8500",
        "#ff0000",
        "#af0000",
        "#640000",
        "#ff00fe",
        "#a152bc",
    ]
    cmap = mpcolors.ListedColormap(cpool, "nwsprecip")
    cmap.set_over("#FFFFFF")
    cmap.set_under("#FFFFFF")
    cmap.set_bad("#FFFFFF")

    clevs = [
        0.01,
        0.1,
        0.3,
        0.5,
        0.75,
        1,
        1.5,
        2.0,
        2.5,
        3.0,
        3.5,
        4,
        5,
        6,
        8,
        10,
    ]
    norm = mpcolors.BoundaryNorm(clevs, cmap.N)

    for c in clevs:
        print(c, norm(c), cmap(norm(c)))

    (fig, ax) = plt.subplots(1, 1)
    mpcolorbar.ColorbarBase(
        ax,
        cmap=cmap,
        norm=norm,
        boundaries=[0] + clevs + [14],
        ticks=clevs,
        extend="both",
        spacing="uniform",
        orientation="vertical",
    )

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
