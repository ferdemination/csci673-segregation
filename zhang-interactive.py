import pygame
import numpy as np

# Constants
GRID_SIZE = 20
CELL_SIZE = 30
WIDTH = HEIGHT = GRID_SIZE * CELL_SIZE
FPS = 30
PREFERENCE = 1.0  # y = p - 1 in Zhang's model
BETA = 2.0

# States: 0 = vacant, 1 = black, 2 = white
VACANT = 0
BLACK = 1
WHITE = 2

# Colors
COLORS = {
    VACANT: (200, 200, 200),
    BLACK: (0, 0, 0),
    WHITE: (255, 255, 255)
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

# Utility functions
def utility_black(x, y, grid):
    neighbors = get_neighbors(x, y, grid)
    return 10 - sum(1 for n in neighbors if n in [BLACK, WHITE])

def utility_white(x, y, grid):
    neighbors = get_neighbors(x, y, grid)
    white_neighbors = sum(1 for n in neighbors if n == WHITE)
    black_neighbors = sum(1 for n in neighbors if n == BLACK)
    return 10 + PREFERENCE * white_neighbors - black_neighbors

def move_decision(delta_u):
    try:
        return np.exp(BETA * delta_u) / (1 + np.exp(BETA * delta_u))
    except OverflowError:
        return 1.0 if delta_u > 0 else 0.0

# Initialize empty grid
def initialize_grid():
    return [[VACANT for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

def simulate_step(grid):
    candidates = []
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            agent = grid[i][j]
            if agent in (BLACK, WHITE):
                u_old = utility_black(i, j, grid) if agent == BLACK else utility_white(i, j, grid)
                for ni in range(GRID_SIZE):
                    for nj in range(GRID_SIZE):
                        if grid[ni][nj] == VACANT:
                            grid_copy = [row[:] for row in grid]
                            grid_copy[ni][nj] = agent
                            grid_copy[i][j] = VACANT
                            u_new = utility_black(ni, nj, grid_copy) if agent == BLACK else utility_white(ni, nj, grid_copy)
                            delta_u = u_new - u_old
                            if delta_u > 0:
                                candidates.append((delta_u, u_old, u_new, (i, j), (ni, nj)))

    if candidates:
        candidates.sort(reverse=True, key=lambda x: x[0])  # Prioritize biggest utility gain
        delta_u, u_old, u_new, (from_x, from_y), (to_x, to_y) = candidates[0]
        print(f"Move from ({from_x}, {from_y}) to ({to_x}, {to_y}) | Previous Utility: {u_old:.2f}, New Utility: {u_new:.2f}, Change: {delta_u:.2f}")
        grid[to_x][to_y] = grid[from_x][from_y]
        grid[from_x][from_y] = VACANT

    return grid

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
    paint_mode = None  # None, WHITE, or BLACK

    while running:
        screen.fill((0, 0, 0))
        draw_grid(screen, grid)
        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    grid = simulate_step(grid)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                grid_x = y // CELL_SIZE
                grid_y = x // CELL_SIZE
                if event.button == 1:  # Left click starts white paint
                    paint_mode = WHITE
                elif event.button == 3:  # Right click starts black paint
                    paint_mode = BLACK

            elif event.type == pygame.MOUSEBUTTONUP:
                paint_mode = None

            elif event.type == pygame.MOUSEMOTION and paint_mode is not None:
                x, y = pygame.mouse.get_pos()
                grid_x = y // CELL_SIZE
                grid_y = x // CELL_SIZE
                if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                    grid[grid_x][grid_y] = paint_mode

    pygame.quit()

if __name__ == '__main__':
    main()
