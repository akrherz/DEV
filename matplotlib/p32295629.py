import numpy as np

import matplotlib.pyplot as plt

students = ["steve", "bob", "ralph"]
progress = [[1, 3, 4, 4, 5], [2, 3, 4, 4, 5], [3, 3, 4, 5, 5]]

(fig, ax) = plt.subplots(1, 1)

dx = 1.0 / len(progress)
xoff = dx / 2.0
for i, (name, data) in enumerate(zip(students, progress)):
    ax.plot(np.arange(len(data)) + xoff, data, label=name, marker="o")
    xoff += dx

ax.set_xticks(np.arange(0, len(progress[0]) + 0.01, dx), minor=True)
ax.set_xticks(np.arange(1, len(progress[0]) + 1))
labels = students * len(progress[0])
week = 1
for i, ll in enumerate(labels):
    if ll == students[1]:
        labels[i] = "%s\nWeek %s" % (ll, week)
        week += 1
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.set_xticklabels(labels, fontsize=8, ha="left", minor=True)
ax.set_xticklabels([])
ax.tick_params(which="both", direction="out")
ax.tick_params(axis="x", which="major", width=4)
ax.tick_params(axis="x", which="major", length=7)
ax.tick_params(axis="y", which="major", width=0, length=0)

ax.set_ylim(0, 6)
ax.set_yticks(range(1, 6))

ax.get_xaxis().tick_bottom()
ax.get_yaxis().tick_left()

ax.set_title("Student Progress")

ax.legend(loc="best")

fig.savefig("test.png")
