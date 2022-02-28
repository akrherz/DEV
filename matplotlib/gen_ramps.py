"""generate ramps used by select2."""
import numpy as np
from pyiem.plot.use_agg import plt


# https://matplotlib.org/stable/tutorials/colors/colormaps.html
cmaps = [
    (
        "Perceptually Uniform Sequential",
        ["viridis", "plasma", "inferno", "magma", "cividis"],
    ),
    (
        "Sequential",
        [
            "Greys",
            "Purples",
            "Blues",
            "Greens",
            "Oranges",
            "Reds",
            "YlOrBr",
            "YlOrRd",
            "OrRd",
            "PuRd",
            "RdPu",
            "BuPu",
            "GnBu",
            "PuBu",
            "YlGnBu",
            "PuBuGn",
            "BuGn",
            "YlGn",
        ],
    ),
    (
        "Sequential (2)",
        [
            "binary",
            "gist_yarg",
            "gist_gray",
            "gray",
            "bone",
            "pink",
            "spring",
            "summer",
            "autumn",
            "winter",
            "cool",
            "Wistia",
            "hot",
            "afmhot",
            "gist_heat",
            "copper",
        ],
    ),
    (
        "Diverging",
        [
            "PiYG",
            "PRGn",
            "BrBG",
            "PuOr",
            "RdGy",
            "RdBu",
            "RdYlBu",
            "RdYlGn",
            "Spectral",
            "coolwarm",
            "bwr",
            "seismic",
        ],
    ),
    ("Cyclic", ["twilight", "twilight_shifted", "hsv"]),
    (
        "Qualitative",
        [
            "Pastel1",
            "Pastel2",
            "Paired",
            "Accent",
            "Dark2",
            "Set1",
            "Set2",
            "Set3",
            "tab10",
            "tab20",
            "tab20b",
            "tab20c",
        ],
    ),
    (
        "Miscellaneous",
        [
            "flag",
            "prism",
            "ocean",
            "gist_earth",
            "terrain",
            "gist_stern",
            "gnuplot",
            "gnuplot2",
            "CMRmap",
            "cubehelix",
            "brg",
            "gist_rainbow",
            "rainbow",
            "jet",
            "turbo",
            "nipy_spectral",
            "gist_ncar",
        ],
    ),
]
gradient = np.linspace(0, 1, 256)
gradient = np.vstack((gradient, gradient))


def main():
    """Go Main Go."""
    for _cmap_category, cmap_list in cmaps:
        for cmap in cmap_list:
            fig, ax = plt.subplots(1, 1, figsize=(2.5, 0.25))
            ax.set_position([0, 0, 1, 1])
            ax.imshow(gradient, aspect="auto", cmap=plt.get_cmap(cmap))
            ax.set_axis_off()
            fig.savefig(f"/mesonet/share/pickup/cmaps/{cmap}.png")
            plt.close()


if __name__ == "__main__":
    main()
