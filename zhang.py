from enum import Enum
from itertools import product
import random
import math
import pygame

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
        print(num_vacant)
        if num_vacant < 0:
            raise ValueError("There are no vacant cells!")
        
        # create cell types
        vacancies = ["vacant"]*num_vacant
        l = [[i]*colors[i] for i in colors.keys()]
        cells = [x for sublist in l for x in sublist]
        cells.extend(vacancies)
        

        random.shuffle(cells)
        count = 0
        for i in cells:
            if i == "orange":
                count += 1
        print(count)

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
    def get_utility(self,cell_type,pos2):
        deltas = self.get_deltas_for_type(cell_type)
        neigh = self.get_neighborhood(pos2,neigh_type="moore")
        utility = 0
        for (i,j) in neigh:
            if self.grid[i][j] == "vacant":
                continue
            utility += deltas[self.color_dict[self.grid[i][j]]]
        return utility
    
    def improving_move_then_swap(self):
        u_move = 0
        u_stay = 0
        flag = False
        candidates = []
        for i in range(N):
            for j in range(N):
                for k in range(i,N):
                    for l in range(j+1, N):
                        cell_type_1 = self.grid[i][j]
                        cell_type_2 = self.grid[k][l]


                        if (cell_type_1 == "vacant" and cell_type_2 == "vacant"):
                            continue
                        elif (cell_type_1 != "vacant" and cell_type_2 == "vacant"):
                            u_move = self.get_utility(cell_type_1, (k,l))
                            u_stay = self.get_utility(cell_type_1, (i,j))
                        elif (cell_type_1 == "vacant" and cell_type_2 != "vacant"):
                            u_move = self.get_utility(cell_type_2, (i,j))
                            u_stay = self.get_utility(cell_type_2, (k,l))
                        if (u_move > u_stay):
                            candidates.append((u_move-u_stay, u_stay, u_move, (i, j), (k, l)))
                        if(cell_type_1 != "vacant" and cell_type_2 != "vacant"):
                            u_move_1 = self.get_utility(cell_type_1, (k,l))
                            u_stay_1 = self.get_utility(cell_type_1, (i,j))
                            u_move_2 = self.get_utility(cell_type_2, (i,j))
                            u_stay_2 = self.get_utility(cell_type_2, (k,l))
                            if(u_move_1 > u_stay_1 and u_move_2 > u_stay_2):
                                candidates.append((u_move_1-u_stay_1,u_stay_1, u_move_1, (i, j), (k, l)))
        if candidates:
            candidates.sort(reverse=True, key=lambda x: x[0])
            delta_u, u_old, u_new, (from_x, from_y), (to_x, to_y) = candidates[0]
            print(f"Move from ({from_x}, {from_y}) to ({to_x}, {to_y}) | Previous Utility: {u_old:.2f}, New Utility: {u_new:.2f}, Change: {delta_u:.2f}")
            self.swap_cells( (to_x,to_y), (from_x,from_y) )
            flag = True
        return flag

    def next_step(self):
       return self.improving_move_then_swap()


    
    def get_type(self,pos):
        pos_x, pos_y = pos
        return self.grid[pos_x][pos_y]


    

                                            # fixed income
N = 25                                      # N x N grid size

#sets the number of cells having each color
colors = {"white":200, "black":200, "orange":50}
l = list(colors.keys())

# defines a color->index coreespondence
color_dict = {c:l.index(c) for c in l}

#p_ij matrix, 
p = [[1,1,1], [1,1,-1], [1,-1,2]]

FPS = 30

CELL_SIZE = 20
WIDTH = HEIGHT = N * CELL_SIZE



#def log_linear_accept(u1,u2, beta=1.0):
    # Compute acceptance probability for swapping
   # prob = math.exp(beta * u2) / (math.exp(beta * u1) + math.exp(beta * u2))
   # return prob

def draw_grid(screen, grid):
    for i in range(N):
        for j in range(N):
            if grid[i][j] == "vacant":
                color = pygame.color.THECOLORS["gray"]
            else:
                color = pygame.color.THECOLORS[grid[i][j]]
            pygame.draw.rect(screen,color , (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, (100, 100, 100), (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Zhang's Segregation Model")
    clock = pygame.time.Clock()

    g = Grid(N=N,p=p,color_dict=color_dict,colors=colors)
    running = True

    while running:
        screen.fill((0, 0, 0))
        draw_grid(screen, g.grid)
        pygame.display.flip()
        clock.tick(FPS)
        running = g.next_step()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()

if __name__ == '__main__':
    main()













