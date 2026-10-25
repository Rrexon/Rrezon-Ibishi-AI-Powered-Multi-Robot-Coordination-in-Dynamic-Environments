import heapq

def heuristic(position, goal):

    row, col = position
    goal_row, goal_col = goal

    return abs(row- goal_row) + abs(col - goal_col)

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
    # Cells waiting to be explored, kept so the lowest f_score is always first
    open_heap = [(heuristic(start, goal), start)]

    came_from = {}
    g_score = {start: 0}

    # Cells already explored
    closed = set()

    while open_heap:
        # Take the cell with the lowest f_score
        _, current = heapq.heappop(open_heap)

        # A cell can be pushed more than once; skip it if already explored
        if current in closed:
            continue

        if current == goal:
            return reconstruct_path(came_from, current)

        closed.add(current)

        for neighbor in get_neighbors(current, obstacles, grid_size):
            tentative_g_score = g_score[current] + 1

            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(open_heap, (f_score, neighbor))

    return None

    