import pygame

from environment import Environment
from astar import astar
from navigation import action_toward

CELL_SIZE = 30
GRID_SIZE = 20

obstacles = {(5, 8), (5, 9), (5, 10), (5, 11), (5, 12)}
env = Environment(GRID_SIZE, obstacles, [(5, 3)], [(12, 15)])

path = astar(env.robots[0], env.tasks[0], env.obstacles, env.grid_size)
path_index = 0

pygame.init()
screen = pygame.display.set_mode((CELL_SIZE * GRID_SIZE, CELL_SIZE * GRID_SIZE))
pygame.display.set_caption("Multi-Robot Coordination")
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #  the robot takes the next step along its A* path
    if path_index < len(path) - 1:
        path_index += 1
        action = action_toward(env.robots[0], path[path_index])
        env.step([action])

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
    clock.tick(5)

pygame.quit()