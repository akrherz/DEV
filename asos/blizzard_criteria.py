"""Lets run some diagnostics on blizzard criterion."""

import numpy as np
from tqdm import tqdm

from matplotlib.ticker import FuncFormatter
from pandas.io.sql import read_sql
from pyiem.database import get_sqlalchemy_conn
from pyiem.network import Table as NetworkTable
from pyiem.plot import figure


def main():
    """Go Main Go."""
    nt = NetworkTable(("IA_ASOS", "AWOS"))

    bestvsby = {}
    bestsknt = {}
    bs_vsby = []
    bs_sknt = []
    bv_vsby = []
    bv_sknt = []

    abestvsby = {}
    abestsknt = {}
    abs_vsby = []
    abs_sknt = []
    abv_vsby = []
    abv_sknt = []

    mbestvsby = {}
    mbestsknt = {}
    mbs_vsby = []
    mbs_sknt = []
    mbv_vsby = []
    mbv_sknt = []

    hits = {}
    ahits = {}
    mhits = {}
    for sid in tqdm(nt.sts):
        with get_sqlalchemy_conn("postgis") as conn:
            df = read_sql(
                """
            select w.ugc from warnings_2021 w JOIN ugcs u on (w.gid = u.gid)
            where substr(w.ugc, 1, 2) = 'IA' and phenomena = 'BZ' and
            significance = 'W' and issue > '2021-01-04' and
            st_contains(u.geom, ST_GeomFromEWKT('SRID=4326;POINT(%s %s)'))
            """,
                conn,
                params=(nt.sts[sid]["lon"], nt.sts[sid]["lat"]),
            )
        # if df.empty:
        #    continue
        bestvsby[sid] = {"sknt": 0, "vsby": 100}
        bestsknt[sid] = {"sknt": 0, "vsby": 100}
        abestvsby[sid] = {"sknt": 0, "vsby": 100}
        abestsknt[sid] = {"sknt": 0, "vsby": 100}
        mbestvsby[sid] = {"sknt": 0, "vsby": 100}
        mbestsknt[sid] = {"sknt": 0, "vsby": 100}

        with get_sqlalchemy_conn("iem") as conn:
            df = read_sql(
                """
            SELECT valid, vsby, greatest(sknt, gust) as wind
            from current_log c JOIN stations t
            ON (c.iemid = t.iemid) WHERE
            t.id = %s and valid > '2021-02-04 00:00' and
            sknt >= 0 and vsby >= 0 and raw !~* 'MADISHF' ORDER by valid ASC
            """,
                conn,
                params=(sid,),
                index_col=None,
            )
        obs = len(df.index)
        if obs < 10:
            print("failed to find enough obs for %s" % (sid,))
            continue
        for i, row in df.iterrows():
            j = i
            while j < obs and (df.valid[j] - row["valid"]).total_seconds() < (
                3 * 3600
            ):
                j += 1
            avg_sknt = np.average(df.wind.values[i:j])
            min_sknt = np.min(df.wind.values[i:j])
            med_sknt = np.median(df.wind.values[i:j])
            avg_vsby = np.average(df.vsby.values[i:j])
            max_vsby = np.max(df.vsby.values[i:j])
            med_vsby = np.median(df.vsby.values[i:j])
            if avg_sknt >= 30 and avg_vsby <= 0.25:
                ahits[sid] = True
            if min_sknt >= 30 and max_vsby <= 0.25:
                hits[sid] = True
            if med_sknt >= 30 and med_vsby <= 0.25:
                mhits[sid] = True

            if min_sknt > bestsknt[sid]["sknt"]:
                bestsknt[sid]["sknt"] = min_sknt
                bestsknt[sid]["vsby"] = max_vsby
            if max_vsby < bestvsby[sid]["vsby"]:
                bestvsby[sid]["sknt"] = min_sknt
                bestvsby[sid]["vsby"] = max_vsby

            if avg_sknt > abestsknt[sid]["sknt"]:
                abestsknt[sid]["sknt"] = avg_sknt
                abestsknt[sid]["vsby"] = avg_vsby
            if avg_vsby < abestvsby[sid]["vsby"]:
                abestvsby[sid]["sknt"] = avg_sknt
                abestvsby[sid]["vsby"] = avg_vsby

            if avg_sknt > mbestsknt[sid]["sknt"]:
                mbestsknt[sid]["sknt"] = med_sknt
                mbestsknt[sid]["vsby"] = med_vsby
            if avg_vsby < mbestvsby[sid]["vsby"]:
                mbestvsby[sid]["sknt"] = med_sknt
                mbestvsby[sid]["vsby"] = med_vsby

        bv_sknt.append(bestvsby[sid]["sknt"])
        bv_vsby.append(bestvsby[sid]["vsby"])
        bs_sknt.append(bestsknt[sid]["sknt"])
        bs_vsby.append(bestsknt[sid]["vsby"])
        abv_sknt.append(abestvsby[sid]["sknt"])
        abv_vsby.append(abestvsby[sid]["vsby"])
        abs_sknt.append(abestsknt[sid]["sknt"])
        abs_vsby.append(abestsknt[sid]["vsby"])

        mbv_sknt.append(mbestvsby[sid]["sknt"])
        mbv_vsby.append(mbestvsby[sid]["vsby"])
        mbs_sknt.append(mbestsknt[sid]["sknt"])
        mbs_vsby.append(mbestsknt[sid]["vsby"])

    def log_10_product(x, _pos):
        """The two args are the value and tick position.
        Label ticks with the product of the exponentiation"""
        return "%1i" % (x)

    fig = figure(title="Iowa ASOS/AWOS 4 February 2021 Blizzard Criteria")
    ax1 = fig.add_axes([0.075, 0.1, 0.25, 0.7])
    ax2 = fig.add_axes([0.4, 0.1, 0.25, 0.7])
    ax3 = fig.add_axes([0.725, 0.1, 0.25, 0.7])

    ax1.set_ylim(0, 45)
    ax1.set_ylabel("Minimum 3HR Wind Speed/Gust [mph]")
    ax1.set_xlim(1e-1, 1.2e1)
    ax1.set_xlabel("Maximum 3HR Visibility [miles]")

    ax2.set_ylabel("Average 3HR Wind Speed/Gust [mph]")
    ax2.set_ylim(0, 45)
    ax2.set_xlim(1e-1, 1.2e1)
    ax2.set_xlabel("Average 3HR Visibility [miles]")

    ax3.set_ylabel("Median 3HR Wind Speed/Gust [mph]")
    ax3.set_ylim(0, 45)
    ax3.set_xlim(1e-1, 1.2e1)
    ax3.set_xlabel("Median 3HR Visibility [miles]")

    ax1.plot([1e-1, 1.2e1], [30 * 1.15, 30 * 1.15], "g--")
    ax1.plot([0.25, 0.25], [0, 45], "g--")
    ax2.plot([1e-1, 1.2e1], [30 * 1.15, 30 * 1.15], "g--")
    ax2.plot([0.25, 0.25], [0, 45], "g--")
    ax3.plot([1e-1, 1.2e1], [30 * 1.15, 30 * 1.15], "g--")
    ax3.plot([0.25, 0.25], [0, 45], "g--")

    ax1.scatter(
        bs_vsby,
        np.array(bs_sknt) * 1.15,
        marker="+",
        color="r",
        label="Best Wind",
    )
    ax1.scatter(
        bv_vsby,
        np.array(bv_sknt) * 1.15,
        marker="o",
        facecolor="w",
        edgecolor="b",
        label="Best Vis",
    )
    ax1.set_xscale("log")
    ax1.legend()

    ax2.scatter(
        abs_vsby,
        np.array(abs_sknt) * 1.15,
        marker="+",
        color="r",
        label="Best Wind",
    )
    ax2.scatter(
        abv_vsby,
        np.array(abv_sknt) * 1.15,
        marker="o",
        facecolor="w",
        edgecolor="b",
        label="Best Vis",
    )
    ax2.set_xscale("log")
    ax2.legend()

    ax3.scatter(
        mbs_vsby,
        np.array(mbs_sknt) * 1.15,
        marker="+",
        color="r",
        label="Best Wind",
    )
    ax3.scatter(
        mbv_vsby,
        np.array(mbv_sknt) * 1.15,
        marker="o",
        facecolor="w",
        edgecolor="b",
        label="Best Vis",
    )
    ax3.set_xscale("log")
    ax3.legend()

    formatter = FuncFormatter(log_10_product)
    ax1.xaxis.set_major_formatter(formatter)
    ax2.xaxis.set_major_formatter(formatter)
    ax3.xaxis.set_major_formatter(formatter)

    ax1.set_title(
        "Max/Min Method: %s/%s Sites Hit\nSites: %s"
        % (len(hits), len(bs_vsby), ",".join(hits.keys()))
    )
    ax2.set_title(
        "Average Method: %s/%s Sites Hit\nSites: %s"
        % (len(ahits), len(abs_vsby), ",".join(ahits.keys()))
    )
    sites = list(mhits.keys())
    ax3.set_title(
        "Median Method: %s/%s Sites Hit\nSites: %s\n%s"
        % (len(mhits), len(mbs_vsby), ",".join(sites[:6]), ",".join(sites[6:]))
    )

    fig.savefig("210204.png")


if __name__ == "__main__":
    main()
