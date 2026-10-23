
def move_obstacle(obstacle, grid_size):
    position, direction = obstacle
    row, col = position
    d_row, d_col = direction

    next_row = row + d_row
    next_col = col + d_col

    if not (0 <= next_row < grid_size and 0 <= next_col < grid_size):
        d_row = -d_row
        d_col = -d_col
        next_row = row + d_row
        next_col = col + d_col

    return ((next_row, next_col), (d_row, d_col))