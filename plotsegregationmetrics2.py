import numpy as np
import pandas as pd
from itertools import product
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from matplotlib.ticker import MaxNLocator
import matplotlib.colors as mcolors



matplotlib.rcParams.update({'font.size': 18})

filename = './results2.csv'
results = pd.read_csv(filename).values

races = ["white", "black"]
metrics = ["avg_dist", "K_div", "multi_racial_fraction", "dist_to_furthest", "fraction_of_rarest"]

num_races = [2, 4, 6, 8, 10]

d = {i: [[] for _ in range(5)] for i in races}
print(d)

for k in results:
    for i in range(5):
        if k[1] == "white" or k[1] == "black":
            d[k[1]][i].append(k[i+2])


for i in range(5):
    for r in races:
            if r == "white":
                color = "r"
            else:
                color = "b"
            plt.plot(num_races,d[r][i], label=f"{r} agents" ,color=color, marker='o', linestyle='-',markersize=4, linewidth=0.8 )
        #ax = plt.gca()
        #ax.set_ylim([0,1])
    plt.tight_layout()
    plt.legend(loc="upper right")
    plt.savefig(f"plot_experiment2_{metrics[i]}.png")
    plt.clf()



        






