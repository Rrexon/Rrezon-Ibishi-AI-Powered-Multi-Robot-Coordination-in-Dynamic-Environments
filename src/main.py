import pygame

from astar import astar

# Initialize Pygame
pygame.init()

# Size of each grid cell in pixels
CELL_SIZE = 30

# Number of rows and columns in the grid
GRID_SIZE = 20

# Calculate the window size
WINDOW_SIZE = CELL_SIZE * GRID_SIZE

# Create the simulation window
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Multi-Robot Coordination")

# Initial robot position in grid coordinates
robot_row = 5
robot_col = 3

target_row = 12
target_col = 15

obstacles = {
    (5, 8),
    (5, 9),
    (5, 10),
    (5, 11),
    (5, 12)
}

# Calculate a path from the robot's start to the target
start = (robot_row, robot_col)
goal = (target_row, target_col)

path = astar(start, goal, obstacles, GRID_SIZE)

path_index = 0

print("Path from A*:", path)

running = True
clock = pygame.time.Clock()
while running:
    # Check for window and user events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Follow the path returned by A*
    if path is not None and path_index < len(path) - 1:
        path_index += 1
        robot_row, robot_col = path[path_index]

    # Set the background color
    screen.fill((240, 240, 240))

    # Draw the grid
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = col * CELL_SIZE
            y = row * CELL_SIZE

            pygame.draw.rect(
                screen,
                (180, 180, 180),
                (x, y, CELL_SIZE, CELL_SIZE),
                1
            )

    for row , col in obstacles:
        y = row * CELL_SIZE
        x = col * CELL_SIZE

        pygame.draw.rect(screen, (50 ,50, 50), (x,y,CELL_SIZE,CELL_SIZE))

    # Convert the robot's grid position to screen coordinates
    robot_x = robot_col * CELL_SIZE
    robot_y = robot_row * CELL_SIZE

    # Draw the robot
    pygame.draw.rect(
        screen,
        (50, 100, 200),
        (robot_x, robot_y, CELL_SIZE, CELL_SIZE)
    )

    # Update the display
    pygame.display.flip()
    clock.tick(5)

# Shut down Pygame
pygame.quit()