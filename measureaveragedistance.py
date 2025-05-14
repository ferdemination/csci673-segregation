import pygame
import numpy as np
import random

# Constants
FPS = 30
GRID_SIZE = 25
CELL_SIZE = 20
WIDTH = HEIGHT = GRID_SIZE * CELL_SIZE
PREFERENCE = 10  # homophilic preference for orange agents
ALPHA = 0.25  # fraction of orange among white + orange
BETA = 0.1  # fraction of vacant cells

# Population calculations
NUM_CELLS = GRID_SIZE * GRID_SIZE
NUM_VACANT = int(BETA * NUM_CELLS)
NUM_BLACK = (NUM_CELLS - NUM_VACANT) // 2
TOTAL_WHITE_ORANGE = NUM_BLACK
NUM_ORANGE = int(ALPHA * TOTAL_WHITE_ORANGE)
NUM_WHITE = TOTAL_WHITE_ORANGE - NUM_ORANGE

# States and Colors
VACANT, BLACK, WHITE, ORANGE = 0, 1, 2, 3
COLORS = {
    VACANT: (200, 200, 200),
    BLACK: (0, 0, 0),
    WHITE: (255, 255, 255),
    ORANGE: (255, 165, 0)
}

# Precompute sorted offsets for toroidal distance checks
sorted_dxdy_dist = []
for dx in range(-GRID_SIZE + 1, GRID_SIZE):
    for dy in range(-GRID_SIZE + 1, GRID_SIZE):
        if dx == 0 and dy == 0:
            continue
        min_dx = min(abs(dx), GRID_SIZE - abs(dx))
        min_dy = min(abs(dy), GRID_SIZE - abs(dy))
        distance = (min_dx**2 + min_dy**2)**0.5
        sorted_dxdy_dist.append((dx, dy, distance))
sorted_dxdy_dist.sort(key=lambda x: x[2])

def compute_average_distances(grid):
    race_data = {
        BLACK: {'distances': [], 'count': 0},
        WHITE: {'distances': [], 'count': 0},
        ORANGE: {'distances': [], 'count': 0}
    }
    
    # First pass to count agents
    present_races = set()
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            race = grid[x][y]
            if race != VACANT:
                present_races.add(race)
                race_data[race]['count'] += 1

    if len(present_races) < 2:
        return {k: 0.0 for k in race_data}

    # Second pass to calculate distances
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            current_race = grid[x][y]
            if current_race == VACANT:
                continue
                
            min_distance = None
            for dx, dy, dist in sorted_dxdy_dist:
                nx = (x + dx) % GRID_SIZE
                ny = (y + dy) % GRID_SIZE
                neighbor_race = grid[nx][ny]
                if neighbor_race != VACANT and neighbor_race != current_race:
                    min_distance = dist
                    break

            if min_distance is not None:
                race_data[current_race]['distances'].append(min_distance)

    # Calculate averages
    averages = {}
    for race, data in race_data.items():
        if data['count'] == 0 or len(data['distances']) == 0:
            averages[race] = 0.0
        else:
            averages[race] = sum(data['distances']) / len(data['distances'])
    return averages

# Existing helper functions remain unchanged
def get_neighbors(x, y, grid):
    neighbors = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = (x + dx) % GRID_SIZE, (y + dy) % GRID_SIZE
            neighbors.append(grid[nx][ny])
    return neighbors

# Existing utility functions and simulation logic remain unchanged
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

def initialize_grid():
    grid = [[VACANT for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    positions = [(i, j) for i in range(GRID_SIZE) for j in range(GRID_SIZE)]
    random.shuffle(positions)
    
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
                u_old = utility_black(i, j, grid) if agent == BLACK else \
                        utility_white(i, j, grid) if agent == WHITE else \
                        utility_orange(i, j, grid)
                
                for ni in range(GRID_SIZE):
                    for nj in range(GRID_SIZE):
                        if grid[ni][nj] == VACANT:
                            grid_copy = [row[:] for row in grid]
                            grid_copy[ni][nj] = agent
                            grid_copy[i][j] = VACANT
                            u_new = utility_black(ni, nj, grid_copy) if agent == BLACK else \
                                    utility_white(ni, nj, grid_copy) if agent == WHITE else \
                                    utility_orange(ni, nj, grid_copy)
                            delta_u = u_new - u_old
                            if delta_u > 0:
                                candidates.append((delta_u, u_old, u_new, (i, j), (ni, nj)))

    if candidates:
        candidates.sort(reverse=True, key=lambda x: x[0])
        delta_u, u_old, u_new, (from_x, from_y), (to_x, to_y) = candidates[0]
        grid[to_x][to_y] = grid[from_x][from_y]
        grid[from_x][from_y] = VACANT
        return True
    return False

def draw_grid(screen, grid):
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            pygame.draw.rect(screen, COLORS[grid[i][j]], 
                           (j*CELL_SIZE, i*CELL_SIZE, CELL_SIZE, CELL_SIZE))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Segregation Model with Distance Metrics")
    clock = pygame.time.Clock()
    grid = initialize_grid()
    step = 0
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Simulation step
        moved = simulate_step(grid)
        
        # Calculate and display metrics
        avg_distances = compute_average_distances(grid)
        print(f"\nStep {step}")
        print("-------------------")
        print(f"Black avg distance: {avg_distances[BLACK]:.2f}")
        print(f"White avg distance: {avg_distances[WHITE]:.2f}")
        print(f"Orange avg distance: {avg_distances[ORANGE]:.2f}")

        # Drawing
        screen.fill((0, 0, 0))
        draw_grid(screen, grid)
        pygame.display.flip()
        clock.tick(FPS)
        step += 1

    pygame.quit()

if __name__ == "__main__":
    main()
