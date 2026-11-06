from astar import astar, distances_from


def bid(env, robot_index, task, distance_maps=None, stats=None):
    if distance_maps is not None:
        if robot_index not in distance_maps:
            distance_maps[robot_index] = distances_from(
                env.robots[robot_index], env.blocked_for(robot_index), env.grid_size
            )
            if stats is not None:
                stats["distance_maps"] = stats.get("distance_maps", 0) + 1
        return distance_maps[robot_index].get(task, float("inf"))

    if stats is not None:
        stats["astar_bids"] = stats.get("astar_bids", 0) + 1
    path = astar(env.robots[robot_index], task, env.blocked_for(robot_index), env.grid_size)

    if path is None:
        return float("inf")

    return len(path) - 1


def run_auction(env, task, distance_maps=None, stats=None):
    best_robot = None
    best_bid = float("inf")

    for i in range(len(env.robots)):
        if env.assignments[i] is not None:
            continue
        b = bid(env, i, task, distance_maps, stats)
        if b < best_bid:
            best_bid = b
            best_robot = i

    return best_robot


def assign_task(env, task, distance_maps=None, stats=None):
    winner = run_auction(env, task, distance_maps, stats)
    if winner is not None:
        env.assignments[winner] = task
    return winner


def preempt_for_urgent_tasks(env, distance_maps=None, stats=None):
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

            b = bid(env, i, task, distance_maps, stats)
            if b < best_bid:
                best_bid = b
                best_robot = i

        if best_robot is not None:
            # The robot's old task is no longer assigned, so it is waiting again
            env.assignments[best_robot] = task


def assign_waiting_tasks(env, method="astar", stats=None):
    if method not in {"astar", "distance_map"}:
        raise ValueError("method must be 'astar' or 'distance_map'")
    distance_maps = {} if method == "distance_map" else None
    waiting = env.waiting_tasks()
    waiting = sorted(waiting, key=env.priority_of, reverse=True)
    for task in waiting:
        assign_task(env, task, distance_maps, stats)

    preempt_for_urgent_tasks(env, distance_maps, stats)
