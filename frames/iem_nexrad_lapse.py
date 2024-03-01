"""Pretty things."""

import datetime
from zoneinfo import ZoneInfo

import geopandas as gpd
import matplotlib.colors as mpcolors
import pandas as pd
from matplotlib.colorbar import ColorbarBase
from pyiem.plot import MapPlot, get_cmap
from pyiem.reference import Z_OVERLAY2
from pyiem.util import get_sqlalchemy_conn, utc

CST = ZoneInfo("America/Chicago")
# geoplot.MAIN_AX_BOUNDS = [0.05, 0.3, 0.89, 0.6]


def main():
    """Go Main Go."""
    sts = utc(2022, 3, 5, 17)
    ets = utc(2022, 3, 6, 4, 0)
    interval = datetime.timedelta(minutes=5)
    i = 0
    now = sts
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            "SELECT distinct ST_x(geom) as lon, ST_y(geom) as lat, typetext, "
            "valid at time zone 'UTC' as valid, magnitude from lsrs_2022 "
            "where valid >= %s and valid < %s ORDER by magnitude ASC",
            conn,
            params=(sts, ets),
        )
        df["valid"] = df["valid"].dt.tz_localize("UTC")
        print(df["magnitude"].describe())
        warndf = gpd.read_postgis(
            "SELECT phenomena, geom, issue at time zone 'UTC' as issue, "
            "expire at time zone 'UTC' as expire from sbw_2022 where "
            "status = 'NEW' and expire >= %s and issue <= %s and "
            "phenomena in ('TO', 'SV')",
            conn,
            params=(sts, ets),
            geom_col="geom",
        )
    warndf["color"] = "yellow"
    warndf.loc[warndf["phenomena"] == "TO", "color"] = "red"
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

    while now < ets:
        mp = MapPlot(
            sector="custom",
            west=-99.5,
            east=-90,
            south=39.5,
            north=43.5,
            # dark gray color
            continentalcolor="#808080",
            statebordercolor="white",
            title=(
                f"5 March 2022 {now.astimezone(CST).strftime('%I:%M %p %Z')}"
            ),
            subtitle=("NWS NEXRAD, SVR+TORs, Unfiltered Local Storm Reports"),
            twitter=True,
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
        # ax = mp.fig.add_axes([0.1, 0.1, 0.8, 0.15], facecolor="tan")

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
                # fmt="%.1f",
                # color=df2["color"].to_list(),
                # labeltextsize=8,
                labelbuffer=0,
            )
        df2 = df[(df["valid"] <= now) & (df["typetext"] == "HAIL")]
        if not df2.empty:
            mp.plot_values(
                df2["lon"].values,
                df2["lat"].values,
                df2["magnitude"].values,
                color="darkgreen",
                outlinecolor="lightgreen",
                labeltextsize=14,
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
                labeltextsize=14,
                labelbuffer=0,
            )
        """
        df2 = df[(df["valid"] <= now) & (df["typetext"] == "TORNADO")]
        if not df2.empty:
            mp.panels[0].ax.scatter(
                df2["lon"].values,
                df2["lat"].values,
                s=60,
                marker="v",
                facecolor="r",
                edgecolor="white",
                zorder=Z_OVERLAY2,
            )
            ax.scatter(
                df2["valid"].values,
                [55] * len(df2.index),
                facecolor="r",
                edgecolor="white",
                marker="v",
                zorder=Z_OVERLAY2,
            )
        ax.scatter(
            [
                0.024,
            ],
            [
                0.93,
            ],
            facecolor="r",
            edgecolor="k",
            marker="v",
            transform=ax.transAxes,
        )
        ax.text(
            0.03, 0.96, "Tornado", transform=ax.transAxes, ha="left", va="top"
        )
        """
        df2 = warndf[(warndf["issue"] <= now) & (warndf["expire"] > now)]
        if not df2.empty:
            df2.plot(
                ax=mp.panels[0].ax,
                aspect=None,
                edgecolor=df2["color"].to_list(),
                facecolor="None",
                zorder=Z_OVERLAY2,
                lw=2,
            )
        mp.fig.text(
            0.92,
            0.3,
            "Tornado\nReports",
            color="r",
        )
        mp.fig.text(
            0.92,
            0.37,
            "Hail (inch)\nReports",
            color="darkgreen",
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
        mp.drawcounties("k")
        mp.fig.savefig(f"images/{i:05d}.png")
        mp.close()
        i += 1
        now += interval


if __name__ == "__main__":
    main()
