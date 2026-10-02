import pygame

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

running = True

while running:
    # Check for window and user events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

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

# Shut down Pygame
pygame.quit()