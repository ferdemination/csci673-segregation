from zhang import Grid
from zhang import draw_grid
import pygame
import random
import csv
import metriccomputations


# N x N grid size
N = 30
num_races = [2,4,6,8,10]                            
matching = {"white":"black", "red":"blue", "orange":"green", "brown":"yellow", "purple":"pink"}
colors = []
for r in matching:
    colors.append(r)
    colors.append(matching[r])
print(colors)
# defines a color->index coreespondence
color_dict = {c:colors.index(c) for c in colors}
print(color_dict)

num_occupants = 100



p = []
for (race,mrace) in matching.items():
    cand1 = [0 for _ in colors]
    cand2 = [0 for _ in colors]
    cand1[color_dict[mrace]] = -1
    cand2[color_dict[race]] = -1
    p.append(cand1)
    p.append(cand2)

for r in num_races:
    num_occupants = 800 // r
    curr_colors = colors[:r]
    races = {i:num_occupants for i in curr_colors}
    g = Grid(N=N,p=p,color_dict=color_dict,colors=races)
    running = True
    K=3
    while running:
        metrics = metriccomputations.compute_metrics(g,curr_colors,K)
        running = g.next_step()
    with open(f"results2.csv", "a", newline= '') as file:
        writer = csv.writer(file)
        field = ["num_of_races","race","avg_dist","K_div","multi_racial_fraction","dist_to_furthest","fraction_of_rarest"]
        writer.writerow(field)
    with open("results2.csv", "a", newline='') as file:
        writer = csv.writer(file)
        for col in curr_colors:
            data = metrics[col]
            writer.writerow([ r, col, data['avg_distance'], data['diversity'], data['edge_fraction'], data['WORST_avg_distance'], data['WORST_diversity'] ])
