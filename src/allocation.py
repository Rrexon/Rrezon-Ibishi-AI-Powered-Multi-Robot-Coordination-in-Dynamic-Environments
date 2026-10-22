from astar import astar


def bid(env, robot_index, task):
    path = astar(env.robots[robot_index], task, env.obstacles, env.grid_size)

    if path is None:
        return float("inf")

    return len(path) - 1

def run_auction(env, task):
    best_robot = None
    best_bid = float("inf")

    for i in range(len(env.robots)):
        b = bid(env, i, task)
        if b < best_bid:
            best_bid = b
            best_robot = i

    return best_robot