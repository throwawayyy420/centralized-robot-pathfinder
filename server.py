import numpy as np
import random
import mariadb
import sys
import re
import time

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
plan_cur = conn1.cursor()

plan_cur.execute("SELECT plan FROM plans")
planList = []
for (item) in plan_cur:
    planList.append(eval(item[0]))
plan_cur.execute("SELECT start_pos FROM plans")
startList = []
for (item) in plan_cur:
    startList.append(eval(item[0]))
plan_cur.execute("SELECT destination FROM plans")
destList = []
for (item) in plan_cur:
    destList.append(eval(item[0]))

conn1.close()

plan1 = planList[0]
plan2 = planList[1]
plan3 = planList[2]
max_length = max(len(plan1), len(plan2), len(plan3))
min_length = min(len(plan1), len(plan2), len(plan3))

# resolve step conflicts
for t in range(0, max_length):
    try:
        if plan1[t] == plan2[t]:
            if len(plan1) <= len(plan2):
                plan1.insert(t, plan1[t])  # insert the same step (wait at that step)
            else:
                plan2.insert(t, plan2[t])
    except: pass
    try:
        if plan1[t+1] == plan2[t] or plan1[t] == plan2[t+1]:
            if len(plan1) <= len(plan2):
                plan1.insert(t, plan1[t-1]) # step back
            else:
                plan2.insert(t, plan2[t-1])
    except: pass
    try:
        if plan1[t] == plan3[t]:
            if len(plan1) <= len(plan3):
                plan1.insert(t, plan1[t])
            else:
                plan3.insert(t, plan3[t])
    except: pass
    try:
        if plan1[t+1] == plan3[t] or plan1[t] == plan3[t+1]:
            if len(plan1) <= len(plan3):
                plan1.insert(t, plan1[t-1])
            else:
                plan3.insert(t, plan3[t-1])
    except: pass
    try:
        if plan2[t] == plan3[t]:
            if len(plan2) <= len(plan3):
                plan2.insert(t, plan2[t])
            else:
                plan3.insert(t, plan3[t])
    except: pass
    try:
        if plan2[t+1] == plan3[t] or plan2[t] == plan3[t+1]:
            if len(plan2) <= len(plan3):
                plan2.insert(t, plan2[t-1])
            else:
                plan3.insert(t, plan3[t-1])
    except: pass

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


max_length_resolved = max(len(plan1), len(plan2), len(plan3))
min_length_resolved = min(len(plan1), len(plan2), len(plan3))

while len(plan1) < max_length_resolved:
    plan1.append(plan1[-1])
while len(plan2) < max_length_resolved:
    plan2.append(plan2[-1])
while len(plan3) < max_length_resolved:
    plan3.append(plan3[-1])

# Get Cursor
resolved_cur = conn2.cursor()
resolved_cur.execute(f"UPDATE resolved SET plan='{plan1}' WHERE id=1;")
resolved_cur.execute(f"UPDATE resolved SET plan='{plan2}' WHERE id=2;")
resolved_cur.execute(f"UPDATE resolved SET plan='{plan3}' WHERE id=3;")
conn2.commit()


print(f"Agent 1: \nStart position: {startList[0]} \nDestination: {destList[0] }\n")
print(f"Agent 2: \nStart position: {startList[1]} \nDestination: {destList[1]}\n")
print(f"Agent 3: \nStart position: {startList[2]} \nDestination: {destList[2]}\n")

for step in range(0, max_length_resolved):
    try:
        print(f"step {step}:", end=" ")
        print(f"agent1: {plan1[step]}", end=" ")

    except: pass
    try:
        print(f"agent2: {plan2[step]}", end=" ")
    except: pass
    try:
        print(f"agent3: {plan3[step]}", end=" ")
    except: pass
    print()

def main():
    # try:
    #     while True:
    #         pass
    # except KeyboardInterrupt:
    #     print("Keyboard interrupt received. Exiting.")
    #     sys.exit(0)
    pass


if __name__ == '__main__':
    main()