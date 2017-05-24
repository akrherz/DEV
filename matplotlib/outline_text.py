import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects

(fig, ax) = plt.subplots(1,1)

txt = ax.text(0.5,0.5, "SPC Drulz", color='k', size=30, ha='center')
txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                 foreground="green")])

fig.savefig('test.png')
