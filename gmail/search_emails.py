"""Search emails for a given subject for NCEI"""
import sys
import email
import getpass

import imaplib


def main(argv):
    """Do Something"""
    obj = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    obj.login("akrherz@gmail.com", getpass.getpass())
    obj.select("[Gmail]/All Mail")
    date = argv[1]  # Format dd-Mon-YYYY
    _typ, data = obj.search(None, f'(SUBJECT "AIRS Order" since "{date}")')
    for num in data[0].split():
        _typ, data = obj.fetch(num, "(RFC822)")
        msg = email.message_from_string(data[0][1])
        val = msg["Subject"].replace("AIRS Order", "").replace("Complete", "")
        print(f"mirror {val}")


if __name__ == "__main__":
    main(sys.argv)
