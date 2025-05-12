import pygame
import random

# Constants
FPS = 30
GRID_SIZE = 25
CELL_SIZE = 20
WIDTH = HEIGHT = GRID_SIZE * CELL_SIZE
PREFERENCE = 100  # homophilic preference for orange agents
ALPHA = 0.25  # fraction of orange among white + orange
BETA = 0.1 # fraction of vacant cells
K = 3  # Neighborhood radius for diversity calculation

# Population calculations
NUM_CELLS = GRID_SIZE * GRID_SIZE
NUM_VACANT = int(BETA * NUM_CELLS)
NUM_BLACK = (NUM_CELLS - NUM_VACANT) // 2
TOTAL_WHITE_ORANGE = NUM_BLACK
NUM_ORANGE = int(ALPHA * TOTAL_WHITE_ORANGE)
NUM_BLUE = 40
NUM_WHITE = TOTAL_WHITE_ORANGE - NUM_ORANGE-NUM_BLUE

# States and Colors
VACANT, BLACK, WHITE, ORANGE, BLUE = 0, 1, 2, 3, 4
races = [BLACK, WHITE, ORANGE, BLUE]
COLORS = {
    VACANT: (200, 200, 200),
    BLACK: (0, 0, 0),
    WHITE: (255, 255, 255),
    ORANGE: (255, 165, 0),
    BLUE: (0,0,255)
}

# Precompute neighborhood offsets for K-radius (toroidal)
k_neighborhood = []
for dx in range(-K, K+1):
    for dy in range(-K, K+1):
        if dx == 0 and dy == 0:
            continue
        distance = (dx**2 + dy**2)**0.5
        if distance <= K:
            k_neighborhood.append((dx, dy))

# Precompute sorted offsets for nearest neighbor distances
sorted_dxdy_dist = []
for dx in range(-GRID_SIZE//2, GRID_SIZE//2 + 1):
    for dy in range(-GRID_SIZE//2, GRID_SIZE//2 + 1):
        if dx == 0 and dy == 0:
            continue
        min_dx = min(abs(dx), GRID_SIZE - abs(dx))
        min_dy = min(abs(dy), GRID_SIZE - abs(dy))
        distance = (min_dx**2 + min_dy**2)**0.5
        sorted_dxdy_dist.append((dx, dy, distance))
sorted_dxdy_dist.sort(key=lambda x: x[2])

def calculate_multiracial_edge_fractions(grid):
    race_counts = {}

    for race in races:
        race_counts[race] = {'interracial': 0, 'total': 0} 
    
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            current_race = grid[x][y]
            if current_race == VACANT:
                continue
            
            neighbors = get_neighbors(x, y, grid)
            total_edges = 0
            interracial_edges = 0
            
            for neighbor in neighbors:
                if neighbor != VACANT:
                    total_edges += 1
                    if neighbor != current_race:
                        interracial_edges += 1
            
            if total_edges > 0:
                race_counts[current_race]['interracial'] += interracial_edges
                race_counts[current_race]['total'] += total_edges
    
    fractions = {}
    for race in races:
        total = race_counts[race]['total']
        fractions[race] = race_counts[race]['interracial'] / total if total > 0 else 0.0
    
    return fractions

def compute_metrics(grid):
    race_data = {}
    for race in races:
        race_data[race] = {'distance_sum': 0, 'distance_count': 0, 'diversity_sum': 0, 'diversity_count': 0}
    
    
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            current_race = grid[x][y]
            if current_race == VACANT:
                continue

            # Calculate nearest different race distance
            min_distance = None
            for dx, dy, dist in sorted_dxdy_dist:
                nx = (x + dx) % GRID_SIZE
                ny = (y + dy) % GRID_SIZE
                neighbor_race = grid[nx][ny]
                if neighbor_race != VACANT and neighbor_race != current_race:
                    min_distance = dist
                    break
            
            # Calculate K-radius diversity
            diff_count = 0
            total_count = 0
            for dx, dy in k_neighborhood:
                nx = (x + dx) % GRID_SIZE
                ny = (y + dy) % GRID_SIZE
                neighbor_race = grid[nx][ny]
                if neighbor_race != VACANT:
                    total_count += 1
                    if neighbor_race != current_race:
                        diff_count += 1
            
            # Update race data
            if min_distance is not None:
                race_data[current_race]['distance_sum'] += min_distance
                race_data[current_race]['distance_count'] += 1
                
            if total_count > 0:
                fraction = diff_count / total_count
                race_data[current_race]['diversity_sum'] += fraction
                race_data[current_race]['diversity_count'] += 1

    # Calculate averages
    metrics = {}
    for race in races:
        metrics[race] = {
            'avg_distance': race_data[race]['distance_sum'] / race_data[race]['distance_count'] if race_data[race]['distance_count'] > 0 else 0,
            'diversity': race_data[race]['diversity_sum'] / race_data[race]['diversity_count'] if race_data[race]['diversity_count'] > 0 else 0
        }
    
    # Add edge fractions
    edge_fractions = calculate_multiracial_edge_fractions(grid)
    for race in races:
        metrics[race]['edge_fraction'] = edge_fractions[race]
    
    return metrics

# Original simulation functions
def get_neighbors(x, y, grid):
    neighbors = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = (x + dx) % GRID_SIZE, (y + dy) % GRID_SIZE
            neighbors.append(grid[nx][ny])
    return neighbors

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
    total = total_edges(grid)
    return total_interracial_edges(grid)/total if total > 0 else 0.0

def utility_black(x, y, grid):
    neighbors = get_neighbors(x, y, grid)
    return 10 - sum(1 for n in neighbors if n in [WHITE, ORANGE])

def utility_white(x, y, grid):
    neighbors = get_neighbors(x, y, grid)
    return 10 - sum(1 for n in neighbors if n in [BLACK, ORANGE])

def utility_orange(x, y, grid):
    neighbors = get_neighbors(x, y, grid)
    white_neighbors = sum(1 for n in neighbors if n in [WHITE, ORANGE])
    black_neighbors = sum(1 for n in neighbors if n == BLACK)
    return 10 + PREFERENCE * white_neighbors - black_neighbors

def utility_blue(x, y, grid):
    neighbors = get_neighbors(x, y, grid)
    white_neighbors = sum(1 for n in neighbors if n in [WHITE, ORANGE])
    black_neighbors = sum(1 for n in neighbors if n == BLACK)
    blue_neighbors = sum(1 for n in neighbors if n == BLUE)
    return 10 + PREFERENCE * blue_neighbors - black_neighbors - white_neighbors

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
    for _ in range(NUM_BLUE):
        x, y = positions[idx]
        grid[x][y] = BLUE
        idx += 1
    return grid

def simulate_step(grid):
    candidates = []
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            agent = grid[i][j]
            if agent in races:
                if agent == BLACK:
                    u_old = utility_black(i, j, grid)
                elif agent == WHITE:
                    u_old = utility_white(i, j, grid)
                elif agent == BLUE:
                    u_old = utility_blue(i, j, grid)
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
                            elif agent == BLUE:
                                u_new = utility_blue(ni, nj, grid_copy)
                            else:
                                u_new = utility_orange(ni, nj, grid_copy)
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
    pygame.display.set_caption("Enhanced Segregation Model")
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
        
        # Calculate metrics
        metrics = compute_metrics(grid)
        interracial_ratio = interracialneighborratio(grid)

        # Display results
        print(f"\nStep {step}")
        print("=" * 30)
        print(f"Global interracial neighbor ratio: {interracial_ratio:.2%}")
        for race in races:
            name = ["Black", "White", "Orange","Blue"][race-1]
            data = metrics[race]
            print(f"{name}:")
            print(f"  Avg distance to nearest different race: {data['avg_distance']:.2f}")
            print(f"  K={K} neighborhood diversity: {data['diversity']:.2%}")
            print(f"  Multiracial edge fraction: {data['edge_fraction']:.2%}\n")

        # Drawing
        screen.fill((0, 0, 0))
        draw_grid(screen, grid)
        pygame.display.flip()
        clock.tick(FPS)
        step += 1

    pygame.quit()

if __name__ == "__main__":
    main()
