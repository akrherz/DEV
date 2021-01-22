"""Count Words."""

# 3rd Party
from pyiem.util import get_dbconn, noaaport_text
import pandas as pd


def main():
    """Go Main Go."""
    pgconn = get_dbconn("afos")
    cursor = pgconn.cursor()
    cursor.execute(
        "SELECT data, source, entered, pil from products "
        "WHERE substr(pil, 1, 3) = 'WSW' and entered > '2016-01-01' "
    )
    res = []
    maxcount = 0
    for row in cursor:
        s = noaaport_text(row[0]).replace("\r", "")
        # Arb skip the first 9 lines, for better or worse
        s = "\n".join(s.split("\n")[9:])
        # Go find the UGC line
        segments = s.split("\n\n")
        hit = 0
        for i, segment in enumerate(segments):
            if segment.find("-\n") > -1:
                hit = i
                break
        wordcount = 0
        if hit > 0:
            words = (" ".join(segments[:hit])).split()
            wordcount = sum([i.isalpha() for i in words])
            if wordcount > maxcount:
                maxcount = wordcount
                print(maxcount)
                print(row[2])
                print(row[3])
                print(words)
        else:
            # CAN or EXP disqualifies this one.
            if (
                segments[0].find(".CAN.") > -1
                or segments[0].find(".EXP.") > -1
            ):
                continue

        res.append([row[1][1:], wordcount])
    df = pd.DataFrame(res, columns=["wfo", "count"])
    # df2 = df[df["count"] == 0].groupby("wfo").count() / df.groupby("wfo").count()
    # df2["count"] = df2["count"] * 100.
    df2 = df.groupby("wfo").mean().copy()
    df2.to_csv("wfo.csv")


if __name__ == "__main__":
    main()
