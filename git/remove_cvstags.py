# git grep '$RCSfile' > todo
import re

TAGS = re.compile("\$(RCSfile|Date|Revision|Id)")

for line in open("todo"):
    if line.startswith("Binary"):
        continue
    fn = line.split(":")[0]
    lines = open(fn).readlines()
    o = open(fn, "w")
    for line in lines:
        if not TAGS.search(line):
            o.write(line)
    o.close()
