"""Verify MCD watch confidence."""

from datetime import timedelta, timezone

import geopandas as gpd
import pandas as pd
from pyiem.database import get_dbconn, get_sqlalchemy_conn, sql_helper
from pyiem.plot import figure_axes
from pyiem.util import logger
from tqdm import tqdm

LOG = logger()


def get_mcds():
    """Fetch."""
    with get_sqlalchemy_conn("postgis") as conn:
        df = gpd.read_postgis(
            sql_helper("""
            SELECT issue as mcdtime, watch_confidence, num, year, geom
            from mcd where
            watch_confidence is not null and st_isvalid(geom)
            ORDER by mcdtime ASC
        """),
            conn,
            index_col=None,
            geom_col="geom",
        )  # type: ignore
    df["wfos"] = ""
    return df


def overlap(cursor, row, threshold):
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
            row["geom"].wkt,
            row["mcdtime"],
            row["mcdtime"] + timedelta(minutes=150),
            threshold / 100.0,
        ),
    )
    if cursor.rowcount == 0:
        return None, None
    row2 = cursor.fetchone()
    issued = row2[1].replace(tzinfo=timezone.utc)
    return row2[0], (issued - row["mcdtime"]).total_seconds() / 60.0


def do_verification(df: pd.DataFrame):
    """Do Verification"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    for idx, row in tqdm(df.iterrows(), total=len(df.index)):
        for threshold in range(10, 101, 10):
            verif, timeoffset = overlap(cursor, row, threshold)
            df.at[idx, f"verif{threshold}"] = verif
            df.at[idx, f"timeoffset{threshold}"] = timeoffset


def do_plotting(threshold):
    """Plotting."""
    df = pd.read_excel("mcd_verif.xlsx")
    (fig, ax) = figure_axes(
        title=(
            "SPC MCD Watch Probability Verification (1 May 2012 - 16 Apr 2025)"
        ),
        subtitle=(
            "Subsequent Watch (within 2.5 hours of MCD, "
            f"Polygon Spatial Overlap: >= {threshold:.0f}%)"
        ),
        figsize=(8, 6),
    )
    probs = [5, 20, 40, 60, 80, 95]
    verif = []
    hits = []
    events = []
    for prob in probs:
        df2 = df[df["watch_confidence"] == prob]
        event = len(df2.index)
        hit = len(df2[df2[f"verif{threshold}"] > 0].index)
        hits.append(hit)
        events.append(event)
        verif.append(float(hit) / float(event) * 100.0)

    ax.bar(range(len(probs)), verif)
    for i, v in enumerate(verif):
        ax.text(
            i,
            v + 3,
            f"({hits[i]}/{events[i]})\n{v:.1f}%",
            ha="center",
            bbox=dict(color="white"),
        )
    ax.set_xticks(range(len(probs)))
    ax.set_xticklabels(probs)
    ax.set_ylim(0, 110)
    ax.grid(True)
    ax.set_yticks(probs)
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
    fig.text(0.01, 0.01, "@akrherz, 16 Apr 2025")
    fig.savefig(f"mcd_verify_{threshold}.png")


def do_plotting2():
    """Another plotting option."""
    df = pd.read_excel("mcd_verif.xlsx")
    (fig, ax) = figure_axes()
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
    df["mcdtime"] = df["mcdtime"].apply(lambda x: x.strftime("%Y-%m-%d %H:%M"))
    with pd.ExcelWriter("mcd_verif.xlsx") as writer:
        df.drop(columns="geom").to_excel(
            writer, sheet_name="Verification", index=False
        )


if __name__ == "__main__":
    # do_work()
    do_plotting(50)
    # do_plotting2()
