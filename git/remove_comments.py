"""Useful."""
import os


def main():
    """Go Main Go."""
    for root, _dirs, files in os.walk("."):
        for fn in files:
            localfn = "%s/%s" % (root, fn)
            lastline = ""
            dofile = False
            for line in open(localfn, encoding="utf8"):
                if line.strip() == "*" and lastline.strip() == "/**":
                    # if line.strip() == '-->' and lastline.strip() == '<!--':
                    # print localfn, line, lastline
                    dofile = True
                lastline = line.strip()
            if not dofile:
                continue
            lines = open(localfn, encoding="utf8").readlines()
            o = open(localfn, "w", encoding="utf8")
            for line in lines:
                if line.strip() == "*" and lastline.strip() == "/**":
                    pass
                else:
                    o.write(line)
                lastline = line.strip()
            o.close()


if __name__ == "__main__":
    main()
