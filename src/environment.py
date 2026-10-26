from obstacles import move_obstacle
import random 

ACTIONS = {
    0: (-1, 0),  # up
    1: (1, 0),   # down
    2: (0, -1),  # left
    3: (0, 1),   # right
    4: (0, 0),   # stay
}

class Environment:
    def __init__(self, grid_size, obstacles, robot_starts, task_locations, moving_obstacles=None, new_tasks=None, priorities = None, seed= None, task_rate=0.0, random_obstacles=0):
        self.grid_size = grid_size
        self.walls = set(obstacles)
        self.robot_starts = robot_starts
        if len(set(robot_starts)) != len(robot_starts):
            raise ValueError("Two robots start on the same cell")
        self.task_locations = task_locations
        self.initial_moving = moving_obstacles or []
        self.task_schedule = new_tasks or {}
        self.initial_priorities = priorities or {}
        self.task_rate = task_rate
        self.random_obstacles = random_obstacles
        self.rng = random.Random(seed)
        for task in list(task_locations) + list(self.task_schedule.values()):
            row, col = task
            if not (0 <= row < grid_size and 0 <= col < grid_size):
                raise ValueError("A task is outside the grid")
            if task in self.walls:
                raise ValueError("A task is placed on a wall")
        self.reset()

    def reset(self, seed=None):
        if seed is not None:
            self.rng = random.Random(seed)
        self.robots = list(self.robot_starts)
        self.tasks = list(self.task_locations)
        self.completed = 0
        self.collisions = 0
        self.collisions_avoided = 0
        self.assignments = [None] * len(self.robots)
        self.moving_obstacles = list(self.initial_moving)
        self.obstacles = set(self.walls)
        for position, direction in self.moving_obstacles:
            self.obstacles.add(position)
        self.spawn_random_obstacles()
        self.obstacle_hits = 0
        self.turn = 0
        self.previous_conflicts = set()
        self.priorities = dict(self.initial_priorities)
        self.task_arrival = {task: 0 for task in self.tasks}
        self.completion_times = []
        self.busy_turns = 0
        self.moving_turns = 0

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
            new_list.append(move_obstacle(obstacle, self.grid_size, self.walls))
        self.moving_obstacles = new_list

        self.obstacles = set(self.walls)
        for position, direction in self.moving_obstacles:
            self.obstacles.add(position)

        for pos in self.robots:
            if pos in self.obstacles:
                self.obstacle_hits += 1

    def free_cells(self):
        taken = set(self.obstacles) | set(self.robots) | set(self.tasks)
        cells = []
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if (row, col) not in taken:
                    cells.append((row, col))
        return cells

    def spawn_random_obstacles(self):
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for _ in range(self.random_obstacles):
            cells = self.free_cells()
            if not cells:
                return
            cell = self.rng.choice(cells)
            direction = self.rng.choice(directions)
            self.moving_obstacles.append((cell, direction))
            self.obstacles.add(cell)

    def maybe_spawn_task(self):
        if self.rng.random() >= self.task_rate:
            return
        cells = self.free_cells()
        if not cells:
            return
        cell = self.rng.choice(cells)
        priority = self.rng.choices([1, 2, 3], weights=[70, 20, 10])[0]
        self.tasks.append(cell)
        self.task_arrival[cell] = self.turn
        self.priorities[cell] = priority

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

        assigned_before = [task is not None for task in self.assignments]
        positions_before = list(self.robots)

        self.update_obstacles()
        self.turn += 1
        if self.turn in self.task_schedule:
            new_task = self.task_schedule[self.turn]
            self.tasks.append(new_task)
            self.task_arrival[new_task] = self.turn

        self.maybe_spawn_task()

        desired = self.desired_positions(actions)
        desired = self.resolve_conflicts(desired)
        self.robots = desired

        for a in range(len(self.robots)):
            for b in range(a + 1, len(self.robots)):
                if self.robots[a] == self.robots[b]:
                    self.collisions += 1

        for pos in self.robots:
            if pos in self.tasks:
                self.tasks.remove(pos)
                self.completed += 1
                arrived = self.task_arrival.pop(pos, self.turn)
                self.completion_times.append(self.turn - arrived)
                for j in range(len(self.assignments)):
                    if self.assignments[j] == pos:
                        self.assignments[j] = None

        for i in range(len(self.robots)):
            if assigned_before[i]:
                self.busy_turns += 1
                if self.robots[i] != positions_before[i]:
                    self.moving_turns += 1

    def metrics(self):
        times = self.completion_times
        return {
            "tasks_completed": self.completed,
            "avg_completion_time": sum(times) / len(times) if times else None,
            "slowest_task": max(times) if times else None,
            "collisions_avoided": self.collisions_avoided,
            "obstacle_hits": self.obstacle_hits,
            "efficiency": self.moving_turns / self.busy_turns if self.busy_turns else None,
            "tasks_per_turn": self.completed / self.turn if self.turn else None,
        }