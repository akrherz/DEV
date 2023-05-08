"""
https://stackoverflow.com/questions/50393718

"""
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import split


def rhs_split(poly, splitter):
    intersect_splitter = splitter.intersection(poly)
    geomcollect = split(poly, splitter)
    polya, polyb = geomcollect.geoms[0], geomcollect.geoms[1]
    # Test directionality
    pt0 = Point(intersect_splitter.coords[0])
    pt1 = Point(intersect_splitter.coords[1])
    start_dist = polya.exterior.project(pt0)
    end_dist = polya.exterior.project(pt1)
    return polya if end_dist > start_dist else polyb


print(
    rhs_split(
        Polygon([(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)]),
        LineString([(0.5, -0.1), (0.5, 1.1)]),
    )
)
# POLYGON ((0.5 1, 1 1, 1 0, 0.5 0, 0.5 1))
print(
    rhs_split(
        Polygon([(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)]),
        LineString([(0.5, 1.1), (0.5, -0.1)]),
    )
)
# POLYGON ((0 0, 0 1, 0.5 1, 0.5 0, 0 0))
