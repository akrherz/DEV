"""Count Words."""

# stdlib
import string

# 3rd Party
from pyiem.util import get_dbconn, noaaport_text


def main():
    """Go Main Go."""
    pgconn = get_dbconn("afos")
    cursor = pgconn.cursor()
    while True:
        cursor.execute(
            "SELECT ctid, data from afd WHERE wordcount is null LIMIT 10000"
        )
        if cursor.rowcount == 0:
            break
        cursor2 = pgconn.cursor()
        for row in cursor:
            s = noaaport_text(row[1])
            # Arb skip the first 9 lines, for better or worse
            s = "\n".join(s.split("\r\r\n")[9:])
            s = s.replace("\n", " ")
            words = [i.strip(string.punctuation) for i in s.split()]
            wordcount = sum([i.isalpha() for i in words])
            charcount = sum([len(i) for i in words if i.isalpha()])
            wordcount_full = len(row[1].split())
            cursor2.execute(
                "UPDATE afd SET wordcount = %s, "
                "wordcount_full = %s, charcount = %s where ctid = %s",
                (wordcount, wordcount_full, charcount, row[0]),
            )
        cursor2.close()
        pgconn.commit()


if __name__ == "__main__":
    main()
