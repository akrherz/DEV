"""Graphic showing leadtime."""

from datetime import timedelta, timezone
from zoneinfo import ZoneInfo

import fiona

import geopandas as gpd
import matplotlib.colors as mpcolors
from matplotlib.colorbar import ColorbarBase
from matplotlib.patches import Rectangle
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import MapPlot, get_cmap
from pyiem.util import utc

fiona.drvsupport.supported_drivers["LIBKML"] = "rw"
CentralTZ = ZoneInfo("America/Chicago")


def main():
    """Go Main Go."""
    # Read in the kmz file
    kmz = gpd.read_file("doc.kml")

    # Get the tornado warnings
    with get_sqlalchemy_conn("postgis") as conn:
        tow = gpd.read_postgis(
            "select geom, eventid, issue at time zone 'utc' as utc_issue, "
            "expire at time zone 'UTC' as utc_expire "
            "from sbw_2024 where wfo = 'DMX' and "
            "phenomena = 'TO' and significance = 'W' and status = 'NEW' and "
            "date(issue) = '2024-05-21' ORDER by eventid asc",
            conn,
            index_col="eventid",
            geom_col="geom",
        )
    tow["hit"] = False
    tow["utc_issue"] = tow["utc_issue"].dt.tz_localize(timezone.utc)
    tow["utc_expire"] = tow["utc_expire"].dt.tz_localize(timezone.utc)
    track = kmz.geometry[0]
    track_sts = utc(2024, 5, 21, 21, 30)
    track_ets = utc(2024, 5, 21, 22, 5)
    minutes = int((track_ets - track_sts).total_seconds() / 60.0)
    tow = tow[tow.intersects(track)]

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
    cmap = get_cmap("gist_rainbow")
    cmap.set_under("k")
    bins = list(range(0, 31, 5))
    bins[0] = 1
    norm = mpcolors.BoundaryNorm(bins, cmap.N)

    pts = gpd.GeoDataFrame(
        rows, columns=["geom", "valid"], geometry="geom", crs="EPSG:26915"
    ).to_crs("EPSG:4326")
    pts["lead"] = -1
    for idx, row in pts.iterrows():
        # Find candidate warnings
        ol = tow[tow.intersects(row.geom)]
        valid = row.valid
        # Find ones that overlap in time now
        dol = ol[(ol["utc_issue"] <= valid) & (ol["utc_expire"] >= valid)]

        pts.at[idx, "lead"] = (
            row.valid - dol.iloc[0].utc_issue
        ).total_seconds() / 60.0
    pts["color"] = pts["lead"].apply(
        lambda x: cmap(norm(x))[:3] if x > 0 else [0, 0, 0]
    )

    stats = pts["lead"].describe()
    # Time to plot
    bounds = tow.bounds

    buffer = 0.01
    mp = MapPlot(
        sector="custom",
        title=("Estimated Tornado Warning Lead Time Along Tornado Track"),
        subtitle=(
            f"Polk-Story County Tornado 21 May 2024. "
            f"Assuming constant {speed_mph:.0f} MPH movement, "
            f"Average Lead Time: {stats['mean']:.0f} minutes"
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
        lw=2,
        alpha=0.2,
        color="k",
        zorder=10,
    )
    pts.plot(
        ax=mp.panels[0].ax,
        aspect=None,
        color=pts["color"],
        zorder=11,
    )
    # label the first and last point on the track with the timestamps
    for idx in [0, -1]:
        label = "Start" if idx == 0 else "End"
        tt = pts.iloc[idx].valid.astimezone(CentralTZ).strftime("%-I:%M %p")
        mp.panels[0].ax.annotate(
            f"{label} {tt}",
            xy=(pts.iloc[idx].geom.x, pts.iloc[idx].geom.y),
            xytext=(-10, 30),
            textcoords="offset points",
            ha="center",
            color="k",
            arrowprops=dict(facecolor="black", shrink=0.05),
            bbox=dict(color="white", alpha=0.8, boxstyle="round,pad=0.1"),
            zorder=13,
        )

    tow.plot(
        ax=mp.panels[0].ax,
        aspect=None,
        facecolor="r",
        edgecolor="r",
        alpha=0.2,
        lw=2,
        zorder=9,
    )
    # draw some fancy labels for these warnings
    yloc = 0.5
    for eventid, row in tow.iterrows():
        label = "Tor Warning #%s\n%s till %s" % (
            eventid,
            row["utc_issue"].astimezone(CentralTZ).strftime("%-I:%M %p"),
            row["utc_expire"].astimezone(CentralTZ).strftime("%-I:%M %p"),
        )
        mp.panels[0].ax.annotate(
            label,
            xy=(row["geom"].centroid.x, row["geom"].centroid.y),
            xytext=(0.1, yloc),
            textcoords="axes fraction",
            arrowprops=dict(facecolor="black", shrink=0.05, width=2),
            bbox=dict(color="#f1bebe", boxstyle="round,pad=0.1"),
            ha="center",
            color="k",
            zorder=12,
        )
        yloc += 0.2
    mp.drawcounties()
    # Draw a color bar
    ncb = ColorbarBase(
        mp.cax,
        norm=norm,
        cmap=cmap,
        extend="min",
        spacing="uniform",
    )
    ncb.ax.tick_params(labelsize=8)
    ncb.set_label(
        "Lead Time (minutes)",
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
    mp.fig.savefig("240523.png")


if __name__ == "__main__":
    main()
