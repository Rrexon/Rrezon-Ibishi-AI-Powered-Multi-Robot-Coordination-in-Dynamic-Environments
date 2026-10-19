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


# Test a wall with an opening in the middle
middle_obstacles = {
    (8, col) for col in range(20)
    if col != 10
}

middle_path = astar(start, goal, middle_obstacles, 20)

assert middle_path is not None, "A* should find a path"
assert middle_path[0] == start, "Path should begin at the start"
assert middle_path[-1] == goal, "Path should end at the goal"
assert (8, 10) in middle_path, "Path should pass through the gap"
assert len(middle_path) == 20, "Path should contain 20 positions"

assert all(cell not in middle_obstacles for cell in middle_path), \
    "Path should not cross obstacles"

for current, following in zip(middle_path, middle_path[1:]):
    distance = (
        abs(current[0] - following[0])
        + abs(current[1] - following[1])
    )
    assert distance == 1, "Each move must go to an adjacent cell"

print("Middle-gap test passed!")
print("Found path:", middle_path)

# Test a wall with no opening
blocked_obstacles = {
    (8, col) for col in range(20)
}

blocked_path = astar(start, goal, blocked_obstacles, 20)

assert blocked_path is None, "A* should not find a path"

print("Unreachable-goal test passed!")