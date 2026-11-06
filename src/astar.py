"""A* pathfinding for the four-direction grid."""

import heapq


def heuristic(position, goal):
    """Manhattan distance: the exact distance when there are no obstacles."""
    return abs(position[0] - goal[0]) + abs(position[1] - goal[1])


def get_neighbors(position, obstacles, grid_size):
    """Return unblocked neighbors in up, down, left, right order."""
    row, col = position
    candidates = ((row - 1, col), (row + 1, col),
                  (row, col - 1), (row, col + 1))
    return [cell for cell in candidates
            if 0 <= cell[0] < grid_size and 0 <= cell[1] < grid_size
            and cell not in obstacles]


def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return list(reversed(path))


def astar(start, goal, obstacles, grid_size):
    """Return the shortest path (including start and goal), or None."""
    frontier = [(heuristic(start, goal), start)]
    came_from = {}
    distance = {start: 0}
    visited = set()

    while frontier:
        _, current = heapq.heappop(frontier)
        if current in visited:
            continue
        if current == goal:
            return reconstruct_path(came_from, current)
        visited.add(current)

        for neighbor in get_neighbors(current, obstacles, grid_size):
            new_distance = distance[current] + 1
            if neighbor in distance and new_distance >= distance[neighbor]:
                continue
            came_from[neighbor] = current
            distance[neighbor] = new_distance
            score = new_distance + heuristic(neighbor, goal)
            heapq.heappush(frontier, (score, neighbor))

    return None


def distances_from(start, obstacles, grid_size):
    """Return shortest distances from start to every reachable cell."""
    frontier = [(0, start)]
    distances = {start: 0}

    while frontier:
        distance, current = heapq.heappop(frontier)
        if distance != distances[current]:
            continue
        for neighbor in get_neighbors(current, obstacles, grid_size):
            new_distance = distance + 1
            if new_distance >= distances.get(neighbor, float("inf")):
                continue
            distances[neighbor] = new_distance
            heapq.heappush(frontier, (new_distance, neighbor))

    return distances
