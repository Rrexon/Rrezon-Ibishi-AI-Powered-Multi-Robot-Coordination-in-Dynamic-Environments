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


def preempt_for_urgent_tasks(env):
    # Most urgent waiting tasks first
    for task in sorted(env.waiting_tasks(), key=env.priority_of, reverse=True):
        best_robot = None
        best_bid = float("inf")

        for i in range(len(env.robots)):
            current = env.assignments[i]

            # A free robot was already offered this task by the normal auction
            if current is None:
                continue

            # Only take a robot away from a LESS urgent task
            if env.priority_of(current) >= env.priority_of(task):
                continue

            b = bid(env, i, task)
            if b < best_bid:
                best_bid = b
                best_robot = i

        if best_robot is not None:
            # The robot's old task is no longer assigned, so it is waiting again
            env.assignments[best_robot] = task


def assign_waiting_tasks(env):
    waiting = env.waiting_tasks()
    waiting = sorted(waiting, key=env.priority_of, reverse=True)
    for task in waiting:
        assign_task(env, task)

    preempt_for_urgent_tasks(env)