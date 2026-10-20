from astar import astar

def action_toward(current, next_cell):
    row, col = current
    next_row, next_col = next_cell

    if next_row == row - 1:
        return 0 

    if next_row == row + 1:
        return 1

    if next_col == col - 1:
        return 2

    if next_col == col + 1:
        return 3

def plan_actions(env, targets):
    actions = []
    for i in range(len(env.robots)):
        path = astar(env.robots[i], targets[i], env.obstacles, env.grid_size)
        if path is not None and len(path) > 1:
            actions.append(action_toward(env.robots[i], path[1]))
        else:
            actions.append(4)
    return actions

