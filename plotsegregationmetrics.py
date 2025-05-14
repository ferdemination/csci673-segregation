import pygame
import random
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

# Simulation parameters
NUM_REPETITIONS = 5  # Number of runs per parameter set
T = 50               # Number of timesteps per run
PREFERENCE_VALUES = [5, 10, 15]  # Different affinity levels to test
ALPHA = 0.25
BETA = 0.1
K = 3
GRID_SIZE = 25

# Results storage structure
results = {
    pref: {
        'distance': np.zeros((NUM_REPETITIONS, T)),
        'diversity': np.zeros((NUM_REPETITIONS, T)),
        'edges': np.zeros((NUM_REPETITIONS, T)),
        'global_ratio': np.zeros((NUM_REPETITIONS, T))
    } for pref in PREFERENCE_VALUES
}

def run_simulation(preference, repetition):
    # Modified simulation code without visualization
    grid = initialize_grid()
    metrics_series = []
    
    for step in range(T):
        # Simulation step
        simulate_step(grid, preference)
        
        # Calculate metrics
        metrics = compute_metrics(grid)
        interracial_ratio = interracialneighborratio(grid)
        
        # Store results
        metrics_series.append({
            'distance': [metrics[race]['avg_distance'] for race in [BLACK, WHITE, ORANGE]],
            'diversity': [metrics[race]['diversity'] for race in [BLACK, WHITE, ORANGE]],
            'edges': [metrics[race]['edge_fraction'] for race in [BLACK, WHITE, ORANGE]],
            'global_ratio': interracial_ratio
        })
    
    return metrics_series

def simulate_step(grid, preference):
    # Modified simulation step with parameterized preference
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
                    u_old = utility_orange(i, j, grid, preference)
                
                # Rest of the simulation step logic...
                # (maintain the original movement logic but using parameterized preference)

def utility_orange(x, y, grid, preference):
    neighbors = get_neighbors(x, y, grid)
    white_neighbors = sum(1 for n in neighbors if n in [WHITE, ORANGE])
    black_neighbors = sum(1 for n in neighbors if n == BLACK)
    return 10 + preference * white_neighbors - black_neighbors

# Main simulation loop
for preference in PREFERENCE_VALUES:
    print(f"\nRunning simulations for preference={preference}")
    for rep in tqdm(range(NUM_REPETITIONS)):
        metrics = run_simulation(preference, rep)
        
        # Store results averaged across races
        for t in range(T):
            results[preference]['distance'][rep, t] = np.mean(metrics[t]['distance'])
            results[preference]['diversity'][rep, t] = np.mean(metrics[t]['diversity'])
            results[preference]['edges'][rep, t] = np.mean(metrics[t]['edges'])
            results[preference]['global_ratio'][rep, t] = metrics[t]['global_ratio']

# Plotting function
def plot_results():
    metrics = ['distance', 'diversity', 'edges', 'global_ratio']
    titles = [
        'Average Distance to Nearest Different Race',
        'K-Neighborhood Diversity',
        'Multiracial Edge Fraction',
        'Global Interracial Ratio'
    ]
    
    plt.figure(figsize=(15, 10))
    for i, metric in enumerate(metrics):
        plt.subplot(2, 2, i+1)
        for preference in PREFERENCE_VALUES:
            mean = np.mean(results[preference][metric], axis=0)
            std = np.std(results[preference][metric], axis=0)
            plt.plot(mean, label=f'Pref={preference}')
            plt.fill_between(range(T), mean-std, mean+std, alpha=0.2)
            
        plt.title(titles[i])
        plt.xlabel('Timestep')
        plt.ylabel('Value' if i < 3 else 'Ratio')
        plt.grid(True)
        plt.legend()
    
    plt.tight_layout()
    plt.savefig('simulation_results.png')
    plt.show()

# Run plotting
plot_results()
