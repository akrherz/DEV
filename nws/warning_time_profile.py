"""How quickly are warnings killed off"""

from pyiem.util import get_dbconn
from pyiem.nws.vtec import VTEC_PHENOMENA
import numpy as np
import matplotlib.pyplot as plt


def get_counts(phenomena, significance):
    """Get counts"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    cursor.execute(
        """
     SELECT issue, expire, init_expire from warnings where phenomena = %s
     and significance = %s and issue > '2005-10-01'
     and init_expire is not null
    """,
        (phenomena, significance),
    )

    counts = np.zeros(300)

    for row in cursor:
        origdur = (row[2] - row[0]).days * 86400.0 + (row[2] - row[0]).seconds

        finaldur = (row[1] - row[0]).days * 86400.0 + (row[1] - row[0]).seconds
        if origdur > 0:
            ratio = int((finaldur / origdur) * 100.0)
            counts[:ratio] += 1
    return counts


def main():
    """Go Main Go"""

    (fig, ax) = plt.subplots(1, 1)

    styles = [":", "--", "-"]
    for i, phenomena in enumerate(["TO", "SV", "BZ", "WS", "FF", "MA"]):
        print("Processing %s" % (phenomena,))
        counts = get_counts(phenomena, "W")
        ax.plot(
            np.linspace(0, 3, 300),
            counts / counts[0] * 100.0,
            lw=3,
            label=VTEC_PHENOMENA[phenomena],
            linestyle=styles[i % 3],
        )
    ax.grid(True)
    ax.legend()
    ax.set_yticks([0, 5, 10, 25, 40, 50, 60, 75, 90, 95, 100])
    ax.set_xlim(0, 3.1)
    ax.set_title(
        (
            "Time Duration of NWS Warnings Relative to Issuance\n"
            "1 Oct 2005 - 20 Feb 2020"
        )
    )
    ax.set_xlabel("Relative to Issuance Duration")
    ax.set_ylabel("Percent by Issuance Counties/Zones Still Valid [%]")

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
