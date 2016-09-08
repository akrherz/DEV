import matplotlib.pyplot as plt

counts = []
xticks = []
xticklabels = []

for linenum, line in enumerate(open('data.csv')):
  (year, month, count) = line.split(",")
  counts.append( float(count) )
  if month == "1":
    xticks.append(linenum)
    xticklabels.append( year)
(fig, ax)  = plt.subplots(1,1)

ax.bar(range(len(counts)), counts,fc='g', ec='g')
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
ax.grid(True)
ax.set_title("May 2001 - June 2014:: Emails sent by daryl per month")
ax.set_ylabel("email messages saved to sent-mail")

fig.savefig('test.png')
