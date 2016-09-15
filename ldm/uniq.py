import re

labels = {}

for line in open('sep1412z.log'):
    if line.find("NGRID") == -1:
        continue
    tokens = line.split("!")
    meat = tokens[1]
    pos = meat.find("/2016")
    label = meat[:pos]
    labels[label] = True

for key, _ in labels.iteritems():
    print key
