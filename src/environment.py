ACTIONS = {
    0: (-1, 0),  # up
    1: (1, 0),   # down
    2: (0, -1),  # left
    3: (0, 1),   # right
}

class Environment:
    def __init__(self, grid_size, obstacles, robot_starts, task_locations):
        self.grid_size = grid_size
        self.obstacles = obstacles
        self.robot_starts = robot_starts
        self.task_locations = task_locations
        self.reset()

    def reset(self):
        self.robots = list(self.robot_starts)
        self.tasks = list(self.task_locations)

    def move_robot(self, i, action):
        d_row, d_col = ACTIONS[action]
        row, col = self.robots[i]
        new_pos = (row + d_row, col + d_col)
        if self.is_free(new_pos):
            self.robots[i] = new_pos

    def is_free(self, pos):
        row, col = pos
        inside = 0 <= row < self.grid_size and 0 <= col < self.grid_size
        return inside and pos not in self.obstacles

    def step(self, actions):
        for i, action in enumerate(actions):
            self.move_robot(i, action)