import imaplib
import re
import email
import datetime
import getpass

obj = imaplib.IMAP4_SSL('imap.gmail.com', 993)
obj.login('akrherz@gmail.com', getpass.getpass())
obj.select("[Gmail]/All Mail")
typ, data = obj.search(None, '(SUBJECT "AIRS Order" since "21-May-2017")')
for num in data[0].split():
    found = False
    typ, data = obj.fetch(num, '(RFC822)')
    msg = email.message_from_string(data[0][1])
    val = msg['Subject'].replace('AIRS Order', '').replace('Complete', '')
    print 'mirror', val 
