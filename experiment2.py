from zhang import Grid
import pygame
import random

colors = list(pygame.color.THECOLORS.keys())
print (colors)
#random.shuffle(colors)
# N x N grid size
N = 30
num_races = 8 # must be multiple of 2 for this experiment                                      
races = colors[:num_races] #take the first num_races colors
num_occupants = 100
colors = {r:num_occupants for r in races}

# defines a color->index coreespondence
color_dict = {c:races.index(c) for c in races}
matching = {races[i]:races[i+1] for i in range(0,len(races),2)}
print(matching)

p = []
for (race,mrace) in matching.items():
    cand1 = [0 for _ in races]
    cand2 = [0 for _ in races]
    cand1[color_dict[mrace]] = -1
    cand2[color_dict[race]] = -1
    p.append(cand1)
    p.append(cand2)
print(p)
g = Grid(N=N,p=p,color_dict=color_dict,colors=colors)

running = True
while running:
    running = g.next_step()