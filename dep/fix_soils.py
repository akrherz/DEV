"""Fix mismatch between levels count and actual levels found."""
import os
import glob


def main():
    """Go Main Go."""
    os.chdir("/i/0/sol_input")
    for fn in glob.glob("*.SOL"):
        lines = open(fn).readlines()
        tokens = lines[7].split()
        if int(tokens[-7]) < 10:
            continue
        print("%s %s" % (fn, tokens[-7]))
        with open(fn, "w") as fh:
            for linenum, line in enumerate(lines):
                if linenum == 7:
                    fh.write(line.replace(" %s " % (tokens[-7],), " 9 "))
                else:
                    fh.write(line)


if __name__ == "__main__":
    main()
