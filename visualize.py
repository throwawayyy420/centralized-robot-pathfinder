import numpy as np
import mariadb
import sys
import re
import time
import os


clear = lambda: os.system('clear') #on Linux System

regex1 = re.compile(r'[1](?!])')
regex2 = re.compile(r'[0](?!])')
regex3 = re.compile(r'(]\n)')
regex4 = re.compile(r'(^\[)')
regex5 = re.compile(r'(?<=\])\]')

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
    cursor = conn1.cursor()

    cursor.execute("SELECT * FROM maze")
    for (item) in cursor:
        maze = item[0]

    destList = []
    cursor.execute("SELECT destination FROM plans")
    for (item) in cursor:
        destList.append(eval(item[0]))
    cursor.execute("SELECT start_pos FROM plans")
    startList = []
    for (item) in cursor:
        startList.append(eval(item[0]))
    cursor.execute("SELECT current_pos FROM resolved")
    posList = []
    for (item) in cursor:
        posList.append(eval(item[0]))
    conn1.close()
    return maze, destList, startList, posList



def main():
    try:
        while True:
            maze, destList, startList, posList = getMaze()
            # maze_visual = maze
            maze = regex1.sub(r'1,', maze)
            maze = regex2.sub(r'0,', maze)
            maze = regex3.sub(r'],', maze)

            maze = eval(maze)
            maze = np.array(maze)

            for elem in destList:
                maze[elem[0]][elem[1]] = str('3')
            for elem in startList:
                maze[elem[0]][elem[1]] = str('4')
            for elem in posList:
                maze[elem[0]][elem[1]] = str('5')

            maze_visual = str(maze)
            maze_visual = maze_visual.replace(" ", "")
            maze_visual = regex4.sub(r'', maze_visual)
            maze_visual = regex5.sub(r'', maze_visual)
            maze_visual = regex5.sub(r'', maze_visual)
            maze_visual = maze_visual.replace("1", "  ")
            maze_visual = maze_visual.replace("0", "██")
            maze_visual = maze_visual.replace("[", "██")
            maze_visual = maze_visual.replace("]", "██")
            maze_visual = maze_visual.replace("3", "SP")  # starting position
            maze_visual = maze_visual.replace("4", "DT")  # destination
            maze_visual = maze_visual.replace("5", "RB")  # robot
            maze_visual = "████████████████████████████████████████████\n" + maze_visual + "\n████████████████████████████████████████████" # add edge walls
            print(maze_visual)
            time.sleep(0.5)
            clear()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()