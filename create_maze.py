import mazegen
import mariadb
import sys
import numpy as np
import random
import re

regex1 = re.compile(r'[1](?!])')
regex2 = re.compile(r'[0](?!])')
regex3 = re.compile(r'(]\n)')

# Connect to MariaDB Platform
try:
    conn = mariadb.connect(
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
cur = conn.cursor()

new_maze = str(input("Generate new maze? (y/n): ")).lower()

if new_maze == "y":
    maze = mazegen.generate_maze(20, 20, 0.1, 0.9)
    cur.execute(f"UPDATE maze SET maze='{maze}'")
    conn.commit()
else:
    pass

# maze_cur.execute(f"INSERT INTO maze (maze) VALUES ('{maze}')")
# cur.execute(f"UPDATE maze SET maze='{maze}'")
# conn.commit()
cur.execute("SELECT * FROM maze")
for (item) in cur:
    maze = item[0]

maze = regex1.sub(r'1,', maze)
maze = regex2.sub(r'0,', maze)
maze = regex3.sub(r'],', maze)

maze = eval(maze)
maze = np.array(maze)

#======================== DESTINATION =========================

def start_dest_generator(maze):

    empty_spaces = np.argwhere(maze == 1)
    start = random.choice(empty_spaces)
    dest = random.choice(empty_spaces)

    return start, dest

def generate_start_destList():
    destList = []
    startList = []
    for i in range(0, 3):
        start, dest = start_dest_generator(maze)
        destList.append(tuple(dest))  # Convert numpy array to tuple
        startList.append(tuple(start))
    
    # Check for duplicates in destList and startList
    non_duplicate = False
    while non_duplicate == False:
        non_duplicate = check_dups(destList, startList)
    return startList, destList

def check_dups(startList, destList):
    if len(destList) != len(set(destList)) or len(startList) != len(set(startList)):
        start, dest = start_dest_generator(maze)
        destList.append(tuple(dest))  # Convert numpy array to tuple
        startList.append(tuple(start))
    else:
        non_duplicate = True
    return non_duplicate

def find_empty_space():
    empty_spaces = np.argwhere(maze == 1)
    return empty_spaces

rand_start = str(input("Generate random starting positions? (y/n): ")).lower()
if rand_start == "y":
    for i in range(1,4):
        startList, _ = generate_start_destList()
        cur.execute(f"UPDATE plans SET start_pos='{tuple(startList[i-1])}' WHERE id={i};")
        conn.commit()
else:
    space = find_empty_space()
    print(space)
    print("Printed a list of valid start positions")
    try:
        start1 = eval(input("Enter destination for agent 1 as a tuple (x,y): "))
    except Exception as e:
        print(e)
    try:
        start2 = eval(input("Enter destination for agent 2 as a tuple (x,y): "))
    except Exception as e:
        print(e)
    try:
        start3 = eval(input("Enter destination for agent 3 as a tuple (x,y): "))
    except Exception as e:
        print(e)
    cur.execute(f"UPDATE plans SET start_pos='{start1}' WHERE id=1;")
    cur.execute(f"UPDATE plans SET start_pos='{start2}' WHERE id=2;")
    cur.execute(f"UPDATE plans SET start_pos='{start3}' WHERE id=3;")

    cur.execute(f"UPDATE resolved SET current_pos='{start1}' WHERE id=1;")
    cur.execute(f"UPDATE resolved SET current_pos='{start2}' WHERE id=2;")
    cur.execute(f"UPDATE resolved SET current_pos='{start3}' WHERE id=3;")
    conn.commit()

rand_dest = str(input("Generate random destinations? (y/n): ")).lower()
if rand_dest == "y":
    for i in range(1,4):
        _, destList = generate_start_destList()
        cur.execute(f"UPDATE plans SET destination='{tuple(destList[i-1])}' WHERE id={i};")
        conn.commit()
else:
    space = find_empty_space()
    print(space)
    print("Printed a list of valid destinations")
    try:
        dest1 = eval(input("Enter destination for agent 1 as a tuple (x,y): "))
    except Exception as e:
        print(e)
    try:
        dest2 = eval(input("Enter destination for agent 2 as a tuple (x,y): "))
    except Exception as e:
        print(e)
    try:
        dest3 = eval(input("Enter destination for agent 3 as a tuple (x,y): "))
    except Exception as e:
        print(e)
    cur.execute(f"UPDATE plans SET destination='{dest1}' WHERE id=1;")
    cur.execute(f"UPDATE plans SET destination='{dest2}' WHERE id=2;")
    cur.execute(f"UPDATE plans SET destination='{dest3}' WHERE id=3;")
    conn.commit()
