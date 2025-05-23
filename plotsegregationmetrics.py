import numpy as np
import pandas as pd
from itertools import product
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from matplotlib.ticker import MaxNLocator
import matplotlib.colors as mcolors



colors = list(mcolors.TABLEAU_COLORS.keys())[:3]
print(colors)

matplotlib.rcParams.update({'font.size': 18})

filename = './results1.csv'
results = pd.read_csv(filename).values

races = ["white", "black", "orange"]
metrics = ["avg_dist", "K_div", "multi_racial_fraction", "dist_to_furthest", "fraction_of_rarest"]


orange = []

d = {"white":[[] for _ in range(5)], "black":[[] for _ in range(5)], "orange":[[] for _ in range(5)]}


for k in results:
    if k[0] not in orange:
        orange.append(k[0])
    for i in range(5):
        d[k[1]][i].append(k[i+2])



for i in range(5):
    for r in races:
        plt.plot(orange,d[r][i], label=f"{r}" ,color=colors[races.index(r)], marker='o', linestyle='-',markersize=4, linewidth=0.8 )
    #ax = plt.gca()
    #ax.set_ylim([0,1])
    plt.tight_layout()
    plt.legend(loc="upper right")
    plt.savefig(f"plot_experiment1_{metrics[i]}.png")
    plt.clf()



        






