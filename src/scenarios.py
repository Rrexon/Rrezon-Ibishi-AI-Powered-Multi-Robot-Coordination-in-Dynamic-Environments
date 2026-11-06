"""Shared scenario definitions, so main.py, evaluate.py and baseline.py
all run exactly the same world."""

import random

from environment import Environment

GRID_SIZE = 20
WALLS = {(5, 8), (5, 9), (5, 10)}
ROBOT_STARTS = [(0, 0), (19, 0), (19, 19)]
TASKS = [(12, 5), (3, 14)]
MOVING_OBSTACLES = [((10, 0), (0, 1)), ((2, 17), (1, 0))]
NEW_TASKS = {10: (15, 15), 20: (4, 4)}
PRIORITIES = {(15, 15): 3, (4, 4): 2}


def make_main_scenario(seed=None, random_obstacles=0, task_rate=0.0):
    """The project's main scenario. With the defaults it is fully
    deterministic; seed / random_obstacles / task_rate add seeded randomness."""
    return Environment(
        GRID_SIZE, set(WALLS), list(ROBOT_STARTS), list(TASKS),
        list(MOVING_OBSTACLES), dict(NEW_TASKS), dict(PRIORITIES),
        seed=seed, task_rate=task_rate, random_obstacles=random_obstacles,
    )


# ---------------------------------------------------------------------------
# Random worlds: a different map, robot starts, tasks and obstacles every seed.
# ---------------------------------------------------------------------------

DIRECTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)]


def _neighbors(cell, size):
    row, col = cell
    for d_row, d_col in DIRECTIONS:
        r, c = row + d_row, col + d_col
        if 0 <= r < size and 0 <= c < size:
            yield (r, c)


def free_space_is_connected(walls, size):
    """True if every non-wall cell can reach every other one."""
    free = [(r, c) for r in range(size) for c in range(size) if (r, c) not in walls]
    if not free:
        return False
    seen = {free[0]}
    stack = [free[0]]
    while stack:
        for nxt in _neighbors(stack.pop(), size):
            if nxt not in walls and nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return len(seen) == len(free)


def random_walls(rng, size, segments, max_length=5):
    """Short straight wall segments. A segment is kept only if the free
    cells stay connected, so no robot or task is ever sealed in."""
    walls = set()
    for _ in range(segments):
        for _attempt in range(40):
            length = rng.randint(2, max_length)
            row, col = rng.randrange(size), rng.randrange(size)
            horizontal = rng.random() < 0.5
            cells = {(row, col + k) if horizontal else (row + k, col)
                     for k in range(length)}
            if any(not (0 <= r < size and 0 <= c < size) for r, c in cells):
                continue
            candidate = walls | cells
            if free_space_is_connected(candidate, size):
                walls = candidate
                break
    return walls


def make_random_scenario(seed=None, grid_size=20, n_robots=3, n_tasks=3,
                         n_walls=8, n_moving=4, task_rate=0.08,
                         random_starts=True):
    """A random world. The same seed always gives the same world.

    n_walls      number of random wall segments
    n_moving     moving obstacles at the start
    task_rate    chance per turn that a new task appears (random cell, random priority)
    random_starts  False puts the robots in the corners as in the main scenario
    """
    if seed is None:
        seed = random.randrange(10 ** 6)
    counts = (n_robots, n_tasks, n_walls, n_moving)
    if not isinstance(grid_size, int) or grid_size < 1:
        raise ValueError("grid_size must be a positive integer")
    if any(not isinstance(count, int) or count < 0 for count in counts):
        raise ValueError("robot, task, wall, and obstacle counts must be non-negative integers")
    if not 0 <= task_rate <= 1:
        raise ValueError("task_rate must be between 0 and 1")

    rng = random.Random(seed)
    size = grid_size

    walls = random_walls(rng, size, n_walls)
    free = [(r, c) for r in range(size) for c in range(size) if (r, c) not in walls]
    if n_robots + n_tasks > len(free):
        raise ValueError("Not enough free cells for the requested robots and tasks")

    if random_starts:
        robot_starts = rng.sample(free, n_robots)
    else:
        corners = [(0, 0), (size - 1, 0), (size - 1, size - 1), (0, size - 1)]
        robot_starts = [c for c in corners if c not in walls][:n_robots]
        if len(robot_starts) < n_robots:
            robot_starts += rng.sample([c for c in free if c not in robot_starts],
                                       n_robots - len(robot_starts))

    taken = set(robot_starts)
    tasks = rng.sample([c for c in free if c not in taken], n_tasks)
    priorities = {task: rng.choices([1, 2, 3], weights=[70, 20, 10])[0] for task in tasks}
    taken |= set(tasks)

    # Obstacles start a little away from the robots so nobody is hit on turn 1.
    def near_robot(cell):
        return any(abs(cell[0] - r) + abs(cell[1] - c) <= 2 for r, c in robot_starts)

    spots = [c for c in free if c not in taken and not near_robot(c)]
    if n_moving > len(spots):
        raise ValueError("Not enough free cells for the requested moving obstacles")
    moving = [(cell, rng.choice(DIRECTIONS)) for cell in rng.sample(spots, n_moving)]

    env = Environment(size, walls, robot_starts, tasks, moving, None, priorities,
                      seed=rng.randrange(2 ** 31), task_rate=task_rate)
    env.scenario_seed = seed
    return env
