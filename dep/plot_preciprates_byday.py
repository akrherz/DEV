"""Generate a visual showing rainfall rates."""
import calendar

from pyiem.dep import read_cli
from pyiem.plot.use_agg import plt
from metpy.units import units


def main():
    """Go Main Go."""
    df = read_cli("/i/0/cli/091x041/091.48x041.88.cli")
    df["jday"] = df.index.strftime("%j").astype("i")
    df["maxr"] = (df["maxr"].values * units("mm")).to(units("inch")).m
    gdf = df[["jday", "maxr"]].groupby("jday").max()

    (fig, ax) = plt.subplots(1, 1)
    ax.bar(
        gdf.index,
        gdf["maxr"].values,
        width=1,
        facecolor="tan",
        edgecolor="tan",
        zorder=2,
        label="Raw Daily",
    )
    gdf = df[["jday", "maxr"]].groupby("jday").max().rolling(14).mean()
    ax.plot(
        gdf.index,
        gdf["maxr"],
        color="blue",
        zorder=4,
        label="Two Week Smoothed",
    )
    ax.set_xticks([1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335])
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_title(
        (
            "DEP 2007-2019 Maximum Precipitation Rate\n"
            "For 41.88N 91.48W, Hourly Rate extrapolated from 2 minute value."
        )
    )
    ax.legend()
    ax.set_ylabel("Precipitation Rate [in/hr]")
    ax.grid(True)
    ax.set_xlim(60, 182)
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
