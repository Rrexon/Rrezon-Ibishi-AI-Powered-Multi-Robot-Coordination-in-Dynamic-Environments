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
font = pygame.font.SysFont(None, 22)
clock = pygame.time.Clock()


def draw_cell(cell, color):
    row, col = cell
    pygame.draw.rect(screen, color,
                     (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))


def draw_label(cell, text):
    row, col = cell
    image = font.render(str(text), True, (255, 255, 255))
    x = col * CELL_SIZE + (CELL_SIZE - image.get_width()) // 2
    y = row * CELL_SIZE + (CELL_SIZE - image.get_height()) // 2
    screen.blit(image, (x, y))


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

    # Fixed walls: dark grey
    for cell in env.walls:
        draw_cell(cell, (50, 50, 50))

    # Moving obstacles: orange
    for cell, direction in env.moving_obstacles:
        draw_cell(cell, (230, 120, 30))

    # Tasks: green, with the priority number on top
    for cell in env.tasks:
        draw_cell(cell, (60, 180, 80))
        draw_label(cell, env.priority_of(cell))

    # Robots: blue, with the robot number on top
    for i, cell in enumerate(env.robots):
        draw_cell(cell, (50, 100, 200))
        draw_label(cell, i)

    pygame.display.flip()
    clock.tick(3)

pygame.quit()