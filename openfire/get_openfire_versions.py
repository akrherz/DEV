import requests
import time

payload = ("<available>"
           "</available>")
# base = "http://openfire:8080/ignite/"
base = "http://www.igniterealtime.org/"
for i in range(1800):
    req = requests.post(base + "projects/openfire/versions.jsp",
                        dict(type='available', query=payload))
    if len(req.content) < 1800:
        print req.content
    time.sleep(0.1)
