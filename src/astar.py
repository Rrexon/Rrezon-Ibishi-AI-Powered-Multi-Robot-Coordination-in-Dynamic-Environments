
def heuristic(position, goal):

    row, col = position
    goal_row, goal_col = goal

    return abs(row- goal_row) + (col - goal_col)

# Find neighbor available cells it can move to
def get_neighbors(position, obstacles, grid_size):
    row, col = position

    possible_neighbors = [
        (row - 1, col),  # Up
        (row + 1, col),  # Down
        (row, col - 1),  # Left
        (row, col + 1)   # Right
    ]

    neighbors = []

    for next_row, next_col in possible_neighbors:
        # Skip positions outside the grid
        if not (0 <= next_row < grid_size):
            continue

        if not (0 <= next_col < grid_size):
            continue

        # Skip blocked positions
        if (next_row, next_col) in obstacles:
            continue

        neighbors.append((next_row, next_col))

    return neighbors

#traces back from the target to the start to reconstruct the path
def reconstruct_path(came_from, current):
    path = [current]

    while current in came_from:
        current = came_from[current]
        path.append(current)

    path.reverse()
    return path


def astar(start, goal, obstacles, grid_size):
    # Cells waiting to be explored
    open_set = {start}

    # Records where each cell came from
    came_from = {}

    # Cost from the start to each cell
    g_score = {start: 0}

    # Estimated total cost through each cell
    f_score = {start: heuristic(start, goal)}

        # Search until there are no cells left to explore
    while open_set:
        current = None

        # Find the cell with the lowest f_score
        for position in open_set:
            if current is None or f_score[position] < f_score[current]:
                current = position

        # Remove the selected cell from the cells waiting to be explored
        open_set.remove(current)

        # Check whether the target has been reached
        # this statement returns the path
        if current == goal:
            return reconstruct_path(came_from, current)

        # Check each valid neighboring cell
        for neighbor in get_neighbors(current, obstacles, grid_size):
            # Calculate the cost of reaching this neighbor
            tentative_g_score = g_score[current] + 1

               # Check whether this is a new or cheaper route
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                open_set.add(neighbor)

    return None

    