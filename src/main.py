import pygame

from environment import Environment
from navigation import plan_actions

CELL_SIZE = 30
GRID_SIZE = 20

obstacles = {(3, 12), (3, 13), (3, 14)}
targets = [(10, 15), (4, 9)]
env = Environment(GRID_SIZE, obstacles, [(10, 3), (16, 9)], list(targets))

pygame.init()
screen = pygame.display.set_mode((CELL_SIZE * GRID_SIZE, CELL_SIZE * GRID_SIZE))
pygame.display.set_caption("Multi-Robot Coordination")
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #  every robot plans from where it is now, then all move
    env.step(plan_actions(env, targets))

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
    clock.tick(3)

pygame.quit()