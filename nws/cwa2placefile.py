"""
Convert the NWS CWA shapefile to a gibson ridge placefile.
"""

import geopandas as gpd


def main():
    """Go Main Go."""
    df = gpd.read_file("w_08mr23.shp")
    # filter for just DMX
    df = df[df["CWA"] == "DMX"]
    # Simplify the geometry to 5 decimal places
    df["geometry"] = df["geometry"].simplify(0.00001)  # type: ignore
    # create a gibson ridge placefile with just the boundaries
    with open("DMX.txt", "w", encoding="utf-8") as fh:
        fh.write(
            """Title: NWS Des Moines County Warning Area
Refresh: 5
Color: 255 255 255
IconFile: 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
Font: 1, 11, 1, "Courier New"
Line: 2, 0, 255, 255, 255
"""
        )
        for _, row in df.iterrows():
            fh.write("Polygon: 2, 0, 0, 0, 0, 0, 255, 255, 255\n")
            for pt in row["geometry"].exterior.coords:
                fh.write("%.5f,%.5f\n" % (pt[1], pt[0]))
            fh.write("End:\n")


if __name__ == "__main__":
    main()
