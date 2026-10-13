from astar import astar

start = (5, 3)
goal = (12, 15)

obstacles = {
    (5, 8),
    (5, 9),
    (5, 10),
    (5, 11),
    (5, 12)
}

path = astar(start, goal, obstacles, 20)

print("Found path:", path)