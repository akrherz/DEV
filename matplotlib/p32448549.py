import matplotlib.pyplot as plt

ax = plt.axes([0.15, 0.65, 0.8, 0.3])
ax.plot(range(100), range(100))

ax2 = plt.axes([0.15, 0.15, 0.8, 0.3])
ax2.plot(range(100), range(10000, 110000,  1000))

plt.show()
