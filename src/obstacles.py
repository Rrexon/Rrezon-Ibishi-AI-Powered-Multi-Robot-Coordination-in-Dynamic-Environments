def is_blocked(cell, grid_size, walls):
    row, col = cell
    if not (0 <= row < grid_size and 0 <= col < grid_size):
        return True
    return cell in walls


def move_obstacle(obstacle, grid_size, walls=()):
    position, direction = obstacle
    row, col = position
    d_row, d_col = direction

    if is_blocked((row + d_row, col + d_col), grid_size, walls):
        d_row = -d_row
        d_col = -d_col

    next_cell = (row + d_row, col + d_col)
    if is_blocked(next_cell, grid_size, walls):
        next_cell = position

    return (next_cell, (d_row, d_col))