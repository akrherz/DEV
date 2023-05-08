import email
import imaplib

obj = imaplib.IMAP4_SSL("imap.gmail.com", 993)
obj.login("akrherz", "")
obj.select("[Gmail]/All Mail")

users = {}

typ, data = obj.search(
    None,
    '(TO "akrherz@iastate.edu" FROM "@iastate.edu" since "01-Jan-2014" '
    'NOT FROM "agron.iastate.edu")',
)
for num in data[0].split():
    typ, data = obj.fetch(num, "(RFC822)")
    msg = email.message_from_string(data[0][1])
    users[msg["From"]] = 1

for key in users:
    print(key)
