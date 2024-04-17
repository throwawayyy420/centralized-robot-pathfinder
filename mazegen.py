# only used as module, do not run directly

import numpy as np
import random

def generate_maze(rows, cols, wall_prob=0.1, space_prob=0.9):
    maze = np.zeros((rows, cols), dtype=int)
    for i in range(rows):
        for j in range(cols):
            maze[i][j] = random.choices([0, 1], weights=[wall_prob, space_prob])[0]

    return maze

def main():
    maze = generate_maze(20, 20)
    print(maze)

if __name__ == '__main__':
    main()