"""
Loop over sites that we think are solely COOP, but report many times per day
and so are likely DCP
"""

from pyiem.database import get_dbconn


def main():
    """GO!"""
    ipgconn = get_dbconn("iem")
    icursor = ipgconn.cursor()
    icursor2 = ipgconn.cursor()
    mpgconn = get_dbconn("mesosite")
    mcursor = mpgconn.cursor()
    mcursor2 = mpgconn.cursor()

    # Look for over-reporting COOPs
    icursor.execute(
        """
     select id, network, count(*), max(raw) from current_log c JOIN stations s
     ON (s.iemid = c.iemid)
     where network ~* 'COOP' and valid > 'TODAY'::date
     GROUP by id, network ORDER by count DESC
    """
    )
    for row in icursor:
        sid = row[0]
        network = row[1]
        if row[2] < 5:
            continue
        # Is there a DCP variant?
        mcursor.execute(
            "SELECT network from stations where id = %s and network = %s",
            (sid, network.replace("_COOP", "_DCP")),
        )
        if mcursor.rowcount == 0:
            newnetwork = network.replace("_COOP", "_DCP")
            print(
                "We shall switch %s from %s to %s" % (sid, network, newnetwork)
            )
            mcursor2.execute(
                "UPDATE stations SET network = %s "
                "WHERE id = %s and network = %s",
                (newnetwork, sid, network),
            )

    ipgconn.commit()
    icursor2.close()
    mpgconn.commit()
    mcursor.close()


if __name__ == "__main__":
    main()
