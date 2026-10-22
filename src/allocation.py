from astar import astar


def bid(env, robot_index, task):
    path = astar(env.robots[robot_index], task, env.obstacles, env.grid_size)

    if path is None:
        return float("inf")

    return len(path) - 1
     