"""Pretty things."""

import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import text
from tqdm import tqdm

import geopandas as gpd
import matplotlib.colors as mpcolors
import matplotlib.dates as mdates
import pandas as pd
from matplotlib.colorbar import ColorbarBase
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import MapPlot, geoplot, get_cmap
from pyiem.reference import Z_OVERLAY2
from pyiem.util import utc

CST = ZoneInfo("America/Chicago")
geoplot.MAIN_AX_BOUNDS = [0.05, 0.3, 0.89, 0.6]


def main():
    """Go Main Go."""
    sts = utc(2024, 7, 15, 20)
    ets = utc(2024, 7, 16, 6)
    interval = datetime.timedelta(minutes=5)
    i = 0
    now = sts
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            text(
                "SELECT distinct ST_x(geom) as lon, ST_y(geom) as lat, "
                "typetext, "
                "valid at time zone 'UTC' as valid, magnitude from lsrs "
                "where valid >= :sts and valid < :ets ORDER by magnitude ASC"
            ),
            conn,
            params={"sts": sts, "ets": ets},
        )
        df["valid"] = df["valid"].dt.tz_localize("UTC")
        print(df["magnitude"].describe())
        warndf = gpd.read_postgis(
            text(
                "SELECT phenomena, geom, issue at time zone 'UTC' as issue, "
                "expire at time zone 'UTC' as expire from sbw_2024 where "
                "status = 'NEW' and expire >= :sts and issue <= :ets and "
                "phenomena in ('TO', 'SV', 'MA') and significance = 'W'"
            ),
            conn,
            params={"sts": sts, "ets": ets},
            geom_col="geom",
        )
        print(f"Warnings found {len(warndf.index)}")
    warndf["color"] = "yellow"
    warndf.loc[warndf["phenomena"] == "TO", "color"] = "red"
    warndf.loc[warndf["phenomena"] == "MA", "color"] = "green"
    warndf["issue"] = warndf["issue"].dt.tz_localize("UTC")
    warndf["expire"] = warndf["expire"].dt.tz_localize("UTC")

    # nldn = gpd.read_postgis(
    #    "SELECT geom, valid at time zone 'UTC' as valid from nldn2021_12 "
    #    "WHERE valid >= %s and valid < %s",
    #    get_dbconn("nldn"),
    #    params=(sts, ets),
    # )
    # nldn["valid"] = nldn["valid"].dt.tz_localize("UTC")
    # nldn = nldn.to_crs(epsg=4326)

    cmap = get_cmap("cool")
    bins = list(range(50, 101, 10))
    norm = mpcolors.BoundaryNorm(bins, cmap.N)

    def f(val):
        return cmap(norm(val))

    df["color"] = df["magnitude"].apply(f)

    ncmap = get_cmap("binary_r")
    ncmap.set_under("#00000000")
    ncmap.set_over("white")
    nbins = list(range(0, 121, 10))
    nbins[0] = 1
    mpcolors.BoundaryNorm(nbins, ncmap.N)

    progress = tqdm(pd.date_range(sts, ets, freq=interval))
    for now in progress:
        progress.set_description(now.strftime("%Y-%m-%d %H:%M"))
        mp = MapPlot(
            sector="spherical_mercator",
            west=-93.5,
            east=-88.0,
            south=38.5,
            north=42.5,
            # dark gray color
            continentalcolor="#808080",
            statebordercolor="k",
            stateborderwitdth=2,
            title=(f"{now.astimezone(CST):%d %b %Y %I:%M %p %Z}"),
            subtitle="NWS NEXRAD, SVR+TORs, Unfiltered Local Storm Reports",
            figsize=(10.24, 7.68),
            caption="@akrherz",
        )
        """
        df2 = nldn[nldn["valid"] <= now]
        # ~ 2254 km x 973 km  2.32x about 24km2 grid
        mp.panels[0].ax.hexbin(
            df2["geom"].x,
            df2["geom"].y,
            cmap=ncmap,
            norm=nnorm,
            zorder=Z_FILL - 1,
            extent=mp.panels[0].get_extent(),
            gridsize=(92, 40),
        )
        ncax = mp.fig.add_axes(
            [0.92, 0.3, 0.02, 0.2],
            frameon=True,
            facecolor="#EEEEEE",
            yticks=[],
            xticks=[],
        )

        ncb = ColorbarBase(
            ncax, norm=nnorm, cmap=ncmap, extend="max", spacing="proportional"
        )
        ncb.set_label(
            "Strikes per ~24 km cell, courtesy Vaisala NLDN",
            loc="bottom",
        )
        """
        mp.overlay_nexrad(now)
        ax = mp.fig.add_axes([0.075, 0.1, 0.8, 0.15], facecolor="tan")

        df2 = df[(df["valid"] <= now) & (df["typetext"] == "HAIL")]
        if not df2.empty:
            mp.plot_values(
                df2["lon"].values,
                df2["lat"].values,
                df2["magnitude"].values,
                color="darkgreen",
                outlinecolor="lightgreen",
                textsize=8,
                labelbuffer=0,
            )
        df2 = df[(df["valid"] <= now) & (df["typetext"] == "TORNADO")]
        if not df2.empty:
            mp.plot_values(
                df2["lon"].values,
                df2["lat"].values,
                ["T"] * len(df2.index),
                color="r",
                outlinecolor="yellow",
                textsize=8,
                labelbuffer=0,
            )
        df2 = df[(df["valid"] <= now) & (df["typetext"] == "TSTM WND GST")]
        if not df2.empty:
            mp.scatter(
                df2["lon"].values,
                df2["lat"].values,
                df2["magnitude"].values,
                bins,
                cmap=cmap,
                norm=norm,
                draw_colorbar=False,
                edgecolor="white",
                fmt="%.0f",
                color=df2["color"].to_list(),
                textsize=8,
                labelbuffer=0,
            )
            ax.bar(
                df2["valid"].values,
                df2["magnitude"].values,
                color=df2["color"].to_list(),
                width=5 / 1440.0,  # 5 minutes
            )
        df2 = warndf[(warndf["issue"] <= now) & (warndf["expire"] > now)]
        if not df2.empty:
            df2.to_crs(mp.panels[0].crs).plot(
                ax=mp.panels[0].ax,
                aspect=None,
                edgecolor=df2["color"].to_list(),
                facecolor="None",
                zorder=Z_OVERLAY2,
                lw=2,
            )
        mp.fig.text(
            0.92,
            0.34,
            "Tornado\nReports",
            color="r",
            bbox=dict(color="white"),
        )
        mp.fig.text(
            0.92,
            0.41,
            "Hail (inch)\nReports",
            color="darkgreen",
            bbox=dict(color="white"),
        )
        cax2 = mp.fig.add_axes(
            [0.91, 0.05, 0.02, 0.2],
            frameon=False,
            yticks=[],
            xticks=[],
        )

        cb = ColorbarBase(
            cax2,
            norm=norm,
            cmap=cmap,
            extend="neither",
            spacing="proportional",
        )
        cb.set_label(
            "Wind Gust [MPH]",
            loc="bottom",
        )
        ax.axvline(now, color="k", lw=1)
        ax.set_xlim(sts, ets)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%-I %p", tz=CST))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        ax.set_xlabel(
            "16-17 July 2024 Central Daylight Time, 5 minute bar width"
        )
        ax.set_yticks(range(50, 111, 10))
        ax.set_ylim(50, 110)
        ax.set_ylabel("Wind Gust [MPH]")
        ax.set_title("NWS Thunderstorm Wind Gust Reports [MPH]")
        ax.grid(True)
        # mp.drawcounties("k")
        mp.fig.savefig(f"images/{i:05d}.png")
        mp.close()
        i += 1


if __name__ == "__main__":
    main()
