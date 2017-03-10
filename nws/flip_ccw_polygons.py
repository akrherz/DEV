from pyiem.nws.product import str2polygon

for line in open('/tmp/DMX-reach-latlon.txt'):
    tokens = line.replace("||", "").replace('"', "").split(";")
    if len(tokens) != 2:
        continue
    (nwsli, pairs) = tokens
    pairs = " ".join(pairs.split())
    poly = str2polygon(pairs)
    if poly is None:
        continue
    if poly.exterior.is_ccw:
        tokens = pairs.strip().split()
        grouped = []
        for i in range(0, len(tokens), 2):
            grouped.append("%s %s" % (tokens[i], tokens[i+1]))
        print(("\nNWSLI: %s should be flipped!\nOLD: %s\nNEW: %s\n"
               ) % (nwsli, pairs, " ".join(grouped[::-1])))
