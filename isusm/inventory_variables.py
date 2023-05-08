"""Figure out how much of a variable name mess we have."""
import glob
import os
import sys


def runtype(name):
    """Run for a given filetime."""
    os.chdir("/mnt/home/loggernet")
    cols = {}
    for fn in glob.glob("*%s.dat" % (name,)):
        station = fn.split("_")[0]
        for linenum, line in enumerate(open(fn, "rb").readlines()):
            if linenum == 1:
                for token in (
                    line.decode("ascii", "ignore")
                    .strip()
                    .replace('"', "")
                    .split(",")
                ):
                    d = cols.setdefault(token, [])
                    d.append(station)
            if linenum > 1:
                break
            linenum += 1
    keys = list(cols.keys())
    keys.sort()
    for key in keys:
        print("%s\n  %s" % (key, " ".join(cols[key])))


def main(argv):
    """Go Main Go."""
    runtype(argv[1])


if __name__ == "__main__":
    main(sys.argv)
