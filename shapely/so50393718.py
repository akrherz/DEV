"""
https://stackoverflow.com/questions/50393718
"""
from shapely.ops import split
from shapely.geometry import Polygon, LineString, Point


def rhs_split(poly, splitter):
    geomcollect = split(poly, splitter)
    polya, polyb = geomcollect.geoms[0], geomcollect.geoms[1]
    # Test directionality
    pt0 = Point(splitter.coords[0])
    pt1 = Point(splitter.coords[1])
    start_dist = polya.exterior.project(pt0)
    end_dist = polya.exterior.project(pt1)
    # if distance is increasing and not crossing an origin, this is the polygon
    # we are looking for
    splitter_dist_test = abs(pt1.distance(pt0))
    exterior_dist_test = abs(end_dist - start_dist)
    # hack to see if exterior line length is too long and thus origin crossing
    if exterior_dist_test > (splitter_dist_test * 1.00001):
        return polyb
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
