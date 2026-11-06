"""Interactive viewer for the multi-robot coordination simulation."""

import argparse
import random

from allocation import assign_waiting_tasks
from navigation import plan_actions
from scenarios import make_main_scenario, make_random_scenario

COLORS = {
    "background": (19, 25, 36),
    "panel": (29, 38, 52),
    "panel_light": (39, 51, 68),
    "grid": (57, 70, 88),
    "floor": (232, 238, 244),
    "wall": (63, 73, 88),
    "obstacle": (238, 137, 56),
    "task": (66, 170, 120),
    "robot": (75, 132, 232),
    "text": (240, 244, 249),
    "muted": (166, 179, 195),
    "accent": (104, 190, 245),
    "warning": (245, 191, 85),
}


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
    if args.fixed:
        obstacles = 0 if args.obstacles is None else args.obstacles
        task_rate = 0.0 if args.task_rate is None else args.task_rate
        return make_main_scenario(seed, obstacles, task_rate)

    return make_random_scenario(
        seed=seed,
        grid_size=args.size,
        n_robots=args.robots,
        n_tasks=args.tasks,
        n_walls=args.walls,
        n_moving=4 if args.obstacles is None else args.obstacles,
        task_rate=0.08 if args.task_rate is None else args.task_rate,
        random_starts=not args.corners,
    )


def draw_text(pygame, surface, font, text, position, color=None):
    surface.blit(font.render(str(text), True, color or COLORS["text"]), position)


def cell_center(cell, cell_size, offset=(0, 0)):
    row, col = cell
    return (offset[0] + col * cell_size + cell_size // 2,
            offset[1] + row * cell_size + cell_size // 2)


def draw_grid(pygame, screen, env, cell_size, origin, label_font):
    grid_size = env.grid_size * cell_size
    pygame.draw.rect(screen, COLORS["floor"], (*origin, grid_size, grid_size), border_radius=8)

    for row in range(env.grid_size):
        for col in range(env.grid_size):
            rect = (origin[0] + col * cell_size, origin[1] + row * cell_size,
                    cell_size, cell_size)
            pygame.draw.rect(screen, COLORS["grid"], rect, 1)

    for row, col in env.walls:
        rect = (origin[0] + col * cell_size + 2, origin[1] + row * cell_size + 2,
                cell_size - 4, cell_size - 4)
        pygame.draw.rect(screen, COLORS["wall"], rect, border_radius=3)

    for cell, _ in env.moving_obstacles:
        center = cell_center(cell, cell_size, origin)
        radius = max(3, cell_size // 3)
        pygame.draw.circle(screen, COLORS["obstacle"], center, radius)
        pygame.draw.circle(screen, (255, 224, 187), center, radius, 1)

    for task in env.tasks:
        center = cell_center(task, cell_size, origin)
        radius = max(4, cell_size // 3)
        pygame.draw.circle(screen, COLORS["task"], center, radius)
        if cell_size >= 18:
            badge = label_font.render(str(env.priority_of(task)), True, (255, 255, 255))
            screen.blit(badge, badge.get_rect(center=center))

    for robot_id, cell in enumerate(env.robots):
        center = cell_center(cell, cell_size, origin)
        radius = max(5, cell_size * 2 // 5)
        pygame.draw.circle(screen, COLORS["robot"], center, radius)
        pygame.draw.circle(screen, (226, 239, 255), center, radius, 1)
        if cell_size >= 16:
            label = label_font.render(str(robot_id), True, (255, 255, 255))
            screen.blit(label, label.get_rect(center=center))


def draw_legend(pygame, screen, font, x, y):
    entries = [
        ("wall", "Wall"), ("obstacle", "Moving obstacle"),
        ("task", "Task (number = priority)"), ("robot", "Robot (number = ID)"),
    ]
    for color_name, label in entries:
        pygame.draw.circle(screen, COLORS[color_name], (x + 8, y + 10), 7)
        draw_text(pygame, screen, font, label, (x + 24, y), COLORS["muted"])
        y += 27


def draw_panel(pygame, screen, env, seed, paused, speed, fonts, x, width, height):
    pygame.draw.rect(screen, COLORS["panel"], (x, 0, width, height))
    title, body, small = fonts
    margin = 22
    left = x + margin
    draw_text(pygame, screen, title, "ROBOT TEAM", (left, 20))
    draw_text(pygame, screen, small, f"Seed {seed}  •  {env.grid_size} × {env.grid_size}",
              (left, 55), COLORS["muted"])

    state = "PAUSED" if paused else "RUNNING"
    state_color = COLORS["warning"] if paused else COLORS["task"]
    pygame.draw.rect(screen, COLORS["panel_light"], (left, 88, 115, 30), border_radius=8)
    pygame.draw.circle(screen, state_color, (left + 14, 103), 5)
    draw_text(pygame, screen, small, state, (left + 26, 94), state_color)
    draw_text(pygame, screen, small, f"{speed:g} turns/sec", (left + 130, 95), COLORS["muted"])

    draw_text(pygame, screen, body, "RUN STATUS", (left, 139), COLORS["accent"])
    open_count = len(env.tasks)
    completion = (100 * env.completed / (env.completed + open_count)
                  if env.completed + open_count else 0)
    stats = [
        ("Turn", env.turn),
        ("Packages delivered", env.completed),
        ("Tasks still open", open_count),
        ("Completion", f"{completion:.0f}%"),
        ("Avg. completion time", "—" if env.metrics()["avg_completion_time"] is None
         else f"{env.metrics()['avg_completion_time']:.1f} turns"),
        ("Conflicts avoided", env.collisions_avoided),
        ("Obstacle hits", env.obstacle_hits),
        ("Robot efficiency", "—" if env.metrics()["efficiency"] is None
         else f"{env.metrics()['efficiency'] * 100:.0f}%"),
    ]
    y = 170
    for label, value in stats:
        draw_text(pygame, screen, small, label, (left, y), COLORS["muted"])
        value_color = COLORS["warning"] if label == "Obstacle hits" and value else COLORS["text"]
        value_image = small.render(str(value), True, value_color)
        screen.blit(value_image, (x + width - margin - value_image.get_width(), y))
        y += 22

    y += 7
    pygame.draw.line(screen, COLORS["grid"], (left, y), (x + width - margin, y), 1)
    y += 14
    draw_text(pygame, screen, body, "ROBOT ASSIGNMENTS", (left, y), COLORS["accent"])
    y += 32
    for robot_id, task in enumerate(env.assignments):
        color = COLORS["robot"]
        pygame.draw.circle(screen, color, (left + 9, y + 9), 8)
        draw_text(pygame, screen, small, robot_id, (left + 5, y + 1))
        if task is None:
            label = "Idle"
        else:
            label = f"Deliver to ({task[0]}, {task[1]})  P{env.priority_of(task)}"
        draw_text(pygame, screen, small, label, (left + 24, y), COLORS["text"])
        y += 27

    y += 8
    pygame.draw.line(screen, COLORS["grid"], (left, y), (x + width - margin, y), 1)
    y += 14
    draw_text(pygame, screen, body, "LEGEND", (left, y), COLORS["accent"])
    draw_legend(pygame, screen, small, left, y + 30)

    footer_y = height - 96
    pygame.draw.line(screen, COLORS["grid"], (left, footer_y),
                     (x + width - margin, footer_y), 1)
    draw_text(pygame, screen, small, "SPACE  Pause / resume", (left, footer_y + 12), COLORS["muted"])
    draw_text(pygame, screen, small, "N  Step once while paused", (left, footer_y + 34), COLORS["muted"])
    draw_text(pygame, screen, small, "R  New world     +/-  Speed", (left, footer_y + 56), COLORS["muted"])
    draw_text(pygame, screen, small, "ESC  Quit", (left, footer_y + 78), COLORS["muted"])


def main():
    args = parse_args()
    import pygame  # Keep --help usable when pygame is not installed.

    pygame.init()
    seed = args.seed if args.seed is not None else random.randrange(10 ** 6)
    env = make_environment(args, seed)
    print(f"World seed: {seed} (replay with --seed {seed})")

    cell_size = max(12, min(30, 600 // env.grid_size))
    grid_pixels = cell_size * env.grid_size
    panel_width = 330
    margin = 20
    window_width = grid_pixels + panel_width + margin * 3
    window_height = max(grid_pixels + margin * 2, 730)
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Multi-Robot Coordination")
    fonts = (pygame.font.SysFont(None, 28), pygame.font.SysFont(None, 21),
             pygame.font.SysFont(None, 18))
    clock = pygame.time.Clock()
    paused = False
    speed = max(0.2, float(args.fps))
    accumulator = 0.0
    running = True
    origin = (margin, (window_height - grid_pixels) // 2)

    while running:
        frame_time = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_n and paused:
                    assign_waiting_tasks(env)
                    env.step(plan_actions(env, env.assignments))
                elif event.key == pygame.K_r:
                    seed = random.randrange(10 ** 6)
                    env = make_environment(args, seed)
                    accumulator = 0
                    print("New world seed:", seed)
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    speed = min(30, speed + 1)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    speed = max(0.2, speed - 1)

        if not paused:
            accumulator += frame_time
            while accumulator >= 1 / speed:
                assign_waiting_tasks(env)
                env.step(plan_actions(env, env.assignments))
                accumulator -= 1 / speed

        screen.fill(COLORS["background"])
        draw_grid(pygame, screen, env, cell_size, origin, fonts[2])
        panel_x = grid_pixels + margin * 2
        draw_panel(pygame, screen, env, seed, paused, speed, fonts,
                   panel_x, panel_width, window_height)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
