"""Reintroduce a bug with the soils file."""
import glob
import os


def main():
    """Go Main Go."""
    os.chdir("/i/1001/sol")
    for huc8 in glob.glob("*"):
        os.chdir(huc8)
        for huc812 in glob.glob("*"):
            os.chdir(huc812)
            for fn in glob.glob("*.sol"):
                with open(fn + ".tmp", "w") as fh:
                    for linenum, line in enumerate(open(fn)):
                        tokens = line.strip().split()
                        if len(tokens) != 9:
                            fh.write(line)
                            continue
                        # newval = "%.2f" % (float(tokens[6]), )
                        newval = "0.006"
                        print("%s %s->%s" % (linenum, tokens[6], newval))
                        tokens[6] = newval
                        fh.write(" ".join(tokens) + "\n")
                os.rename(fn + ".tmp", fn)
            os.chdir("..")
        os.chdir("..")


if __name__ == "__main__":
    main()
