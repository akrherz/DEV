"""Attempt to copy a color ramp."""
from matplotlib.colors import rgb2hex


def main():
    """GO Main Go."""
    colors = []
    for line in open(
        (
            "/usr/lib/python2.6/site-packages/PyNGL/ncarg/"
            + "colormaps/WhiteBlueGreenYellowRed.rgb"
        )
    ):
        tokens = line.split()
        if len(tokens) < 4:
            continue
        if tokens[3] != "#":
            continue
        r, g, b = (
            float(tokens[0]) / 255.0,
            float(tokens[1]) / 255.0,
            float(tokens[2]) / 255.0,
        )
        colors.append(rgb2hex([r, g, b]))

    print(colors)


if __name__ == "__main__":
    main()
