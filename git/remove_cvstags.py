"""git grep '$RCSfile' > todo"""

import re


def main():
    """GO Main Go."""
    TAGS = re.compile("\$(RCSfile|Date|Revision|Id)")

    for line in open("todo", encoding="utf8"):
        if line.startswith("Binary"):
            continue
        fn = line.split(":")[0]
        lines = open(fn, encoding="utf8").readlines()
        o = open(fn, "w", encoding="utf8")
        for line in lines:
            if not TAGS.search(line):
                o.write(line)
        o.close()


if __name__ == "__main__":
    main()
