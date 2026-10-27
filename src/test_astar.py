from astar import astar

START = (5, 3)
GOAL = (12, 15)


def test_wall_with_open_end():
    obstacles = {(8, col) for col in range(19)}

    path = astar(START, GOAL, obstacles, 20)

    assert path is not None, "A* should find a path"
    assert path[0] == START, "Path should begin at the start"
    assert path[-1] == GOAL, "Path should end at the goal"
    assert len(path) == 28, "Path should contain 28 positions"
    assert all(cell not in obstacles for cell in path), \
        "Path should not cross obstacles"

    for current, following in zip(path, path[1:]):
        distance = (
            abs(current[0] - following[0])
            + abs(current[1] - following[1])
        )
        assert distance == 1, "Each move must go to an adjacent cell"


def test_wall_with_gap_in_middle():
    middle_obstacles = {
        (8, col) for col in range(20)
        if col != 10
    }

    middle_path = astar(START, GOAL, middle_obstacles, 20)

    assert middle_path is not None, "A* should find a path"
    assert middle_path[0] == START, "Path should begin at the start"
    assert middle_path[-1] == GOAL, "Path should end at the goal"
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


def test_wall_with_no_opening_is_unreachable():
    blocked_obstacles = {(8, col) for col in range(20)}

    blocked_path = astar(START, GOAL, blocked_obstacles, 20)

    assert blocked_path is None, "A* should not find a path"