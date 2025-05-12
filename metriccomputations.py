VACANT = 'vacant'
def calculate_multiracial_edge_fractions(g,races):
    grid = g.grid
    GRID_SIZE = g.N
    race_counts = {}

    for race in races:
        race_counts[race] = {'interracial': 0, 'total': 0} 
    
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            current_race = grid[x][y]
            if current_race == VACANT:
                continue
            
            neighbors = get_neighbors(x, y, g)
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

def compute_metrics(g,races,K):
    grid = g.grid
    GRID_SIZE = g.N
    #Compute k-neighborhood offsets
    k_neighborhood = []
    for dx in range(-K, K+1):
        for dy in range(-K, K+1):
            if dx == 0 and dy == 0:
                continue
            distance = (dx**2 + dy**2)**0.5
            if distance <= K:
                k_neighborhood.append((dx, dy))

    # Compute sorted offsets for nearest neighbor distances
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
    edge_fractions = calculate_multiracial_edge_fractions(g,races)
    for race in races:
        metrics[race]['edge_fraction'] = edge_fractions[race]
    
    return metrics

# Original simulation functions
def get_neighbors(x, y, g):
    grid = g.grid
    GRID_SIZE = g.N
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

def num_interracial_neighbors(x,y,g):
    grid = g.grid
    total_interracial_neighbors = 0
    neighbors = get_neighbors(x,y,g)
    for neighbor in neighbors:
        if((neighbor != grid[x][y]) and bothoccupied([neighbor,grid[x][y]])):
            total_interracial_neighbors += 1
    return total_interracial_neighbors

def total_interracial_edges(g):
    grid = g.grid
    totaledges = 0
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            totaledges += num_interracial_neighbors(i,j,g)
    return totaledges/2

def total_neighbors(x,y,g):
    neighbors = get_neighbors(x,y,g)
    total = 0
    for node in neighbors:
        if (node != VACANT):
            total += 1
    return total

def total_edges(g):
    grid = g.grid
    totaledges = 0
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            totaledges += total_neighbors(i,j,g)
    return totaledges/2

def interracialneighborratio(g):
    total = total_edges(g)
    return total_interracial_edges(g)/total if total > 0 else 0.0

