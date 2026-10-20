
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

