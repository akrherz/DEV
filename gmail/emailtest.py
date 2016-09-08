import imaplib
import re
import email
import datetime

obj = imaplib.IMAP4_SSL('imap.gmail.com', 993)
obj.login('akrherz', raw_input("Password is:"))

now = datetime.datetime(2014, 6, 1)
ets = datetime.datetime(2016, 9, 1)

while now < ets:
    fname = now.strftime('sent-mail-%b-%Y').lower()
    res, num = obj.select(fname)
    if num[0].find("NON") > 0:
        fname = "oldsent/%s" % (fname,)
        res, num = obj.select(fname)
    print "%s,%s,%s" % (now.year, now.month, float(num[0]))
    now = now + datetime.timedelta(days=32)
    now = now.replace(day=1)

"""
typ, data = obj.search(None, 'SUBJECT', 'Twitter Support')
for num in data[0].split():
  typ, data = obj.fetch(num, '(RFC822)')
  msg = email.message_from_string(data[0][1])
  tokens = re.findall("#([0-9]+) Twitter Support", msg['Subject'])
  if len(tokens) == 1:
      print tokens[0]
"""
