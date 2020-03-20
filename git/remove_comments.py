import os

for root, dirs, files in os.walk("."):
    for fn in files:
        localfn = "%s/%s" % (root, fn)
        lastline = ""
        dofile = False
        for line in open(localfn):
            if line.strip() == "*" and lastline.strip() == "/**":
                # if line.strip() == '-->' and lastline.strip() == '<!--':
                # print localfn, line, lastline
                dofile = True
            lastline = line.strip()
        if not dofile:
            continue
        lines = open(localfn).readlines()
        o = open(localfn, "w")
        for line in lines:
            if line.strip() == "*" and lastline.strip() == "/**":
                pass
            else:
                o.write(line)
            lastline = line.strip()
        o.close()
