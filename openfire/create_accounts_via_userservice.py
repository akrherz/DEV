"""Create some test accounts."""
import os
SERVICE = "http://localhost:9090/plugins/userService/userservice"

for i in range(0, 200):
    url = (
        "%s?type=add&secret=usethesource&username=user%s&password=%s"
        "&name=user%s&email=akrherz@localhost"
     ) % (SERVICE, i, i, i)
    os.system("wget -O /dev/null '%s'" % (url,))

    url = (
        "%s?type=update&secret=usethesource&username=user%s"
        "&groups=shared+group"
     ) % (SERVICE, i)
    os.system("wget -O /dev/null '%s'" % (url,))
