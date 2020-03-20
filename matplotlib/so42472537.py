import matplotlib.pyplot as plt
from matplotlib import lines


labels = ["LowPower Design", "Pareto Design", "HighPerf Design"]
cats = [
    "q14",
    "q19",
    "q8",
    "q6",
    "q17",
    "q7",
    "q5",
    "q15",
    "q4",
    "q1",
    "q3",
    "q16",
    "q18",
    "q21",
    "q2",
    "q20",
    "q10",
    "q11",
]
fig = plt.figure(figsize=(10, 4))
ax = plt.axes([0.1, 0.2, 0.8, 0.7])
ax.set_xlim(0.5, len(cats) * 3 + 0.5)
ax.set_xticks(range(1, len(cats) * 3 + 1))
ax.set_xticklabels(cats * 3, rotation=90)

# new transparent axis
ax2 = plt.axes([0, 0, 1, 1], facecolor=(1, 1, 1, 0))

pos = ax.get_position()
deltax = pos.width / 3.0
for i in range(4):
    xpos = pos.x0 + deltax * i
    line = lines.Line2D([xpos, xpos], [0.2, 0.05], lw=2.0, color="k")
    ax2.add_line(line)

    if i < 3:
        ax2.text(xpos + deltax / 2.0, 0.05, labels[i], ha="center")

fig.savefig("test.png")
