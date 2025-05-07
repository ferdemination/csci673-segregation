import pygame
import numpy as np
import random

# Constants
FPS = 30

GRID_SIZE = 20
CELL_SIZE = 20
WIDTH = HEIGHT = GRID_SIZE * CELL_SIZE

PREFERENCE = 1000000  # homophilic preference for orange agents

ALPHA = 0.25  # fraction of orange among white + orange
BETA = 0.1 # fraction of vacant cells

# Population sizes
NUM_CELLS = GRID_SIZE * GRID_SIZE
NUM_VACANT = int(BETA * NUM_CELLS)
NUM_BLACK = (NUM_CELLS - NUM_VACANT) // 2
TOTAL_WHITE_ORANGE = NUM_BLACK
NUM_ORANGE = int(ALPHA * TOTAL_WHITE_ORANGE)
NUM_WHITE = TOTAL_WHITE_ORANGE - NUM_ORANGE

# States: 0 = vacant, 1 = black, 2 = white, 3 = orange
VACANT = 0
BLACK = 1
WHITE = 2
ORANGE = 3

# Colors
COLORS = {
    VACANT: (200, 200, 200),
    BLACK: (0, 0, 0),
    WHITE: (255, 255, 255),
    ORANGE: (255, 165, 0)
}

# Neighborhood definition: Moore neighborhood
def get_neighbors(x, y, grid):
    neighbors = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = (x + dx) % GRID_SIZE, (y + dy) % GRID_SIZE
            neighbors.append(grid[nx][ny])
    return neighbors


#Calculate segregation metrics

def bothoccupied(edge):
    return (edge[0] != VACANT) and (edge[1] != VACANT)

def num_interracial_neighbors(x,y,grid):
    total_interracial_neighbors = 0
    neighbors = get_neighbors(x,y,grid)
    for neighbor in neighbors:
        if((neighbor != grid[x][y]) and bothoccupied([neighbor,grid[x][y]])):
            total_interracial_neighbors += 1
    return total_interracial_neighbors

def total_interracial_edges(grid):
    totaledges = 0
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            totaledges += num_interracial_neighbors(i,j,grid)
    return totaledges/2

def total_neighbors(x,y,grid):
    neighbors = get_neighbors(x,y,grid)
    total = 0
    for node in neighbors:
        if (node != VACANT):
            total += 1
    return total

def total_edges(grid):
    totaledges = 0
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            totaledges += total_neighbors(i,j,grid)
    return totaledges/2

def interracialneighborratio(grid):
    if(total_edges(grid) > 0):
        return total_interracial_edges(grid)/total_edges(grid)
    else:
        print('no neighbors')
        return 0

# Utility functions
def utility_black(x, y, grid):
    neighbors = get_neighbors(x, y, grid)
    return 10 - sum(1 for n in neighbors if n in [BLACK, WHITE, ORANGE])

def utility_white(x, y, grid):
    neighbors = get_neighbors(x, y, grid)
    return 10 - sum(1 for n in neighbors if n in [BLACK, WHITE, ORANGE])

def utility_orange(x, y, grid):
    neighbors = get_neighbors(x, y, grid)
    white_neighbors = sum(1 for n in neighbors if n in [WHITE, ORANGE])
    black_neighbors = sum(1 for n in neighbors if n == BLACK)
    return 10 + PREFERENCE * white_neighbors - black_neighbors

# Initialize grid with random agent placement
def initialize_grid():
    total_agents = NUM_BLACK + NUM_WHITE + NUM_ORANGE
    positions = [(i, j) for i in range(GRID_SIZE) for j in range(GRID_SIZE)]
    random.shuffle(positions)

    grid = [[VACANT for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    idx = 0
    for _ in range(NUM_BLACK):
        x, y = positions[idx]
        grid[x][y] = BLACK
        idx += 1
    for _ in range(NUM_WHITE):
        x, y = positions[idx]
        grid[x][y] = WHITE
        idx += 1
    for _ in range(NUM_ORANGE):
        x, y = positions[idx]
        grid[x][y] = ORANGE
        idx += 1
    return grid

def simulate_step(grid):
    candidates = []
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            agent = grid[i][j]
            if agent in (BLACK, WHITE, ORANGE):
                if agent == BLACK:
                    u_old = utility_black(i, j, grid)
                elif agent == WHITE:
                    u_old = utility_white(i, j, grid)
                else:
                    u_old = utility_orange(i, j, grid)

                for ni in range(GRID_SIZE):
                    for nj in range(GRID_SIZE):
                        if grid[ni][nj] == VACANT:
                            grid_copy = [row[:] for row in grid]
                            grid_copy[ni][nj] = agent
                            grid_copy[i][j] = VACANT
                            if agent == BLACK:
                                u_new = utility_black(ni, nj, grid_copy)
                            elif agent == WHITE:
                                u_new = utility_white(ni, nj, grid_copy)
                            else:
                                u_new = utility_orange(ni, nj, grid_copy)
                            delta_u = u_new - u_old
                            if delta_u > 0:
                                candidates.append((delta_u, u_old, u_new, (i, j), (ni, nj)))

    if candidates:
        candidates.sort(reverse=True, key=lambda x: x[0])
        delta_u, u_old, u_new, (from_x, from_y), (to_x, to_y) = candidates[0]
        print(f"Move from ({from_x}, {from_y}) to ({to_x}, {to_y}) | Previous Utility: {u_old:.2f}, New Utility: {u_new:.2f}, Change: {delta_u:.2f}")
        print('RATIO OF INTERRACIAL NEIGHBORS:' + str(interracialneighborratio(grid)))
        grid[to_x][to_y] = grid[from_x][from_y]
        grid[from_x][from_y] = VACANT
        return True
    return False

def draw_grid(screen, grid):
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            pygame.draw.rect(screen, COLORS[grid[i][j]], (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, (100, 100, 100), (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Zhang's Segregation Model")
    clock = pygame.time.Clock()

    grid = initialize_grid()
    running = True

    while running:
        screen.fill((0, 0, 0))
        draw_grid(screen, grid)
        pygame.display.flip()
        clock.tick(FPS)

        simulate_step(grid)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()

if __name__ == '__main__':
    main()
