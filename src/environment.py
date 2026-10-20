ACTIONS = {
    0: (-1, 0),  # up
    1: (1, 0),   # down
    2: (0, -1),  # left
    3: (0, 1),   # right
    4: (0, 0),   # stay
}

class Environment:
    def __init__(self, grid_size, obstacles, robot_starts, task_locations):
        self.grid_size = grid_size
        self.obstacles = obstacles
        self.robot_starts = robot_starts
        self.task_locations = task_locations
        self.collisions_avoided = 0
        self.reset()

    def reset(self):
        self.robots = list(self.robot_starts)
        self.tasks = list(self.task_locations)
        self.completed = 0
        self.collision = 0

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

    def desired_position(self, i, action):
        d_row, d_col = ACTIONS[action]
        row, col = self.robots[i]
        new_pos = (row + d_row, col + d_col)
        if self.is_free(new_pos):
            return new_pos
        return (row, col)

    def desired_positions(self, actions):
        desired = []
        for i, action in enumerate(actions):
            desired.append(self.desired_position(i, action))
        return desired

    def find_conflicts(self, desired):
        conflicts = []
        for a in range(len(desired)):
            for b in range(a + 1, len(desired)):
                if desired[a] == desired[b]:
                    conflicts.append((a, b))
        return conflicts

    def resolve_conflicts(self, desired):
        for a, b in self.find_conflicts(desired):
            desired[b] = self.robots[b]
            self.collisions_avoided += 1
        return desired
    
    def step(self, actions):
        desired = self.desired_positions(actions)
        desired = self.resolve_conflicts(desired)
        self.robots = desired

        for pos in self.robots:
            if pos in self.tasks:
                self.tasks.remove(pos)
                self.completed += 1