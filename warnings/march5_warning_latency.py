"""Here we are."""
from datetime import timedelta, timezone

import fiona
import pandas as pd
import geopandas as gpd
from matplotlib.colorbar import ColorbarBase
import matplotlib.colors as mpcolors
from matplotlib.patches import Rectangle
from pyiem.plot import MapPlot, get_cmap
from pyiem.util import get_sqlalchemy_conn, utc

fiona.drvsupport.supported_drivers["LIBKML"] = "rw"

EST_ISSUED = {
    4: utc(2022, 3, 5, 22, 11, 18),
    5: utc(2022, 3, 5, 22, 34, 43),
    7: utc(2022, 3, 5, 23, 5, 51),
    10: utc(2022, 3, 5, 23, 35, 59),
}
DELAYED_ISSUED = {
    4: utc(2022, 3, 5, 22, 18, 4),
    5: utc(2022, 3, 5, 22, 39, 13),
    7: utc(2022, 3, 5, 23, 11, 9),
    10: utc(2022, 3, 5, 23, 41, 16),
}


def main():
    """Go Main Go."""
    # Read in the kmz file
    kmz = gpd.read_file("doc.kml")

    # Get the tornado warnings
    with get_sqlalchemy_conn("postgis") as conn:
        tow = gpd.read_postgis(
            "select geom, eventid, issue at time zone 'utc' as utc_issue, "
            "expire at time zone 'UTC' as utc_expire "
            "from sbw_2022 where wfo = 'DMX' and "
            "phenomena = 'TO' and significance = 'W' and status = 'NEW' and "
            "date(issue) = '2022-03-05' ORDER by eventid",
            conn,
            index_col="eventid",
            geom_col="geom",
        )
    tow["utc_issue"] = tow["utc_issue"].dt.tz_localize(timezone.utc)
    tow["utc_expire"] = tow["utc_expire"].dt.tz_localize(timezone.utc)
    track = kmz.geometry[0]
    track_sts = utc(2022, 3, 5, 22, 26)
    track_ets = utc(2022, 3, 6, 0, 1)
    minutes = int((track_ets - track_sts).total_seconds() / 60.0)
    tow = tow[tow.intersects(track)]
    delayed_issue = pd.Series(DELAYED_ISSUED)
    tow["delay_issue"] = delayed_issue.loc[tow.index]
    est_issue = pd.Series(EST_ISSUED)
    tow["est_issue"] = est_issue.loc[tow.index]

    # Discretize the track into segments, do in UTMZ15N
    utm_track = kmz.to_crs(epsg=26915).geometry[0]
    speed = utm_track.length / minutes * 60.0  # km/hr
    speed_mph = speed * 0.621371 / 1000.0
    rows = []
    for minute in range(minutes + 1):
        # Compute the time of the segment
        valid = track_sts + timedelta(minutes=minute)
        # Compute the distance of the segment
        pt = utm_track.interpolate(minute / minutes * utm_track.length)
        rows.append({"geom": pt, "valid": valid})
    # cmap = get_cmap("gist_rainbow")
    # norm = mpcolors.BoundaryNorm(range(0, 46), cmap.N)

    cmap = get_cmap("plasma")
    norm = mpcolors.BoundaryNorm(range(4, 8), cmap.N)

    pts = gpd.GeoDataFrame(
        rows, columns=["geom", "valid"], geometry="geom", crs="EPSG:26915"
    ).to_crs("EPSG:4326")
    pts["delay_lead"] = -1
    pts["nodelay_lead"] = -1
    for idx, row in pts.iterrows():
        # Find candidate warnings
        ol = tow[tow.intersects(row.geom)]
        valid = row.valid
        # Find ones that overlap in time now
        dol = ol[(ol["delay_issue"] <= valid)]
        delay_issue = dol["delay_issue"].min()
        ndol = ol[(ol["est_issue"] <= valid)]
        nodelay_issue = ndol["est_issue"].min()

        pts.at[idx, "delay_lead"] = (
            row.valid - delay_issue
        ).total_seconds() / 60.0
        pts.at[idx, "nodelay_lead"] = (
            row.valid - nodelay_issue
        ).total_seconds() / 60.0
    pts["delta"] = pts["nodelay_lead"] - pts["delay_lead"]
    pts["color"] = pts["delta"].apply(
        lambda x: cmap(norm(x))[:3] if x > 0 else [0, 0, 0]
    )

    stats = pts["delta"].describe()
    # Time to plot
    bounds = kmz.bounds

    buffer = 0.1
    mp = MapPlot(
        sector="custom",
        title=(
            "Discretized Tornado Warning Decreased Lead Time Due To "
            "Dissemination Latency"
        ),
        subtitle=(
            f"5 March 2022. Assuming constant {speed_mph:.0f} MPH movement, "
            f"Average Lead Time Decrease: {stats['mean']:.0f} minutes"
        ),
        west=bounds.minx.min() - buffer,
        east=bounds.maxx.max() + buffer,
        south=bounds.miny.min() - buffer,
        north=bounds.maxy.max() + buffer,
    )

    # city outlines
    cities = gpd.read_file("../matplotlib/incorporated_cities_2010.shp")
    cities.to_crs("EPSG:4326").plot(
        ax=mp.panels[0].ax,
        aspect=None,
        fc="tan",
        zorder=7,
    )

    kmz.plot(
        ax=mp.panels[0].ax,
        aspect=None,
        lw=4,
        color="#EEEEEE",
        zorder=10,
    )
    pts.plot(
        ax=mp.panels[0].ax,
        aspect=None,
        color=pts["color"],
        zorder=11,
    )
    tow.plot(
        ax=mp.panels[0].ax,
        aspect=None,
        facecolor="None",
        edgecolor="r",
        lw=2,
        zorder=9,
    )
    mp.drawcounties()
    # Draw a color bar
    ncb = ColorbarBase(
        mp.cax,
        norm=norm,
        cmap=cmap,
        extend="neither",
        spacing="uniform",
    )
    ncb.ax.tick_params(labelsize=8)
    ncb.set_label(
        "Lead Time Decrease (minutes)",
    )
    # Create a legend for the warnings
    lng = mp.panels[0].ax.legend(
        [
            Rectangle((0, 0), 1, 1, ec="r", fc="None"),
            Rectangle((0, 0), 1, 1, color="tan"),
        ],
        ["Tornado Warning", "2010 Urban Areas"],
        loc=2,
        framealpha=1,
    )
    lng.set_zorder(12)
    mp.drawcities(labelbuffer=25)
    mp.fig.savefig("test.png")


if __name__ == "__main__":
    main()
