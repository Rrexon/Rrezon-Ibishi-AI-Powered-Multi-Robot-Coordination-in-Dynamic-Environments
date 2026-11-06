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
    def __init__(self, grid_size, obstacles, robot_starts, task_locations,
                 moving_obstacles=None, new_tasks=None, priorities=None,
                 seed=None, task_rate=0.0, random_obstacles=0):
        if not isinstance(grid_size, int) or grid_size < 1:
            raise ValueError("grid_size must be a positive integer")
        if not 0 <= task_rate <= 1:
            raise ValueError("task_rate must be between 0 and 1")
        if not isinstance(random_obstacles, int) or random_obstacles < 0:
            raise ValueError("random_obstacles must be a non-negative integer")

        self.grid_size = grid_size
        self.walls = set(obstacles)
        self.robot_starts = list(robot_starts)
        if len(set(robot_starts)) != len(robot_starts):
            raise ValueError("Two robots start on the same cell")
        self.task_locations = list(task_locations)
        if len(set(self.task_locations)) != len(self.task_locations):
            raise ValueError("Two initial tasks cannot occupy the same cell")
        self.initial_moving = list(moving_obstacles or [])
        positions = [position for position, _ in self.initial_moving]
        if len(set(positions)) != len(positions):
            raise ValueError("Moving obstacles cannot start on the same cell")
        valid_directions = {(0, 1), (0, -1), (1, 0), (-1, 0)}
        if any(direction not in valid_directions
               for _, direction in self.initial_moving):
            raise ValueError("Moving obstacle directions must be one cell cardinal moves")
        self.task_schedule = dict(new_tasks or {})
        self.initial_priorities = dict(priorities or {})
        self.task_rate = task_rate
        self.random_obstacles = random_obstacles
        self.rng = random.Random(seed)
        for start in self.robot_starts:
            row, col = start
            if not (0 <= row < grid_size and 0 <= col < grid_size):
                raise ValueError("A robot starts outside the grid")
            if start in self.walls:
                raise ValueError("A robot starts on a wall")
        for position, direction in self.initial_moving:
            row, col = position
            if not (0 <= row < grid_size and 0 <= col < grid_size):
                raise ValueError("A moving obstacle starts outside the grid")
            if position in self.walls:
                raise ValueError("A moving obstacle starts on a wall")
            if position in self.robot_starts:
                raise ValueError("A moving obstacle starts on a robot")
        for turn in self.task_schedule:
            if turn < 1:
                raise ValueError("Scheduled tasks appear from turn 1 onward")
        all_tasks = self.task_locations + list(self.task_schedule.values())
        for task in all_tasks:
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
        self.turn = 0
        self.spawn_random_obstacles()
        self.obstacle_hits = 0
        self.previous_conflicts = set()
        self.priorities = dict(self.initial_priorities)
        self.task_arrival = {task: 0 for task in self.tasks}
        self.completion_times = []
        self.busy_turns = 0
        self.moving_turns = 0

    def check_action(self, action):
        if action not in ACTIONS:
            raise ValueError(f"Unknown action {action!r}; use 0-4")

    def move_robot(self, i, action):
        self.check_action(action)
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
        self.moving_obstacles = [
            move_obstacle(obstacle, self.grid_size, self.walls)
            for obstacle in self.moving_obstacles
        ]
        self.obstacles = self.walls | {position for position, _ in self.moving_obstacles}
        self.obstacle_hits += sum(pos in self.obstacles for pos in self.robots)

    def obstacle_forecast(self, steps=2):
        """Where the moving obstacles will be after 1, 2, ... `steps` moves.
        Their motion is deterministic, so this is exact. Returns a list of sets."""
        moving = list(self.moving_obstacles)
        forecast = []
        for _ in range(steps):
            moving = [move_obstacle(o, self.grid_size, self.walls) for o in moving]
            forecast.append({position for position, direction in moving})
        return forecast

    def reserved_cells(self):
        """Cells where a scheduled task has not appeared yet."""
        return {cell for turn, cell in self.task_schedule.items() if turn > self.turn}

    def free_cells(self):
        taken = (set(self.obstacles) | set(self.robots) | set(self.tasks)
                 | self.reserved_cells())
        return [(row, col)
                for row in range(self.grid_size)
                for col in range(self.grid_size)
                if (row, col) not in taken]

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
        return [task for task in self.tasks if task not in self.assignments]

    def blocked_for(self, i):
        blocked = set(self.obstacles)
        for j, pos in enumerate(self.robots):
            if j != i:
                blocked.add(pos)
        return blocked

    def priority_of(self, task):
        return self.priorities.get(task, 1)

    def desired_position(self, i, action):
        self.check_action(action)
        d_row, d_col = ACTIONS[action]
        row, col = self.robots[i]
        new_pos = (row + d_row, col + d_col)
        if self.is_free(new_pos):
            return new_pos
        return (row, col)

    def desired_positions(self, actions):
        return [self.desired_position(i, action) for i, action in enumerate(actions)]

    def find_conflicts(self, desired):
        conflicts = []
        for a in range(len(desired)):
            for b in range(a + 1, len(desired)):
                if desired[a] == desired[b]:
                    conflicts.append((a, b))
                elif desired[a] == self.robots[b] and desired[b] == self.robots[a]:
                    conflicts.append((a, b))
        return conflicts

    def robot_priority(self, i):
        task = self.assignments[i]
        return 0 if task is None else self.priority_of(task)

    def resolve_conflicts(self, desired):
        conflicts = self.find_conflicts(desired)
        seen = set()

        while conflicts:
            a, b = conflicts[0]
            seen.add((a, b))

            if desired[b] == self.robots[b]:
                loser = a          # b is standing still and keeps its cell
            elif desired[a] == self.robots[a]:
                loser = b          # a is standing still and keeps its cell
            elif self.robot_priority(b) > self.robot_priority(a):
                loser = a          # the more urgent task goes first
            else:
                loser = b          # equal priority: lower robot number wins

            desired[loser] = self.robots[loser]
            conflicts = self.find_conflicts(desired)

        self.collisions_avoided += len(seen - self.previous_conflicts)
        self.previous_conflicts = seen
        return desired
    
    def step(self, actions):
        if len(actions) != len(self.robots):
            raise ValueError("Need exactly one action per robot")
        for action in actions:
            self.check_action(action)  # before anything changes

        assigned_before = [task is not None for task in self.assignments]
        positions_before = list(self.robots)

        self.update_obstacles()
        self.turn += 1
        if self.turn in self.task_schedule:
            new_task = self.task_schedule[self.turn]
            if new_task not in self.tasks:   # one task per cell
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
                self.priorities.pop(pos, None)
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
        """Return run metrics; collisions_avoided counts resolved robot conflicts."""
        times = self.completion_times
        return {
            "tasks_completed": self.completed,
            "avg_completion_time": sum(times) / len(times) if times else None,
            "slowest_task": max(times) if times else None,
            "collisions_avoided": self.collisions_avoided,
            "obstacle_hits": self.obstacle_hits,
            "efficiency": self.moving_turns / self.busy_turns if self.busy_turns else None,
            "tasks_per_turn": self.completed / self.turn if self.turn else None,
            "tasks_unfinished": len(self.tasks),
            "completion_rate": (self.completed / (self.completed + len(self.tasks))
                                if self.completed + len(self.tasks) else None),
            "oldest_open_task": (max(self.turn - self.task_arrival[t] for t in self.tasks)
                                 if self.tasks else None),
        }
