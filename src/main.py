"""Run the interactive multi-robot simulation viewer."""

import argparse
import random

from allocation import assign_waiting_tasks
from navigation import plan_actions
from scenarios import make_main_scenario, make_random_scenario


def parse_args():
    parser = argparse.ArgumentParser(description="Multi-robot coordination viewer")
    parser.add_argument("--seed", type=int, help="replay a specific world")
    parser.add_argument("--fixed", action="store_true", help="use the fixed demo world")
    parser.add_argument("--size", type=int, default=20, help="random-world grid size")
    parser.add_argument("--robots", type=int, default=3)
    parser.add_argument("--tasks", type=int, default=3, help="starting task count")
    parser.add_argument("--walls", type=int, default=8, help="random wall segments")
    parser.add_argument("--obstacles", type=int, help="moving obstacles")
    parser.add_argument("--task-rate", type=float, help="chance of a task per turn")
    parser.add_argument("--corners", action="store_true", help="start robots near corners")
    parser.add_argument("--fps", type=int, default=3, help="simulation turns per second")
    return parser.parse_args()


def make_environment(args, seed):
    """Choose the requested world and apply mode-specific defaults."""
    if args.fixed:
        obstacles = 0 if args.obstacles is None else args.obstacles
        task_rate = 0.0 if args.task_rate is None else args.task_rate
        return make_main_scenario(seed, obstacles, task_rate)

    obstacles = 4 if args.obstacles is None else args.obstacles
    task_rate = 0.08 if args.task_rate is None else args.task_rate
    return make_random_scenario(
        seed=seed,
        grid_size=args.size,
        n_robots=args.robots,
        n_tasks=args.tasks,
        n_walls=args.walls,
        n_moving=obstacles,
        task_rate=task_rate,
        random_starts=not args.corners,
    )


def draw_cell(pygame, screen, cell_size, cell, color):
    row, col = cell
    pygame.draw.rect(screen, color,
                     (col * cell_size, row * cell_size, cell_size, cell_size))


def draw_label(pygame, screen, font, cell_size, cell, text):
    row, col = cell
    image = font.render(str(text), True, (255, 255, 255))
    x = col * cell_size + (cell_size - image.get_width()) // 2
    y = row * cell_size + (cell_size - image.get_height()) // 2
    screen.blit(image, (x, y))


def main():
    args = parse_args()
    import pygame  # Keep --help usable when pygame is not installed.

    seed = args.seed if args.seed is not None else random.randrange(10 ** 6)
    env = make_environment(args, seed)
    print(f"World seed: {seed} (replay with --seed {seed})")

    pygame.init()
    cell_size = max(12, min(30, 600 // env.grid_size))
    screen = pygame.display.set_mode((cell_size * env.grid_size,) * 2)
    font = pygame.font.SysFont(None, max(14, cell_size - 8))
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                seed = random.randrange(10 ** 6)
                env = make_environment(args, seed)
                print("New world seed:", seed)

        assign_waiting_tasks(env)
        env.step(plan_actions(env, env.assignments))
        pygame.display.set_caption(
            f"Seed {seed}  Turn {env.turn}  Done {env.completed}  "
            f"Avoided {env.collisions_avoided}  Hits {env.obstacle_hits}  [R = new world]"
        )

        screen.fill((240, 240, 240))
        for row in range(env.grid_size):
            for col in range(env.grid_size):
                pygame.draw.rect(screen, (180, 180, 180),
                                 (col * cell_size, row * cell_size,
                                  cell_size, cell_size), 1)

        for cell in env.walls:
            draw_cell(pygame, screen, cell_size, cell, (50, 50, 50))
        for cell, _ in env.moving_obstacles:
            draw_cell(pygame, screen, cell_size, cell, (230, 120, 30))
        for cell in env.tasks:
            draw_cell(pygame, screen, cell_size, cell, (60, 180, 80))
            draw_label(pygame, screen, font, cell_size, cell, env.priority_of(cell))
        for robot_id, cell in enumerate(env.robots):
            draw_cell(pygame, screen, cell_size, cell, (50, 100, 200))
            draw_label(pygame, screen, font, cell_size, cell, robot_id)

        pygame.display.flip()
        clock.tick(args.fps)

    pygame.quit()


if __name__ == "__main__":
    main()
