"""Reprocess junky data"""
import sys
import datetime

import pytz
from pyiem.util import noaaport_text, get_dbconn
from pyiem.nws.products.vtec import parser


def p(ts):
    """Helper."""
    if ts is None:
        return "(NONE)"
    return ts.strftime("%Y-%m-%d %H:%M")


def main(argv):
    """go"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()

    table = "warnings_%s" % (argv[1],)

    cursor.execute(
        "SELECT ctid, ugc, issue at time zone 'UTC', "
        "expire at time zone 'UTC', init_expire at time zone 'UTC', "
        f"report, svs, phenomena, eventid, significance from {table} where "
        "(issue - expire) > '1 month'::interval"
    )

    print("Found %s entries to process..." % (cursor.rowcount,))
    for row in cursor:
        ctid = row[0]
        ugc = row[1]
        report = row[5]
        if row[6] is None:
            svss = []
        else:
            svss = row[6].split("__")
        phenomena = row[7]
        eventid = row[8]
        significance = row[9]
        issue0 = (
            row[2].replace(tzinfo=pytz.UTC) if row[2] is not None else None
        )
        expire0 = (
            row[3].replace(tzinfo=pytz.UTC) if row[3] is not None else None
        )
        init_expire0 = (
            row[4].replace(tzinfo=pytz.UTC) if row[4] is not None else None
        )
        svss.insert(0, report)

        expire1 = None
        issue1 = None
        init_expire1 = None
        msg = []
        print("  Found %s svss to process through" % (len(svss),))
        for i, svs in enumerate(svss):
            if svs.strip() == "":
                continue
            try:
                prod = parser(noaaport_text(svs))
            except Exception as exp:
                print("%s %s" % (ctid, exp))
                if i == 0:
                    print("FATAL ABORT as first product failed")
                    break
                continue
            for segment in prod.segments:
                found = False
                print(segment.ugcs)
                for this_ugc in segment.ugcs:
                    if str(this_ugc) == ugc:
                        found = True
                if not found:
                    print("Did not find %s in segment" % (ugc,))
                    continue
                for vtec in segment.vtec:
                    if (
                        vtec.phenomena != phenomena
                        or vtec.etn != eventid
                        or vtec.significance != significance
                    ):
                        print("skipping segment as it does not match")
                        continue
                    # if (vtec.etn != eventid and
                    #        vtec.significance == 'W' and
                    #        vtec.phenomena in ('SV', 'TO')):
                    #    print(("Updating eventid! old: %s new: %s"
                    #           ) % (eventid, vtec.etn))
                    #    cursor2.execute("""
                    # UPDATE """+table+""" SET eventid = %s WHERE oid = %s
                    #    """, (vtec.etn, oid))
                    if i == 0:
                        init_expire1 = (
                            vtec.endts
                            if vtec.endts is not None
                            else prod.valid + datetime.timedelta(hours=144)
                        )
                        expire1 = init_expire1
                        issue1 = (
                            vtec.begints
                            if vtec.begints is not None
                            else prod.valid
                        )
                    if vtec.begints is not None:
                        if vtec.begints != issue1:
                            msg.append(
                                ("%s %s %s %s %s")
                                % ("I", i, ugc, vtec.action, p(vtec.begints))
                            )
                        issue1 = vtec.begints
                    if vtec.endts is not None:
                        if vtec.endts != expire1:
                            msg.append(
                                ("%s %s %s %s %s")
                                % ("E", i, ugc, vtec.action, p(vtec.endts))
                            )
                        expire1 = vtec.endts
                    if vtec.action in ["EXA", "EXB"]:
                        issue1 = (
                            prod.valid
                            if vtec.begints is None
                            else vtec.begints
                        )
                    if vtec.action in ["UPG", "CAN"]:
                        expire1 = prod.valid

        if issue0 != issue1 or expire0 != expire1:
            print("\n".join(msg))
        if issue0 != issue1:
            print(
                ("%s %s.%s.%s Issue0: %s Issue1: %s")
                % (ugc, phenomena, significance, eventid, p(issue0), p(issue1))
            )
            cursor2.execute(
                f"UPDATE {table} SET issue = %s WHERE ctid = %s",
                (issue1, ctid),
            )
        if expire0 != expire1:
            print(
                ("%s %s.%s.%s Expire0: %s Expire1: %s")
                % (
                    ugc,
                    phenomena,
                    significance,
                    eventid,
                    p(expire0),
                    p(expire1),
                )
            )
            cursor2.execute(
                f"UPDATE {table} SET expire = %s WHERE ctid = %s",
                (expire1, ctid),
            )
        if init_expire0 != init_expire1:
            print(
                ("%s %s.%s.%s Init_Expire0: %s Init_Expire1: %s")
                % (
                    ugc,
                    phenomena,
                    significance,
                    eventid,
                    p(init_expire0),
                    p(init_expire1),
                )
            )
            cursor2.execute(
                f"UPDATE {table} SET init_expire = %s WHERE ctid = %s",
                (init_expire1, ctid),
            )

    cursor2.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main(sys.argv)
