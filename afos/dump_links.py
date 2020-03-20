"""Dump links to products."""
import re

import pytz
from pyiem.nws.products import parser
from pyiem.util import get_dbconn, noaaport_text

PATTERN = re.compile(r"AT\s+THE\s+REQUEST\s+OF\s+(.*?)\.", re.M | re.S)


def main():
    """Go Main Go."""
    AFOS = get_dbconn("afos")
    acursor = AFOS.cursor("streamer")

    output = open("listing.txt", "w")
    acursor.execute(
        """
        select source, wmo, entered at time zone 'UTC', data, pil from cem
        where substr(pil, 1, 3) = 'CEM'
        ORDER by entered ASC
    """
    )
    for row in acursor:
        text = noaaport_text(row[3])
        try:
            prod = parser(text)
        except Exception as exp:
            print(exp)
            continue
        entered = row[2].replace(tzinfo=pytz.UTC)
        # if entered != prod.valid:
        #    sql = (
        #        "UPDATE products_%s_%s SET entered = %s WHERE "
        #        "source = %s and wmo = %s and entered = %s and pil = %s;"
        #    ) % (entered.year, "0712" if entered.month > 6 else "0106",
        #         prod.valid, row[0], row[1], entered, row[4])
        #    print(sql)
        tokens = PATTERN.findall(prod.unixtext)
        if not tokens:
            if prod.unixtext.find(" FIRE") < 0:
                continue
            res = ""
        else:
            res = tokens[0].replace("\n", " ")
        # print(res)
        prod.valid = entered
        output.write(
            ("%s,%s,%s,%s,https://mesonet.agron.iastate.edu/p.php?pid=%s\n")
            % (
                prod.source,
                res,
                entered.strftime("%Y-%m-%dT%H:%MZ"),
                " ".join([str(s) for s in prod.segments[0].ugcs]),
                prod.get_product_id(),
            )
        )
    output.close()


if __name__ == "__main__":
    main()
