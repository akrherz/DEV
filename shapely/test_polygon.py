"""See what shapely says."""

from shapely.geometry import LinearRing, Polygon


def main():
    """Go Main Go."""
    X = [-77.66, -77.45, -77.5, -77.73, -77.81, -77.81, -77.77, -77.66]
    Y = [35.5, 35.44, 35.39, 35.45, 35.59, 35.58, 35.61, 35.5]

    lr = LinearRing(zip(X, Y, strict=False))
    assert lr.is_valid

    poly = Polygon(lr)
    assert poly.is_valid


if __name__ == "__main__":
    main()
