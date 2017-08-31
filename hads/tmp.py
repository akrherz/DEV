data = """  CUPT2   |   85.97 |    2.38 |     83.59
 PKST2   |  103.08 |    21.6 |     81.48
 DULT2   |  108.52 |   36.68 |     71.84
 CDFT2   |  102.24 |   35.52 |     66.72
 BSRT2   |  907.02 |  844.15 |     62.87
 SGRT2   |  103.04 |   42.84 |      60.2
 ADLT2   |      98 |   38.88 |     59.12
 LMAT2   |   80.64 |   26.34 |      54.3
 CFMT2   |    91.2 |   39.44 |     51.76
 MCFT2   |   91.72 |   41.68 |     50.04
 LGCT2   |   79.48 |   31.36 |     48.12"""

from pyiem.network import Table as NetworkTable

nt = NetworkTable("TX_DCP")

for line in data.split("\n"):
    tokens = line.split("|")
    print(("%s %-33s %6.2f %6.2f %6.2f"
           ) % (tokens[0].strip(), nt.sts[tokens[0].strip()]['name'],
                float(tokens[2]), float(tokens[1]), float(tokens[3])))
