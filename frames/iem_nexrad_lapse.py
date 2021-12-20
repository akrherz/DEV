"""Pretty things."""
import datetime
from backports.zoneinfo import ZoneInfo

from matplotlib.colorbar import ColorbarBase
import matplotlib.dates as mdates
import matplotlib.colors as mpcolors
import geopandas as gpd
from matplotlib.pyplot import angle_spectrum
from pandas.io.sql import read_sql
from pyiem.plot import MapPlot, get_cmap, geoplot
from pyiem.util import utc, get_dbconn, convert_value
from pyiem.reference import Z_OVERLAY2

CST = ZoneInfo("America/Chicago")
geoplot.MAIN_AX_BOUNDS = [0.05, 0.3, 0.89, 0.6]


def main():
    """Go Main Go."""
    sts = utc(2021, 12, 15, 18)
    ets = utc(2021, 12, 16, 5, 56)
    interval = datetime.timedelta(minutes=5)
    i = 0
    now = sts
    df = read_sql(
        "SELECT distinct ST_x(geom) as lon, ST_y(geom) as lat, "
        "valid at time zone 'UTC' as valid, magnitude from lsrs_2021 where "
        "valid >= %s and valid < %s and typetext = 'TSTM WND GST' and "
        "magnitude >= 50 ORDER by magnitude ASC",
        get_dbconn("postgis"),
        params=(sts, ets),
    )
    df["valid"] = df["valid"].dt.tz_localize("UTC")
    df["magnitude"] = convert_value(df["magnitude"].values, "knot", "mph")
    warndf = gpd.read_postgis(
        "SELECT phenomena, geom, issue at time zone 'UTC' as issue, "
        "expire at time zone 'UTC' as expire from sbw_2021 where "
        "status = 'NEW' and expire >= %s and issue <= %s and "
        "phenomena in ('TO', 'SV')",
        get_dbconn("postgis"),
        params=(sts, ets),
        geom_col="geom",
    )
    warndf["color"] = "yellow"
    warndf.loc[warndf["phenomena"] == "TO", "color"] = "red"
    warndf["issue"] = warndf["issue"].dt.tz_localize("UTC")
    warndf["expire"] = warndf["expire"].dt.tz_localize("UTC")

    print(df["magnitude"].describe())

    cmap = get_cmap("cool")
    bins = list(range(50, 111, 10))
    norm = mpcolors.BoundaryNorm(bins, cmap.N)

    def f(val):
        return cmap(norm(val))

    df["color"] = df["magnitude"].apply(f)

    while now < ets:
        mp = MapPlot(
            sector="custom",
            west=-103.5,
            east=-87,
            south=36.0,
            north=46.0,
            continentalcolor="k",
            statebordercolor="white",
            title="15 Dec 2021 Serial Derecho",
            subtitle=(
                f"{now.astimezone(CST).strftime('%I:%M %p %Z')}, "
                "NWS NEXRAD, SVR+TOR Warns, T-Storm Wind LSRs"
            ),
            twitter=True,
            caption="@akrherz",
        )
        mp.overlay_nexrad(now)
        ax = mp.fig.add_axes([0.1, 0.1, 0.8, 0.15], facecolor="tan")

        df2 = df[df["valid"] <= now]
        if not df2.empty:
            mp.scatter(
                df2["lon"].values,
                df2["lat"].values,
                df2["magnitude"].values,
                bins,
                cmap=cmap,
                # fmt="%.1f",
                # color=df2["color"].to_list(),
                # labeltextsize=8,
                # labelbuffer=0,
            )
            ax.bar(
                df2["valid"].values,
                df2["magnitude"].values,
                color=df2["color"].to_list(),
                width=15 / 1440.0,  # 15 minutes
            )
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
        cax = mp.fig.add_axes(
            [0.91, 0.05, 0.02, 0.2],
            frameon=False,
            yticks=[],
            xticks=[],
        )

        cb = ColorbarBase(
            cax, norm=norm, cmap=cmap, extend="neither", spacing="proportional"
        )
        cb.set_label(
            "Wind Gust [MPH]",
            loc="bottom",
        )
        ax.axvline(now, color="k", lw=1)
        ax.set_xlim(sts, ets)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%-I %p", tz=CST))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        ax.set_xlabel("15 Dec 2021 Central Standard Time, 5 minute bar width")
        ax.set_ylim(50, 110)
        ax.set_ylabel("Wind Gust [MPH]")
        ax.set_title("NWS Thunderstorm Wind Gust Reports [MPH]")
        ax.grid(True)

        mp.fig.savefig(f"images/{i:05d}.png")
        mp.close()
        i += 1
        now += interval


if __name__ == "__main__":
    main()
