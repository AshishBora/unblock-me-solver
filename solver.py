# pylint: disable = C0103, C0111, C0301, R0913, R0903, R0914

import copy
import collections
import time
import matplotlib.pyplot as plt
import numpy as np

# from sklearn.cluster import KMeans
# import numpy as np


def read_image():
    image = plt.imread('./screencap.png')
    image = image[:, :, :3]
    # plt.imshow(im)
    return image


def get_type(color):
    # X = colors
    # kmeans = KMeans(n_clusters=3, random_state=0).fit(colors)
    # kmeans.cluster_centers_

    empty = [0.41390375, 0.28627452, 0.11515152]
    block = [0.89002558, 0.48661553, 0.0054561]
    red = [0.88627452, 0.0, 0.0]
    return np.argmin([np.linalg.norm(color - centre) for centre in [empty, block, red]])


def is_wall(line):
    grad = line[1:] - line[:-1]
    grad_norms = np.sum(grad**2, axis=1)
    return max(grad_norms) > 0.01
    # plt.figure()
    # plt.plot(grad_norms)
    # print grad_norms.shape
    # print np.linalg.norm(grad, ord='fro')


def get_string_rep(grid, wall_grid_x, wall_grid_y):
    string = [['' for _ in range(6)] for _ in range(6)]
    vert_counter = 0
    horiz_counter = 0

    for j in range(6):
        for i in range(6):

            if string[j][i]:
                continue

            if grid[j][i] == 0:
                string[j][i] = 'e'
            elif grid[j][i] == 2:
                string[j][i] = 'r'

            elif wall_grid_x[j][i]:
                string[j][i] = 'v{}'.format(vert_counter)
                j_temp = j+1
                while not wall_grid_y[j_temp-1][i]:
                    string[j_temp][i] = string[j][i]
                    j_temp += 1
                vert_counter += 1
            else:
                string[j][i] = 'h{}'.format(horiz_counter)
                i_temp = i+1
                while not wall_grid_x[j][i_temp-1]:
                    string[j][i_temp] = string[j][i]
                    i_temp += 1
                horiz_counter += 1

    return string


def pprint(string):
    for row in string:
        for elem in row:
            print '{:4}'.format(elem),
        print ''
    print ''


def get_moves(node):
    moves = []
    for j in range(6):
        for i in range(6):
            if node[j][i] == 'e':
#                 print j, i
                directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

                dir_map = {
                    (0, 1): ['h', 'r'],
                    (0, -1): ['h', 'r'],
                    (1, 0): 'v',
                    (-1, 0): 'v',
                }

                for dy, dx in directions:
                    y, x = j, i

                    while True:
                        y, x = y + dy, x + dx

                        cond1 = (0 <= x < 6) and (0 <= y < 6)
                        if not cond1:
                            break

                        if node[y][x] != 'e':
#                             print '    ', y, x
                            if node[y][x][0] in dir_map[(dy, dx)]:
                                move = (j, i, (j-y, i-x))
                                moves.append(move)
                            break

                # for (y, x) in neighbors:
                #     direc = (j-y, i-x)
                #     if node[y][x][0] in dir_map[direc]:
                #         move = (j, i, direc)
                #         moves.append(move)

    return moves


def apply_move(old_node, move):
    node = copy.deepcopy(old_node)

    j, i, direc = move
    dy, dx = direc

    label = node[j-dy][i-dx]

    j = j - dy
    i = i - dx
    while (0 <= j < 6) and (0 <= i < 6) and (node[j][i] == label):
        node[j][i] = 'e'
        node[j+dy][i+dx] = label
        j = j - dy / abs(dy + dx)
        i = i - dx / abs(dy + dx)

    return node


def get_neighbors(node):
    moves = get_moves(node)
    neighbors = [apply_move(node, move) for move in moves]
    return neighbors, moves


def check_solved(node):
    solved = (node[2][4] == 'r') and (node[2][5] == 'r')
    return solved


class HashError(Exception):
    pass

def hashed(node):
    try:
        return ''.join([' '.join(row) for row in node])
    except:
        raise HashError


class BFSError(Exception):
    pass


def bfs(start):
    start_time = time.time()
    timeout = 60 # seconds
    # print 'Starting BFS...',

    back_pointer = {}
    visited = {}
    queue = collections.deque([start])
    visited[hashed(start)] = True

    while len(queue) > 0:
        if time.time() - start_time > timeout:
            print 'Could not find a path in {} seconds... terminating'.format(timeout)
            break

        node = queue.popleft()
        neighbors, moves = get_neighbors(node)
        for neighbor, move in zip(neighbors, moves):
            if check_solved(neighbor):
                back_pointer[hashed(neighbor)] = node, move
                # bfs_time = time.time() - start_time
                # print 'Solved in {} seconds'.format(bfs_time)
                return back_pointer, neighbor

            if hashed(neighbor) in visited:
                continue
            else:
                queue.append(neighbor)
                visited[hashed(neighbor)] = True
                back_pointer[hashed(neighbor)] = node, move

    if len(queue) == 0:
        print 'BFS terminated but could not find a path'
        raise BFSError

    return False, None


def get_path(back_pointer, start, final):
    path = [(final, None)]
    while path[-1][0] != start:
        prev_node, _ = path[-1]
        node, move = back_pointer[hashed(prev_node)]
        path.append((node, move))
    return list(reversed(path))


def get_swipes(path):
    swipes = []
    for _, move in path:
        x, y, direc = move
        dx, dy = direc
        x1, y1 = x - dx, y - dy
        x2, y2 = x, y
        swipe = (x1, y1, x2, y2)
        swipes.append(swipe)
    return swipes


def get_grid(image, X_vals, Y_vals):
    grid = [[None for _ in range(6)] for _ in range(6)]
    for i, y in enumerate(Y_vals):
        for j, x in enumerate(X_vals):
            color = image[y, x, :]
            grid[i][j] = get_type(color)
    return grid


def get_wall_grids(image, X_vals, Y_vals):
    wall_grid_x = [[True for i in range(6)] for j in range(6)]
    for j in range(6):
        for i in range(5):
            line = image[Y_vals[j], X_vals[i]:X_vals[i+1], :]
            wall_grid_x[j][i] = is_wall(line)

    wall_grid_y = [[True for i in range(6)] for j in range(6)]
    for j in range(5):
        for i in range(6):
            line = image[Y_vals[j]:Y_vals[j+1], X_vals[i], :]
            wall_grid_y[j][i] = is_wall(line)

    return wall_grid_x, wall_grid_y


def validate_grid(grid):
    num_red = sum([float(elem==2) for row in grid for elem in row])
    return num_red == 2


def get_start_config():
    image = read_image()
    X_vals = [127, 294, 461, 628, 795, 962]
    Y_vals = [633, 800, 967, 1134, 1301, 1468]

    grid = get_grid(image, X_vals, Y_vals)
    if not validate_grid(grid):
        return None

    wall_grid_x, wall_grid_y = get_wall_grids(image, X_vals, Y_vals)
    start = get_string_rep(grid, wall_grid_x, wall_grid_y)

    # print 'Current board configuration:'
    # pprint(start)
    # neighbors = get_neighbors(start)
    # for neighbor in neighbors:
    #     pprint(neighbor)
    #     print ''

    return start



def solve(start):
    back_pointer, final = bfs(start)
    path = get_path(back_pointer, start, final)
    swipes = get_swipes(path[:-1])
    swipes.append((2, 4, 2, 5))
    return swipes
