import datetime

import matplotlib.pyplot as plt

x = [
    "Mon Sep 1 16:40:20 2015",
    "Mon Sep 1 16:45:20 2015",
    "Mon Sep 1 16:50:20 2015",
    "Mon Sep 1 16:55:20 2015",
]
y = range(4)

x = [datetime.datetime.strptime(elem, "%a %b %d %H:%M:%S %Y") for elem in x]

(fig, ax) = plt.subplots(1, 1)
ax.plot(x, y)
fig.show()

fig.savefig("test.png")
