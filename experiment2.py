from zhang import Grid
from zhang import draw_grid
import pygame
import random
import metriccomputations

colors = list(pygame.color.THECOLORS.keys())
print (colors)
random.shuffle(colors)
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
K=5
#DISPLAY CODE
FPS = 30

CELL_SIZE = 20
WIDTH = HEIGHT = N * CELL_SIZE
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
#END DISPLAY
while running:
    #DISPLAY CODE:
    screen.fill((0, 0, 0))
    draw_grid(screen, g.grid)
    pygame.display.flip()
    clock.tick(FPS)
    #END DISPLAY
    metrics = metriccomputations.compute_metrics(g,races,K)
    running = g.next_step()
    for race in races:
            name = race
            data = metrics[race]
            print(f"{name}:")
            print(f"  Avg distance to nearest different race: {data['avg_distance']:.2f}")
            print(f"  K={K} neighborhood diversity: {data['diversity']:.2%}")
            print(f"  Multiracial edge fraction: {data['edge_fraction']:.2%}\n")
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()

