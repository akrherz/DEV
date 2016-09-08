import os

for i in range(0,200):
  url = "http://localhost:9090/plugins/userService/userservice?type=add&secret=usethesource&username=user%s&password=%s&name=user%s&email=akrherz@localhost" % (i,i,i)
  os.system("wget -O /dev/null '%s'" % (url,))

  url = "http://localhost:9090/plugins/userService/userservice?type=update&secret=usethesource&username=user%s&groups=shared+group" % (i,)
  os.system("wget -O /dev/null '%s'" % (url,))
