from astar import astar

# start = (5, 3)
# goal = (12, 15)

# obstacles = {
#     (5, 8),
#     (5, 9),
#     (5, 10),
#     (5, 11),
#     (5, 12)
# }
start = (5, 3)
goal = (12, 15)

obstacles = {(8, col) for col in range(19)}

path = astar(start, goal, obstacles, 20)

assert path is not None, "A* should find a path"
assert path[0] == start, "Path should begin at the start"
assert path[-1] == goal, "Path should end at the goal"
assert len(path) == 28, "Path should contain 28 positions"
assert all(cell not in obstacles for cell in path), \
    "Path should not cross obstacles"

for current, following in zip(path, path[1:]):
    distance = (
        abs(current[0] - following[0])
        + abs(current[1] - following[1])
    )
    assert distance == 1, "Each move must go to an adjacent cell"

print("All path checks passed!")

print("Found path:", path)