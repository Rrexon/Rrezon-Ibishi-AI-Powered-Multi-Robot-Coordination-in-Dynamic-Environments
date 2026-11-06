from astar import astar, get_neighbors


def action_toward(current, next_cell):
    row, col = current
    next_row, next_col = next_cell

    if abs(next_row - row) + abs(next_col - col) != 1:
        raise ValueError("next_cell must be adjacent to current")

    if next_row == row - 1:
        return 0

    if next_row == row + 1:
        return 1

    if next_col == col - 1:
        return 2

    return 3


def safe_neighbor(env, i, unsafe, avoid=()):
    """A free neighbour of robot i that no obstacle is about to hit.
    Cells in `avoid` are used only when nothing else is available."""
    blocked = env.blocked_for(i)
    options = [cell for cell in get_neighbors(env.robots[i], blocked, env.grid_size)
               if cell not in unsafe]
    preferred = [cell for cell in options if cell not in avoid]
    if preferred:
        return preferred[0]
    return options[0] if options else None


def plan_one(env, i, target, forecast):
    """Next cell for robot i and whether a route to the target exists.

    One-turn lookahead on the moving obstacles: they move before the robots do,
    so a cell is unsafe if an obstacle will be there after 1 move (the robot
    cannot enter) or after 2 moves (the robot would be hit next turn)."""
    position = env.robots[i]
    after_one, after_two = forecast
    unsafe = after_one | after_two
    blocked = env.blocked_for(i)

    if target is not None:
        path = astar(position, target, blocked, env.grid_size)
        if path is not None and len(path) > 1:
            if path[1] not in unsafe:
                return path[1], True
            # Take a different first step only if it costs nothing; a longer
            # detour is worse than waiting a turn (and makes robots dither).
            detour = astar(position, target, blocked | unsafe, env.grid_size)
            if detour is not None and 1 < len(detour) <= len(path):
                return detour[1], True
            routed = True              # route exists, just not safe right now
        else:
            routed = path is not None  # already on the target, or boxed in
    else:
        routed = True

    # Waiting is the default; step aside only if an obstacle is coming here.
    if position in after_two:
        aside = safe_neighbor(env, i, unsafe)
        if aside is not None:
            return aside, routed
    return position, routed


def plan_actions(env, targets):
    forecast = env.obstacle_forecast(2)
    unsafe = forecast[0] | forecast[1]
    count = len(env.robots)
    cells = []
    routed = []
    for i in range(count):
        cell, has_route = plan_one(env, i, targets[i], forecast)
        cells.append(cell)
        routed.append(has_route)

    # A working robot with no route at all may be boxed in by an idle robot.
    # Idle robots have nothing to protect, so one steps aside and the working
    # robot moves into the cell it frees in the same turn.
    yielding = set()
    for i in range(count):
        if targets[i] is None or routed[i]:
            continue
        ghost = astar(env.robots[i], targets[i], env.obstacles, env.grid_size)
        if ghost is None or len(ghost) < 2 or ghost[1] in unsafe:
            continue
        if ghost[1] not in env.robots:
            cells[i] = ghost[1]        # walk up to the blockage
            continue
        j = env.robots.index(ghost[1])
        if j in yielding:
            continue
        if targets[j] is not None:
            # A busy robot yields only when the blocked robot has precedence.
            if env.robot_priority(i) < env.robot_priority(j):
                continue
            if (env.robot_priority(i) == env.robot_priority(j)
                    and i > j):
                continue
        aside = safe_neighbor(env, j, unsafe | set(cells), avoid=set(ghost))
        if aside is None or (targets[j] is not None and aside in ghost):
            continue
        cells[j] = aside
        cells[i] = ghost[1]
        yielding.add(j)

    actions = []
    for i in range(count):
        if cells[i] == env.robots[i]:
            actions.append(4)
        else:
            actions.append(action_toward(env.robots[i], cells[i]))
    return actions
