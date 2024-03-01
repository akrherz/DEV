"""Do some fun email stuff."""

import datetime
import email
import imaplib


def monthly_emails():
    """sent-mail totals."""
    obj = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    obj.login("akrherz", input("Password is:"))

    now = datetime.datetime(2016, 9, 1)
    ets = datetime.datetime(2018, 9, 1)

    while now < ets:
        fname = now.strftime("sent-mail-%b-%Y").lower()
        _res, num = obj.select(fname)
        if num[0].find(b"NON") > 0:
            fname = "oldsent/%s" % (fname,)
            _res, num = obj.select(fname)
        print("%s,%s,%s" % (now.year, now.month, float(num[0])))
        now = now + datetime.timedelta(days=32)
        now = now.replace(day=1)


def compute(to, cc):
    """Go."""
    if to is None:
        return []
    base = to.split("<")[-1].replace(">", "")
    res = []
    if base.find("unidata.ucar.edu") > -1:
        res.append(base)
    if cc is not None:
        for token in cc.split(","):
            base = token.split(">")[-1].replace(">", "")
            if base.find("unidata.ucar.edu") > -1:
                res.append(base.strip())
    return res


def blah(obj):
    """Go."""
    obj.select("[Gmail]/All Mail")
    typ, data = obj.search(
        None, '(to "ucar.edu") (from "akrherz@iastate.edu")'
    )
    counts = dict()
    for num in data[0].split():
        typ, data = obj.fetch(num, "(RFC822)")
        msg = email.message_from_string(data[0][1])
        if msg["From"].find("akrherz@iastate.edu") == -1:
            continue
        for myto in compute(msg["To"], msg["Cc"]):
            if myto not in counts:
                counts[myto] = 0
            counts[myto] += 1
            print(num, myto, counts[myto], msg["Cc"])

    print(counts)


if __name__ == "__main__":
    monthly_emails()
