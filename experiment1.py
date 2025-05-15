from zhang import Grid
from zhang import draw_grid
import pygame
import random
import csv
import metriccomputations


# N x N grid size
N = 30
num_races = 3                          
colors = ["white", "black", "orange"]
# defines a color->index coreespondence
color_dict = {c:colors.index(c) for c in colors}

p = [[-1,-1,-1], [-1,-1,-1], [0,-1,0]]

fracs = [ _ / 10 for _ in range(1,10)]
num_occupants = 300
num_orange = [int( _ * num_occupants) for _ in fracs]

for no in num_orange:
    races = {i: (num_occupants if i == "white" or i == "black" else no)
             for i in colors }
    print(races)
    g = Grid(N=N,p=p,color_dict=color_dict,colors=races)
    running = True
    K=5
    while running:
        metrics = metriccomputations.compute_metrics(g,colors,K)
        running = g.next_step()
    with open(f"results1.csv", "a", newline= '') as file:
        writer = csv.writer(file)
        field = ["race","avg_dist","K_div","multi_racial_fraction","dist_to_furthest","fraction_of_rarest"]
        writer.writerow(field)
    with open("results1.csv", "a", newline='') as file:
        writer = csv.writer(file)
        for col in colors:
            data = metrics[col]
            writer.writerow([ col, data['avg_distance'], data['diversity'], data['edge_fraction'], data['WORST_avg_distance'], data['WORST_diversity'] ])
