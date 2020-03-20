"""Dump events for our enjoyment"""
from __future__ import print_function
import sys

import tqdm
import numpy as np
import pandas as pd
from pandas.io.sql import read_sql
import matplotlib.pyplot as plt
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn
from pyiem.datatypes import temperature


def calc(T, Td):
    pSFC = 1000
    #
    #   set constants
    c1 = 0.0091379024
    c2 = 6106.396
    f = 0.0006355
    #
    #   convert T and Td to degrees K
    Td = np.where(np.greater_equal(Td, T), (T), Td)
    tK = temperature(T, "F").value("K")
    tdK = temperature(Td, "F").value("K")
    #
    #   convert T and Td to degrees C
    tC = tK - 273.15
    tdC = tdK - 273.15
    #
    #   calculate saturation vapor pressures using the
    #   Bolton (1980) form of the Clausius-Clapeyron Equation
    es = 6.112 * np.exp((17.67 * tC) / (tC + 243.5))
    #
    #   calculate dewpoint vapor pressures
    ed = 6.112 * np.exp((17.67 * tdC) / (tdC + 243.5))
    #   compute dewpoint depression
    dewptDep = tK - tdK
    #
    #   clip to avoid divide-by-zero
    ##           dewptDep = where(less_equal(dewptDep, 0.0), 0.00001, dewptDep)
    dewptDep = np.where(np.less_equal(dewptDep, 0.0), 0.1, dewptDep)
    #
    #   s is an intermediate in the Tw calculation
    s = (es - ed) / (dewptDep)
    #
    #   calculate first guess Tw
    tW = ((tK * f * pSFC) + (tdK * s)) / ((f * pSFC) + s)
    #
    #       where f is the constant Cp/0.622Lv
    #
    #    Solve for tW iteratively by attempting an energy balance
    #    Ten steps should be sufficient
    for i in xrange(0, 10, 1):
        #
        #       convert to deg C
        tWC = tW - 273.15
        #
        #       calculate wet bulb vapor pressures
        ew = 6.112 * np.exp((17.67 * tWC) / (tWC + 243.5))
        #
        #       calculate difference values (after Iribarne and Godson (1981))
        de = (f * pSFC * (tK - tW)) - (ew - ed)
        #
        #       take derivative of difference value w.r.t. Tw to find zero value of function
        der = (ew * (c1 - (c2 / tW ** 2))) - (f * pSFC)
        #
        #       calculate next guess of tW
        tW = tW - (de / der)
        #
        #   Convert wet bulb back to deg F
    Twk = temperature(tW, "K").value("F")
    Twk = np.where(np.greater_equal(Twk, 200.0), (Twk - 273.15), Twk)
    ## self.createGrid('Fcst', 'WetBulb', 'SCALAR',(Twk), self._timm)
    # WetBulb grid calculation
    return Twk


def grouper():
    """Go Plot2"""
    df = pd.read_csv("events.csv")
    rows = []
    for (tmpf, dwpf), gdf in df[
        ((df["vaid"].dt.year >= decade) & (df["vaid"].dt.year < (decade + 10)))
    ].groupby(["tmpf", "dwpf"]):
        gdf2 = gdf.groupby("event").count()
        snowcount = 0
        raincount = 0
        for idx in gdf2.index:
            if idx.find("SN") > 0:
                snowcount += gdf2.at[idx, "station"]
            elif idx.find("RA") > 0:
                raincount += gdf2.at[idx, "station"]
        rows.append(
            dict(
                tmpf=tmpf, dwpf=dwpf, snowcount=snowcount, raincount=raincount
            )
        )

    newdf = pd.DataFrame(rows)
    newdf.to_csv("events_grouped.csv", index=False)


def plot():
    """Make a plot"""
    df = pd.read_csv("events.csv")
    df["wetbulb"] = calc(df["tmpf"].values, df["dwpf"].values)
    df2 = df[df["zr"]]
    (fig, ax) = plt.subplots(2, 1, sharex=True)
    fig.text(
        0.5, 0.95, "Frequency of Freezing Rain (ZR) 1997-2017", ha="center"
    )
    hist, xedges, yedges = np.histogram2d(
        df2["tmpf"].values, df2["dwpf"].values, np.arange(-20.5, 40.5, 1)
    )
    hist = np.ma.array(hist)
    hist.mask = np.ma.where(hist < 1, True, False)
    # ax.scatter(df['tmpf'], df['dwpf'])
    res = ax[0].pcolormesh(xedges, yedges, hist.T)
    ax[0].grid(True)
    ax[0].set_ylabel("Dew Point Temp F")
    ax[0].set_ylim(20, 40)
    ax[0].set_xticks(range(21, 41, 2))
    ax[0].set_yticks(range(21, 41, 2))
    fig.colorbar(res, ax=ax[0], label="events")

    hist, xedges, yedges = np.histogram2d(
        df2["tmpf"].values, df2["wetbulb"].values, np.arange(-20.5, 40.5, 1)
    )
    hist = np.ma.array(hist)
    hist.mask = np.ma.where(hist < 1, True, False)
    # ax.scatter(df['tmpf'], df['dwpf'])
    res = ax[1].pcolormesh(xedges, yedges, hist.T)
    ax[1].grid(True)
    ax[1].set_xlabel("Air Temperature F")
    ax[1].set_ylabel("Wet Bulb Temp F")
    ax[1].set_xlim(20, 40)
    ax[1].set_xticks(range(21, 41, 2))
    ax[1].set_yticks(range(21, 41, 2))
    ax[1].set_ylim(20, 40)
    fig.colorbar(res, ax=ax[1], label="events")
    fig.savefig("test.png")


def plot4():
    df = pd.read_csv("events.csv")
    df["wetbulb"] = calc(df["tmpf"].values, df["dwpf"].values)
    df["i_wetbulb"] = df["wetbulb"].astype("i")
    (fig, ax) = plt.subplots(1, 1)

    labels = {
        "i_wetbulb": "Wet Bulb",
        "dwpf": "Dew Point",
        "tmpf": "Air Temperature",
    }
    for state in df["state"].unique():
        gdf = df[df["state"] == state].groupby("i_wetbulb").sum()
        total = gdf["snow"] + gdf["zr"] + gdf["rain"]
        ax.plot(gdf.index.values, gdf["snow"] / total * 100.0, label=state)
    ax.grid(True)
    ax.legend(loc=6)
    ax.set_xticks(range(20, 41, 2))
    ax.set_xlim(20, 40)
    ax.set_ylabel("Frequency [%]")
    ax.set_yticks(range(0, 101, 10))
    ax.set_title(
        (
            "For Precipitating Events\n"
            "Frequency of Snow by Wet Bulb Temperature"
        )
    )
    fig.savefig("test.png")


def plot3():
    df = pd.read_csv("events.csv")
    df["wetbulb"] = calc(df["tmpf"].values, df["dwpf"].values)
    df["i_wetbulb"] = df["wetbulb"].astype("i")
    (fig, axes) = plt.subplots(3, 1, figsize=(6.4, 8))

    labels = {
        "i_wetbulb": "Wet Bulb",
        "dwpf": "Dew Point",
        "tmpf": "Air Temperature",
    }
    for i, label in enumerate(["i_wetbulb", "tmpf", "dwpf"]):
        gdf = df.groupby(label).sum()
        total = gdf["snow"] + gdf["zr"] + gdf["rain"]  # + gdf['pl']
        ax = axes[i]
        ax.plot(gdf.index.values, gdf["snow"] / total * 100.0, label="Snow")
        ax.plot(
            gdf.index.values, gdf["zr"] / total * 100.0, label="Freeze Rain"
        )
        ax.plot(gdf.index.values, gdf["rain"] / total * 100.0, label="Rain")
        # ax.plot(gdf.index.values,
        #        gdf['pl'] / total * 100., label='Sleet')
        ax.grid(True)
        ax.legend(loc=6)
        ax.set_xticks(range(20, 41, 2))
        ax.set_xlim(20, 40)
        ax.text(
            1.01,
            0.5,
            "%s" % (labels[label],),
            transform=ax.transAxes,
            rotation=-90,
            fontsize=15,
            va="center",
        )
        ax.set_ylabel("Frequency [%]")
        ax.set_yticks(range(0, 101, 10))
    axes[0].set_title(
        (
            "For Precipitating Events (1997-2017)\n"
            "Frequency of Precip Type by Temperature"
        )
    )
    fig.savefig("test.png")


def plot2():
    """Make a plot"""
    df = pd.read_csv("events_grouped.csv")
    df["wetbulb"] = calc(df["tmpf"].values, df["dwpf"].values)
    df["snowfreq"] = df["snowcount"] / (df["raincount"] + df["snowcount"])
    df["i_wetbulb"] = df["wetbulb"].astype("i")
    (fig, ax) = plt.subplots(1, 1)
    for varname in ["tmpf", "dwpf", "i_wetbulb"]:
        gdf = df.groupby(varname).sum()
        # gdf.to_csv('events_bywetbulb.csv')
        ax.plot(
            gdf.index.values,
            gdf["snowcount"] / (gdf["raincount"] + gdf["snowcount"]) * 100.0,
            label=varname,
        )
    ax.legend()
    ax.grid(True)
    ax.set_xlim(20, 40)
    ax.set_xticks(range(20, 41, 2))
    ax.set_yticks(range(0, 101, 10))
    ax.set_ylabel("Frequency of Event being Snow")
    ax.set_xlabel("Temperature F")
    ax.set_title("Frequency of Reported Snowfall vs Rain")
    fig.savefig("test.png")
    return
    res = ax.scatter(df["dwpf"], df["wetbulb"], c=df["snowfreq"].values)
    fig.colorbar(res, label="Frequency of Snow [1]")
    ax.set_title("Frequency of Having Snow Reported for given T/Wetbulb Combo")
    ax.set_xlim(-30, 50)
    ax.set_xlabel("Wet Bulb F")
    ax.set_ylabel("Air Temperature F")
    ax.grid(True)
    fig.savefig("test.png")


def delineate(val):
    """What type is this, please"""
    tokens = val.split(",")
    for test in ["+SN", "+RA", "SN", "RA", "-SN", "-RA"]:
        if test in tokens:
            return test
    return ""


def is_in(val, options):
    """Hacky, maybe"""
    for token in val.split(","):
        if token in options:
            return True
    return False


def workflow(pgconn, sid):
    """Get data please"""
    df = read_sql(
        """
    SELECT station, valid, tmpf::int as tmpf, dwpf::int as dwpf,
    presentwx, metar from alldata
    where station = %s and tmpf >= 20 and tmpf < 50 and tmpf >= dwpf
    and dwpf > -40 and presentwx is not null and
    (strpos(presentwx, 'SN') > 0 or strpos(presentwx, 'RA') > 0)
    and valid > '1997-01-01'
    """,
        pgconn,
        params=(sid,),
        index_col=None,
    )
    df["snow"] = df["presentwx"].apply(
        is_in, args=(["-SN", "SN", "+SN", "-RASN", "-TSSN", "TSSN", "+TSSN"],)
    )
    df["rain"] = df["presentwx"].apply(
        is_in, args=(["-RA", "RA", "+RA", "-RASN", "-TSRA", "TSRA", "+TSRA"],)
    )
    df["zr"] = df["presentwx"].apply(is_in, args=(["-FZRA", "FZRA", "+FZRA"],))
    df["pl"] = df["presentwx"].apply(
        is_in, args=(["-PLRA", "-PLSN", "-PL", "PL", "-RAPL"],)
    )
    return df


def main():
    """Go Main Go"""
    pgconn = get_dbconn("asos", user="nobody")
    nt = NetworkTable(
        (
            "IA_ASOS",
            "MN_ASOS",
            "WI_ASOS",
            "MI_ASOS",
            "OH_ASOS",
            "IN_ASOS",
            "KY_ASOS",
            "IL_ASOS",
            "MO_ASOS",
            "KS_ASOS",
            "NE_ASOS",
            "ND_ASOS",
            "SD_ASOS",
        )
    )
    dfs = []
    for sid in tqdm.tqdm(nt.sts):
        if (
            nt.sts[sid]["archive_begin"]
            and nt.sts[sid]["archive_begin"].year < 1980
        ):
            df = workflow(pgconn, sid)
            df["state"] = nt.sts[sid]["state"]
            if not df.empty:
                dfs.append(df)

    df = pd.concat(dfs)
    df.to_csv("events.csv", index=False)
    # grep -v 'False,False,False' events.csv > e2


if __name__ == "__main__":
    # main()
    # grouper()
    plot()
    # plot4()
