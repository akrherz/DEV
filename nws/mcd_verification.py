"""Verify MCD watch confidence."""
import datetime

from tqdm import tqdm
import pytz
from pyiem.plot.use_agg import plt
from pyiem.nws.products.mcd import parser
from pyiem.util import get_dbconn
import pandas as pd
from pandas.io.sql import read_sql


def get_mcds():
    """Fetch."""
    pgconn = get_dbconn("afos")
    df = read_sql(
        """
        SELECT entered as mcdtime, data from products where pil = 'SWOMCD' and
        entered > '2012-05-01' ORDER by mcdtime ASC
    """,
        pgconn,
        index_col=None,
    )
    df["algofail"] = True
    df["probability"] = None
    df["wfos"] = ""
    df["num"] = None
    df["year"] = None
    return df


def overlap(cursor, prod, threshold):
    """Do Overlap"""
    cursor.execute(
        """
        WITH mcd as (
            SELECT ST_SetSrid(ST_GeomFromEWKT(%s), 4326) as geom
        )
        SELECT num, issued at time zone 'UTC'
        from watches w, mcd m WHERE issued > %s and issued < %s
        and st_intersects(w.geom, m.geom)
        and (st_area(st_intersection(w.geom, m.geom))/st_area(w.geom)) >= %s
        ORDER by issued ASC
    """,
        (
            str(prod.geometry),
            prod.valid,
            prod.valid + datetime.timedelta(minutes=150),
            threshold / 100.0,
        ),
    )
    if cursor.rowcount == 0:
        return None, None
    row = cursor.fetchone()
    issued = row[1].replace(tzinfo=pytz.utc)
    return row[0], (issued - prod.valid).total_seconds() / 60.0


def do_verification(df):
    """Do Verification"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    for idx, row in tqdm(df.iterrows(), total=len(df.index)):
        try:
            prod = parser(row["data"])
        except Exception as _:
            print(_)
            print(row["data"])
            continue
        if not prod.geometry.is_valid:
            print(
                "MCD: %s is invalid: %s" % (prod.discussion_num, prod.geometry)
            )
            continue
        prob = prod.watch_prob
        if prob is None:
            continue
        df.at[idx, "algofail"] = False
        df.at[idx, "probability"] = prob
        df.at[idx, "wfos"] = ",".join(prod.attn_wfo)
        df.at[idx, "num"] = prod.discussion_num
        df.at[idx, "year"] = prod.valid.year
        for threshold in range(10, 101, 10):
            try:
                verif, timeoffset = overlap(cursor, prod, threshold)
            except Exception:
                cursor = pgconn.cursor()
                print("FATAL")
                continue
            df.at[idx, "verif%s" % (threshold,)] = verif
            df.at[idx, "timeoffset%s" % (threshold,)] = timeoffset


def do_plotting(threshold):
    """Plotting."""
    df = pd.read_excel("mcd_verif.xlsx")
    (fig, ax) = plt.subplots(1, 1)
    probs = [5, 20, 40, 60, 80, 95]
    verif = []
    hits = []
    events = []
    for prob in probs:
        df2 = df[df["probability"] == prob]
        event = len(df2.index)
        hit = len(df2[df2["verif%s" % (threshold,)] > 0].index)
        hits.append(hit)
        events.append(event)
        verif.append(float(hit) / float(event) * 100.0)

    ax.bar(range(len(probs)), verif)
    for i, v in enumerate(verif):
        ax.text(
            i,
            v + 3,
            "(%s/%s)\n%.1f%%" % (hits[i], events[i], v),
            ha="center",
            bbox=dict(color="white"),
        )
    ax.set_xticks(range(len(probs)))
    ax.set_xticklabels(probs)
    ax.set_ylim(0, 110)
    ax.grid(True)
    ax.set_yticks(probs)
    ax.set_title(
        (
            "SPC MCD Watch Probability Verification "
            "(1 May 2012 - 12 Aug 2019)\n"
            "Subsequent Watch (within 2.5 hours of MCD, "
            "Spatial Overlap: >= %.0f%%)" % (threshold,)
        )
    )
    ax.set_ylabel("Watch Issuance Frequency [%]")
    ax.set_xlabel("MCD Watch Issuance Confidence [%]")
    ax.text(
        0,
        95,
        "(hits/events)\npercent",
        ha="center",
        va="center",
        bbox=dict(color="white"),
    )
    fig.text(0.01, 0.01, "@akrherz, 12 Aug 2019")
    fig.savefig("test%s.png" % (threshold,))


def do_plotting2():
    """Another plotting option."""
    df = pd.read_excel("mcd_verif.xlsx")
    (fig, ax) = plt.subplots(1, 1)
    for threshold in range(10, 101, 10):
        probs = [5, 20, 40, 60, 80, 95]
        verif = []
        for prob in probs:
            df2 = df[df["probability"] == prob]
            events = len(df2.index)
            hits = len(df2[df2["verif%s" % (threshold,)] > 0].index)
            verif.append(float(hits) / float(events) * 100.0)

        ax.plot(probs, verif, label="%.0f%%" % (threshold,))

    ax.set_title(
        (
            "SPC MCD Watch Probability Verification "
            "(1 May 2012 - 12 Aug 2019)\n"
            "Subsequent Watch (within 2.5 hours of MCD, "
            "Given Spatial Overlap)"
        )
    )
    ax.set_ylabel("Watch Issuance Frequency [%]")
    ax.set_xlabel("MCD Watch Confidence [%]")
    ax.plot([0, 100], [0, 100], linestyle="-.", lw=2)
    ax.legend(loc=2, title="Spatial\nOverlap %")
    ax.grid(True)
    ax.set_xticks(probs)
    ax.set_yticks(probs)
    ax.set_xlim(-0.5, 101)
    ax.set_ylim(-0.5, 101)
    fig.text(0.01, 0.01, "@akrherz, 12 Aug 2019")
    fig.savefig("line.png")


def do_work():
    """Do Something Fun"""
    df = get_mcds()
    do_verification(df)
    del df["data"]
    df = df[df["probability"] > 0]
    df["mcdtime"] = df["mcdtime"].apply(lambda x: x.strftime("%Y-%m-%d %H:%M"))
    with pd.ExcelWriter("mcd_verif.xlsx") as writer:
        df.to_excel(writer, "Verification", index=False)
        writer.save()


if __name__ == "__main__":
    # do_work()
    do_plotting(10)
    # do_plotting2()
