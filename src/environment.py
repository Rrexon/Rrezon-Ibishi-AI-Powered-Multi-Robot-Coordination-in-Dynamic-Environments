from obsctacles import move_obstacle

ACTIONS = {
    0: (-1, 0),  # up
    1: (1, 0),   # down
    2: (0, -1),  # left
    3: (0, 1),   # right
    4: (0, 0),   # stay
}

class Environment:
    def __init__(self, grid_size, obstacles, robot_starts, task_locations, moving_obstacles=None, new_tasks=None, priorities = None):
        self.grid_size = grid_size
        self.walls = set(obstacles)
        self.robot_starts = robot_starts
        if len(set(robot_starts)) != len(robot_starts):
            raise ValueError("Two robots start on the same cell")
        self.task_locations = task_locations
        self.initial_moving = moving_obstacles or []
        self.task_schedule = new_tasks or {}
        self.priorities = priorities or {}
        self.reset()

    def reset(self):
        self.robots = list(self.robot_starts)
        self.tasks = list(self.task_locations)
        self.completed = 0
        self.collisions = 0
        self.collisions_avoided = 0
        self.obstacle_hits = 0
        self.turn = 0
        self.previous_conflicts = set()
        self.assignments = [None] * len(self.robots)
        self.moving_obstacles = list(self.initial_moving)
        self.obstacles = set(self.walls)
        for position, direction in self.moving_obstacles:
            self.obstacles.add(position)

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

    def update_obstacles(self):
        new_list = []
        for obstacle in self.moving_obstacles:
            new_list.append(move_obstacle(obstacle, self.grid_size))
        self.moving_obstacles = new_list

        self.obstacles = set(self.walls)
        for position, direction in self.moving_obstacles:
            self.obstacles.add(position)

        for pos in self.robots:
            if pos in self.obstacles:
                self.obstacle_hits += 1

    def waiting_tasks(self):
        waiting = []
        for task in self.tasks:
            if task not in self.assignments:
                waiting.append(task)
        return waiting

    def blocked_for(self, i):
        blocked = set(self.obstacles)
        for j, pos in enumerate(self.robots):
            if j != i:
                blocked.add(pos)
        return blocked

    def priority_of(self, task):
        return self.priorities.get(task, 1)

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
                elif desired[a] == self.robots[b] and desired[b] == self.robots[a]:
                    conflicts.append((a, b))
        return conflicts

    def resolve_conflicts(self, desired):
        conflicts = self.find_conflicts(desired)
        seen = set()

        while conflicts:
            a, b = conflicts[0]
            seen.add((a, b))

            if desired[b] == self.robots[b]:
                loser = a
            else:
                loser = b

            desired[loser] = self.robots[loser]
            conflicts = self.find_conflicts(desired)

        self.collisions_avoided += len(seen - self.previous_conflicts)
        self.previous_conflicts = seen
        return desired
    
    def step(self, actions):
        if len(actions) != len(self.robots):
            raise ValueError("Need exactly one action per robot")
        self.update_obstacles()
        self.turn += 1
        if self.turn in self.task_schedule:
            self.tasks.append(self.task_schedule[self.turn])
        desired = self.desired_positions(actions)
        desired = self.resolve_conflicts(desired)
        self.robots = desired

        for i, pos in enumerate(self.robots):
            if pos in self.tasks:
                self.tasks.remove(pos)
                self.completed += 1
                for j in range(len(self.assignments)):
                    if self.assignments[j] == pos:
                        self.assignments[j] = None