from astar import astar


def bid(env, robot_index, task):
    path = astar(env.robots[robot_index], task, env.blocked_for(robot_index), env.grid_size)

    if path is None:
        return float("inf")

    return len(path) - 1

def run_auction(env, task):
    best_robot = None
    best_bid = float("inf")

    for i in range(len(env.robots)):
        if env.assignments[i] is not None:
            continue
        b = bid(env, i, task)
        if b < best_bid:
            best_bid = b
            best_robot = i

    return best_robot

def assign_task(env, task):
    winner = run_auction(env, task)
    if winner is not None:
        env.assignments[winner] = task
    return winner

def assign_waiting_tasks(env):
    waiting = env.waiting_tasks()
    waiting = sorted(waiting, key=env.priority_of, reverse=True)
    for task in waiting:
        assign_task(env, task)