import requests
import sys

RELEASE = sys.argv[1]

req = requests.get(("https://api.github.com/repos/igniterealtime/Openfire/"
                    "releases/tags/v" + RELEASE))
j = req.json()
total = 0
print("Openfire Download Stats for Release: %s" % (RELEASE,))
for a in j['assets']:
    print("%27s %6i" % (a['name'], a['download_count']))
    total += a['download_count']
print("%27s ======" % ("", ))
print("%27s %6i" % ("", total))
