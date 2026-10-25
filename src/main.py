import pygame

from environment import Environment
from allocation import assign_waiting_tasks
from navigation import plan_actions

CELL_SIZE = 30
GRID_SIZE = 20

walls = {(5, 8), (5, 9), (5, 10)}
robot_starts = [(0, 0), (19, 0), (19, 19)]
tasks = [(12, 5), (3, 14)]
moving = [((10, 0), (0, 1)), ((2, 17), (1, 0))]
new_tasks = {10: (15, 15), 20: (4, 4)}
priorities = {(15, 15): 3, (4, 4): 2}

env = Environment(GRID_SIZE, walls, robot_starts, tasks, moving, new_tasks, priorities)

pygame.init()
screen = pygame.display.set_mode((CELL_SIZE * GRID_SIZE, CELL_SIZE * GRID_SIZE))
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # One turn: free robots win tasks, then everyone plans and moves
    assign_waiting_tasks(env)
    env.step(plan_actions(env, env.assignments))

    pygame.display.set_caption(
        f"Turn {env.turn}  Done {env.completed}  "
        f"Avoided {env.collisions_avoided}  Hits {env.obstacle_hits}"
    )

    screen.fill((240, 240, 240))

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            pygame.draw.rect(screen, (180, 180, 180),
                             (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

    for row, col in env.obstacles:
        pygame.draw.rect(screen, (50, 50, 50),
                         (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    for row, col in env.tasks:
        pygame.draw.rect(screen, (60, 180, 80),
                         (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    for row, col in env.robots:
        pygame.draw.rect(screen, (50, 100, 200),
                         (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    pygame.display.flip()
    clock.tick(2)

pygame.quit()