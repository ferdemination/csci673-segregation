from enum import Enum
from itertools import product
import random
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Simulating Zhang's model of segregation https://wordpress.clarku.edu/wp-content/uploads/sites/423/2016/03/segregation.pdf


        

class Grid:
    def __init__(self, N,p,color_dict,colors):
        self.N = N
        self.grid = [[None for _ in range(N)] for _ in range(N)]
        self.p = p
        self.color_dict = color_dict
        self.colors = colors

        total_cells = N * N
        num_vacant = total_cells - sum(colors.values())

        if num_vacant < 0:
            raise ValueError("There are no vacant cells!")
        
        # create cell types
        vacancies = ["vacant"]*num_vacant
        l = [[i]*colors[i] for i in colors.keys()]
        cells = [x for sublist in l for x in sublist]
        cells.extend(vacancies)

        random.shuffle(cells)

        # Assign types and deltas
        idx = 0
        for i in range(N):
            for j in range(N):
                cell_type = cells[idx]
                self.grid[i][j] = cell_type
                idx += 1

    def get_deltas_for_type(self, cell_type):
        if cell_type == "vacant":
            return [0 for _ in range(len(self.colors))]
        return self.p[self.color_dict[cell_type]]

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
    def get_utility(self, pos1,pos2):
        pos_x, pos_y = pos1 
        cell_type = self.grid[pos_x][pos_y]    
        deltas = self.get_deltas_for_type(cell_type)

        neigh = self.get_neighborhood(pos2,neigh_type="moore")
        utility = 0
        for (i,j) in neigh:
            if self.grid[i][j] == "vacant":
                continue
            utility += deltas[self.color_dict[self.grid[i][j]]]
        return utility
    
    def next_step(self):
        for i in range(self.N):
            for j in range(self.N):

                if (self.grid[i][j] == "vacant"):
                    u_move = self.get_utility((i,i), (i,j))
                    u_stay = self.get_utility((i,i), (i,i))
                    if (u_move > u_stay):
                        self.swap_cells((i,i),(i,j))
                elif (self.grid[i][i] == "vacant"):
                    u_move = self.get_utility((i,j), (i,i))
                    u_stay = self.get_utility((i,j), (i,j))
                    if (u_move > u_stay):
                        self.swap_cells((i,i), (i,j))
                else:
                    u_move_1 = self.get_utility((i,i), (i,j))
                    u_stay_1 = self.get_utility((i,i), (i,i))
                    u_move_2 = self.get_utility((i,j), (i,i))
                    u_stay_2 = self.get_utility((i,j), (i,j))
                    if(u_move_1 > u_stay_1 and u_move_2 > u_stay_2):
                        self.swap_cells((i,i),(i,j))
    
    def get_type(self,pos):
        pos_x, pos_y = pos
        return self.grid[pos_x][pos_y]


    

                                            # fixed income
N = 30                                      # N x N grid size

#sets the number of cells having each color
colors = {"white":100, "black":100, "orange":50, "blue":50}
l = list(colors.keys())

# defines a color->index coreespondence
color_dict = {c:l.index(c) for c in l}

#p_ij matrix, 
p = [[1,1,1,1], [1,1,1,1], [1,1,1,1], [1,1,1,1]]

#def log_linear_accept(u1,u2, beta=1.0):
    # Compute acceptance probability for swapping
   # prob = math.exp(beta * u2) / (math.exp(beta * u1) + math.exp(beta * u2))
   # return prob

def animate_grid(g, steps=100, interval=300):
    N = g.N

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
        g.next_step()
        for i in range(N):
            for j in range(N):
                cell = g.grid[i][j]
                if (cell == "vacant"):
                    color = "gray"
                else:
                    color = cell
                patches[i][j].set_facecolor(color)
        return sum(patches, []) + sum(delta_text, [])

    ani = animation.FuncAnimation(fig, update, frames=steps, interval=interval, blit=False)
    plt.show()

g = Grid(N=N,p=p,color_dict=color_dict,colors=colors)
animate_grid(g, steps=100, interval=200)











