"""Search emails for a given subject for NCEI"""
from __future__ import print_function
import sys
import email
import getpass

import imaplib


def main(argv):
    """Do Something"""
    obj = imaplib.IMAP4_SSL('imap.gmail.com', 993)
    obj.login('akrherz@gmail.com', getpass.getpass())
    obj.select("[Gmail]/All Mail")
    date = argv[1]  # Format dd-Mon-YYYY
    _typ, data = obj.search(None,
                            '(SUBJECT "AIRS Order" since "%s")' % (date, ))
    for num in data[0].split():
        _typ, data = obj.fetch(num, '(RFC822)')
        msg = email.message_from_string(data[0][1])
        val = msg['Subject'].replace('AIRS Order', '').replace('Complete', '')
        print('mirror %s' % (val, ))


if __name__ == '__main__':
    main(sys.argv)
