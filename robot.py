import queue
import numpy as np
import random
import mariadb
import sys
import re
import time


regex1 = re.compile(r'[1](?!])')
regex2 = re.compile(r'[0](?!])')
regex3 = re.compile(r'(]\n)')
# to keep track of the blocks of maze
class Grid_Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# each block will have its own position and cost of steps taken
class Node:
    def __init__(self, pos: Grid_Position, cost):
        self.pos = pos
        self.cost = cost

    def __lt__(self, other):
        if self.cost < other.cost:
            return True
        else:
            return False

def heuristic_value(curr_node,dest):
    return (abs(curr_node.x-dest.x)+abs(curr_node.y-dest.y))


def A_Star(maze, end, start):
    # Create lists for open nodes and closed nodes
    open1 = queue.PriorityQueue()
    closed = [[False for i in range(len(maze))]
                      for j in range(len(maze))]
    closed[start.x][start.y] = True

    #using these cell arrays to get neighbours
    adj_cell_x = [-1, 0, 0, 1]
    adj_cell_y = [0, -1, 1, 0]

    # Create a start node and an goal node
    Start = Node(start, 0)
    goal = Node(end, 0)

    # Add the start node
    open1.put((0, Start))
    cost = 0
    cells = 4

    # Create a dictionary to store the parent nodes
    parent = {}

    # Loop until the open list is empty
    while open1:
        # Get the node with the lowest cost
        current = open1.get()
        current_node = current[1]
        current_pos = current_node.pos

        # Add the current node to the closed list
        if current_node not in closed:
            closed[current_pos.x][current_pos.y] = True
            cost = cost + 1

        # Check if we have reached the goal, return the path
        if current_pos.x == end.x and current_pos.y == end.y:
            print("No. of moves utilized = ", cost)

            # Retrieve the path by backtracking from the goal node to the start node
            path = []
            while current_node != Start:
                path.append((current_node.pos.x, current_node.pos.y))
                current_node = parent[current_node]
            path.append((Start.pos.x, Start.pos.y))
            path.reverse()
            return path

        x_pos = current_pos.x
        y_pos = current_pos.y

        # Get neighbours
        for i in range(cells):
            if x_pos == len(maze) - 1 and adj_cell_x[i] == 1:
                x_pos = current_pos.x
                y_pos = current_pos.y + adj_cell_y[i]
                post = Grid_Position(x_pos, y_pos)
            if y_pos == 0 and adj_cell_y[i] == -1:
                x_pos = current_pos.x + adj_cell_x[i]
                y_pos = current_pos.y
                post = Grid_Position(x_pos, y_pos)
            else:
                x_pos = current_pos.x + adj_cell_x[i]
                y_pos = current_pos.y + adj_cell_y[i]
                post = Grid_Position(x_pos, y_pos)
            if x_pos < 20 and y_pos < 20 and x_pos >= 0 and y_pos >= 0:
                if maze[x_pos][y_pos] == 1:
                    if not closed[x_pos][y_pos]:
                        neighbor = Node(Grid_Position(x_pos, y_pos), current_node.cost + 1)
                        h = heuristic_value(neighbor.pos, end)
                        f = h + neighbor.cost
                        closed[x_pos][y_pos] = True
                        open1.put((f, neighbor))
                        parent[neighbor] = current_node

    return []

def getMaze():
    # Connect to MariaDB Platform
    try:
        conn1 = mariadb.connect(
            user="kr4kn",
            password="1",
            host="localhost",
            port=3306,
            database="autostore"

        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    # Get Cursor
    maze_cur = conn1.cursor()

    maze_cur.execute("SELECT * FROM maze")
    for (item) in maze_cur:
        maze = item[0]

    destList = []
    maze_cur.execute("SELECT destination FROM plans")
    for (item) in maze_cur:
        destList.append(eval(item[0]))

    startList = []
    maze_cur.execute("SELECT start_pos FROM plans")
    for (item) in maze_cur:
        startList.append(eval(item[0]))
    conn1.close()
    return maze, destList, startList

maze, destList, startList = getMaze()
maze = regex1.sub(r'1,', maze)
maze = regex2.sub(r'0,', maze)
maze = regex3.sub(r'],', maze)

maze = eval(maze)
maze = np.array(maze)

def solveAndUpdateDb(agent_id, dest, start, maze):

    destination = Grid_Position(dest[0], dest[1])
    starting_position = Grid_Position(start[0], start[1])
    path = 0

    print("Robot id: ", agent_id)
    print(f"Start position: ({starting_position.x}, {starting_position.y})")
    print(f"Goal position: ({destination.x}, {destination.y})")
    maze= maze.tolist()
    path = A_Star(maze, destination, starting_position)
    # path = path[::-1]
    print("Path: ", path)
    print("Path length: ", len(path))
    print("\n")

    
    # Connect to MariaDB Platform
    try:
        conn2 = mariadb.connect(
            user="kr4kn",
            password="1",
            host="localhost",
            port=3306,
            database="autostore"

        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    # Get Cursor
    plan_cur = conn2.cursor()

    # plan_cur.execute(f"INSERT INTO plans (start_pos, destination, plan) VALUES ('{start}', '{dest}', '{path}');")
    plan_cur.execute(f"UPDATE plans SET start_pos='{start}', plan='{path}' WHERE id={agent_id};")
    conn2.commit()
    conn2.close()

def send_plan_to_server():
            
    for k in range(0, 3):
        solveAndUpdateDb(k+1, destList[k], startList[k], maze)

def get_resolved_from_server():
    # Connect to MariaDB Platform
    try:
        conn3 = mariadb.connect(
            user="kr4kn",
            password="1",
            host="localhost",
            port=3306,
            database="autostore"

        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    # Get Cursor
    resolved_cur = conn3.cursor()
    resolved_cur.execute("SELECT plan FROM resolved")
    resolvedList = []
    for (item) in resolved_cur:
        resolvedList.append(eval(item[0]))
    return resolvedList


def main():
    send_plan_to_server()
    time.sleep(5)
    resolvedList = get_resolved_from_server()
    resolvedPlan1 = resolvedList[0]
    resolvedPlan2 = resolvedList[1]
    resolvedPlan3 = resolvedList[2]

    max_length = max(len(resolvedPlan1), len(resolvedPlan2), len(resolvedPlan3))

    # Connect to MariaDB Platform
    try:
        conn4 = mariadb.connect(
            user="kr4kn",
            password="1",
            host="localhost",
            port=3306,
            database="autostore"

        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    # Get Cursor
    position_cur = conn4.cursor()

    for step in range(0, max_length):
        position_cur.execute(f"UPDATE plans SET start_pos='{resolvedPlan1[-1]}' WHERE id=1;")
        position_cur.execute(f"UPDATE plans SET start_pos='{resolvedPlan2[-1]}' WHERE id=2;")
        position_cur.execute(f"UPDATE plans SET start_pos='{resolvedPlan3[-1]}' WHERE id=3;")
        print(f"================= Step {step} =================")
        try:
            position_cur.execute(f"UPDATE resolved SET current_pos='{resolvedPlan1[step]}' WHERE id=1;")
            print("Robot 1: ", resolvedPlan1[step])
        except Exception as e:
            # print(e)
            pass
        try:
            position_cur.execute(f"UPDATE resolved SET current_pos='{resolvedPlan2[step]}' WHERE id=2;")
            print("Robot 2: ", resolvedPlan2[step])
        except Exception as e:
            # print(e)
            pass
        try:
            position_cur.execute(f"UPDATE resolved SET current_pos='{resolvedPlan3[step]}' WHERE id=3;")
            print("Robot 3: ", resolvedPlan3[step])
        except Exception as e:
            # print(e)
            pass
        conn4.commit()
        time.sleep(1)

if __name__ == '__main__':
    main()
