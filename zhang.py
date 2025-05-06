from enum import Enum
from itertools import product
import random
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Simulating Zhang's model of segregation https://wordpress.clarku.edu/wp-content/uploads/sites/423/2016/03/segregation.pdf

class Grid:
    def __init__(self, N, Y, num_black, num_vacant, alpha=0.1):
        self.N = N
        self.Y = Y
        self.grid = [[None for _ in range(N)] for _ in range(N)]

        total_cells = N * N
        num_white = total_cells - num_black - num_vacant

        if num_white < 0:
            raise ValueError("Too many black and vacant cells for the grid size.")

        # Create cell types
        cells = (['black'] * num_black +
                 ['vacant'] * num_vacant +
                 ['white'] * num_white)
        random.shuffle(cells)

        # Assign types and deltas
        idx = 0
        for i in range(N):
            for j in range(N):
                cell_type = cells[idx]
                delta = self.get_delta_for_type(cell_type, alpha)
                self.grid[i][j] = {'type': cell_type, 'delta': delta}
                idx += 1

    def get_delta_for_type(self, cell_type, alpha):
        if cell_type == 'black':
            return 1
        elif cell_type == 'vacant':
            return -1
        elif cell_type == 'white':
            # α fraction of white cells get a random non-zero delta (e.g. from -5 to 5, excluding 0)
            if random.random() > alpha:
                return 1
            else:
                return 0

    def display(self):
        for row in self.grid:
            print([f"{cell['type'][0].upper()}:{cell['delta']}" for cell in row])
        print()

    def swap_cells(self, pos1, pos2):
        i1, j1 = pos1
        i2, j2 = pos2
        self.grid[i1][j1], self.grid[i2][j2] = self.grid[i2][j2], self.grid[i1][j1]

    def get_neighborhood(self, pos, neigh_type = "vn"):
        x_pos,y_pos = pos
        neigh = []
        temp_x = []
        temp_y = []
        if x_pos != 0:
            neigh.append((x_pos - 1,y_pos))
            temp_x.append(x_pos - 1)
        if x_pos != N-1:
            neigh.append((x_pos + 1, y_pos))
            temp_x.append(x_pos + 1)
        if y_pos != 0:
            neigh.append((x_pos, y_pos - 1))
            temp_y.append(y_pos - 1)
        if y_pos != N-1:
            neigh.append((x_pos,y_pos + 1))
            temp_y.append(y_pos + 1)
        if neigh_type == "moore":
            res = list(product(temp_x,temp_y))
            neigh.extend(res)
    
        return neigh

    # for utility of black agents use delta = 1 always (for this model at least)
    def get_utility(self, pos,delta):
        neigh = self.get_neighborhood(pos)

        if delta == -1:
            raise ValueError("Utility is undefined for vacant cells")
        whites = 0
        blacks = 0

        for (i,j) in neigh:
            if self.grid[i][j]['type'] == "white":
                whites += 1
            elif self.grid[i][j]['type'] == "black":
                blacks += 1

            return Y - delta * whites - blacks
    def get_two_random_positions(self):
        positions = [(i, j) for i in range(self.N) for j in range(self.N)]
        return random.sample(positions, 2)
    
    def get_type(self,pos):
        pos_x, pos_y = pos
        return self.grid[pos_x][pos_y]["type"]

    def get_delta(self,pos):
        pos_x, pos_y = pos
        return self.grid[pos_x][pos_y]["delta"]
    

Y = 10                                      # fixed income
N = 30                                      # N x N grid size
num_black = 400                             # Black agents
num_white = 400                            # White agents
num_vacant = N*N - num_black - num_white    # total vacant spots
alpha = 0.01                                # fraction of intorelant White agents
beta  = 2

def log_linear_accept(u1,u2, beta=1.0):
    # Compute acceptance probability for swapping
    prob = math.exp(beta * u2) / (math.exp(beta * u1) + math.exp(beta * u2))
    return prob

def animate_grid(grid, steps=100, interval=300, beta=1.0, show_delta=False):
    N = grid.N
    type_to_color = {'black': 'black', 'white': 'white', 'vacant': 'gray'}

    fig, ax = plt.subplots()
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(0, N)
    ax.set_ylim(0, N)
    ax.set_aspect('equal')

    # Initial state
    patches = [[plt.Rectangle((j, N-1-i), 1, 1, color='white') for j in range(N)] for i in range(N)]
    for row in patches:
        for patch in row:
            ax.add_patch(patch)

    delta_text = [[ax.text(j + 0.5, N - 1 - i + 0.5, '', ha='center', va='center', fontsize=8, color='red')
                   for j in range(N)] for i in range(N)]

    def update(frame):
        list_pos = g.get_two_random_positions()
        pos1 = list_pos[0]
        pos2 = list_pos[1]
        delta1 = g.get_delta(pos1)
        delta2 = g.get_delta(pos2)
        type1 = g.get_type(pos1)
        type2 = g.get_type(pos2)


        if(type1 == "vacant" and type2 != "vacant"):
            # compares utility of agent 2 in pos1 and pos2
            u_move = g.get_utility(pos1,delta2)
            u_stay = g.get_utility(pos2, delta2)
            prob = log_linear_accept(u_stay,u_move,beta)
            if(random.random() < prob):
                g.swap_cells(pos1,pos2)
        elif (type2 == "vacant" and type1 != "vacant"):
            u_move = g.get_utility(pos2,delta1)
            u_stay = g.get_utility(pos1, delta1)
            prob = log_linear_accept(u_stay,u_move,beta)
            if(random.random() < prob):
                g.swap_cells(pos1,pos2)
        elif (type1 != "vacant" and type2 != "vacant"):
            # if none of the cells are vacant they can swap
            u_move_2 = g.get_utility(pos1,delta2)
            u_stay_2 = g.get_utility(pos2,delta2)
            u_move_1 = g.get_utility(pos2,delta1)
            u_stay_1 = g.get_utility(pos1,delta1)
            prob1 = log_linear_accept(u_stay_1,u_move_1,beta)
            prob2 = log_linear_accept(u_stay_2,u_move_2,beta)
            if (random.random() < prob1*prob2):
                g.swap_cells(pos1,pos2)

        for i in range(N):
            for j in range(N):
                cell = grid.grid[i][j]
                color = type_to_color[cell['type']]
                patches[i][j].set_facecolor(color)
                if show_delta:
                    delta_text[i][j].set_text(str(cell['delta']))
                else:
                    delta_text[i][j].set_text('')
        return sum(patches, []) + sum(delta_text, [])

    ani = animation.FuncAnimation(fig, update, frames=steps, interval=interval, blit=False)
    plt.show()

g = Grid(N=6, Y = 10, num_black=8, num_vacant=8, alpha=0.2)
animate_grid(g, steps=100, interval=200, beta=2.0, show_delta=True,)











