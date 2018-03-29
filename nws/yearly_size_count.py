data = """1986	10752	3.359675943
1987	9410	2.957760204
1988	8562	2.74379185
1989	11943	3.510978618
1990	13691	4.212191386
1991	14879	4.672753159
1992	15132	4.881984657
1993	16099	5.037628107
1994	19095	5.912006314
1995	25673	8.079955111
1996	28135	10.38284501
1997	25665	10.24004427
1998	34862	10.94563372
1999	26998	9.765674179
2000	29099	9.234155436
2001	28009	9.899277887
2002	27390	9.377886697
2003	31705	10.40794747
2004	32737	11.38637938
2005	34330	12.85727738
2006	37918	13.28290632
2007	34740	13.20591541
2008	73712	23.01063608
2009	60630	18.43535608
2010	59812	19.13474649
2011	85160	23.7556
2012	58783	17.2
2013	48024	16.86
2014	46132	15.48
2015    50654   17.99"""
data = """1986	0	0
1987	0	0
1988	0	0
1989	0	0
1990	0	0
1991	0	0
1992	0	0
1993	0	0
1994	0	0
1995	0	0
1996	0	0
1997	0	0
1998	0	0
1999	0	0
2000	0	0
2001	0	0
2002	0	0
2003	22892	3.5
2004	24291	3.9
2005	24196	4
2006	27105	4.1
2007	23810	3.86
2008	31274	6.6
2009	24100	5.2
2010	22762	5.2
2011	30124	7.2
2012	22562	4.8
2013	16760   4.02
2014    18309   4.09
2015    20579   4.22"""
counts = []
sizes = []
years = []
for line in data.split("\n"):
  tokens = line.split()
  years.append( int(tokens[0]) )
  sizes.append( float(tokens[2]) )
  counts.append( float(tokens[1]) )

import matplotlib.pyplot as plt
import numpy as np

sizes = np.array(sizes)
counts = np.array(counts)
years = np.array(years)

(fig, ax) = plt.subplots(1,1)

ax.bar(years-0.4, counts, width=0.4, fc='r')
ax.set_ylabel("Warning Count", color='r')

y2 = ax.twinx()
y2.bar(years, sizes, width=0.4, fc='b')
y2.set_ylabel("Size (Continental United States)", color='b')

p1 = plt.Rectangle((0, 0), 1, 1, fc="r")
p3 = plt.Rectangle((0, 0), 1, 1, fc="b")
ax.legend([p1,p3], ["Counts", "Size"], loc=2)
ax.grid(True)

ax.set_title("NWS *Polygon* Tornado + Severe Thunderstorm Warnings")
ax.set_ylim(0,90000)
y2.set_ylim(0,25)
ax.set_xlim(right=2016)

fig.savefig('yearly_size_counts_polygon.png', dpi=100)
