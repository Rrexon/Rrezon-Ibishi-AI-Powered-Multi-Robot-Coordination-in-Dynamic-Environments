from allocation import assign_waiting_tasks
from navigation import plan_actions
from scenarios import (free_space_is_connected, make_main_scenario,
                       make_random_scenario)


def layout(env):
    return (env.walls, env.robot_starts, env.task_locations, env.initial_moving,
            env.initial_priorities)


def test_same_seed_gives_the_same_world():
    assert layout(make_random_scenario(7)) == layout(make_random_scenario(7))


def test_different_seeds_give_different_worlds():
    worlds = [layout(make_random_scenario(seed)) for seed in range(5)]
    for i in range(5):
        for j in range(i + 1, 5):
            assert worlds[i] != worlds[j]


def test_a_world_without_a_seed_still_reports_its_seed():
    env = make_random_scenario()
    assert env.scenario_seed is not None
    assert layout(make_random_scenario(env.scenario_seed)) == layout(env)


def test_everything_starts_on_distinct_free_cells_and_nothing_is_sealed_in():
    for seed in range(60):
        env = make_random_scenario(seed)
        cells = (list(env.robot_starts) + list(env.task_locations)
                 + [cell for cell, direction in env.initial_moving])
        assert len(cells) == len(set(cells)), f"overlap in seed {seed}"
        for row, col in cells:
            assert 0 <= row < env.grid_size and 0 <= col < env.grid_size
            assert (row, col) not in env.walls
        assert free_space_is_connected(env.walls, env.grid_size), f"sealed area, seed {seed}"


def test_obstacles_do_not_start_next_to_a_robot():
    for seed in range(30):
        env = make_random_scenario(seed)
        for (o_row, o_col), direction in env.initial_moving:
            for r_row, r_col in env.robot_starts:
                assert abs(o_row - r_row) + abs(o_col - r_col) > 2


def test_options_are_respected():
    env = make_random_scenario(3, grid_size=12, n_robots=2, n_tasks=4, n_moving=6,
                               task_rate=0.0, random_starts=False)
    assert env.grid_size == 12
    assert len(env.robot_starts) == 2 and len(env.task_locations) == 4
    assert len(env.initial_moving) == 6
    assert env.robot_starts[0] == (0, 0), "Corner starts when random_starts is off"


def test_random_worlds_run_and_robots_get_work_done():
    for seed in range(15):
        env = make_random_scenario(seed)
        for _ in range(120):
            assign_waiting_tasks(env)
            env.step(plan_actions(env, env.assignments))
        assert env.completed >= 3, f"seed {seed} completed only {env.completed}"


def test_the_world_replays_after_reset():
    env = make_random_scenario(4)
    for _ in range(10):
        assign_waiting_tasks(env)
        env.step(plan_actions(env, env.assignments))
    env.reset(seed=1)
    assert env.robots == list(env.robot_starts)
    assert env.tasks == list(env.task_locations)


def test_the_fixed_scenario_is_still_available_and_deterministic():
    a, b = make_main_scenario(), make_main_scenario()
    assert layout(a) == layout(b)


def test_benchmark_records_matched_allocators_and_metrics():
    from benchmark import benchmark, summarize

    rows = benchmark(seeds=1, turns=2, grid_sizes=[8], robot_counts=[1],
                     task_counts=[1], obstacles=1)
    assert len(rows) == 2
    assert rows[0]["seed"] == 0
    assert rows[0]["grid_size"] == 8
    assert rows[0]["robots"] == 1
    assert rows[0]["initial_tasks"] == 1
    assert rows[0]["runtime_seconds"] >= 0
    assert "tasks_completed" in rows[0]
    summary = summarize(rows)
    assert len(summary) == 2
    assert summary[0]["runs"] == 1


def test_distance_map_allocator_matches_astar_on_seeded_world():
    from evaluate import run

    original = make_random_scenario(seed=17)
    optimized = make_random_scenario(seed=17)
    run(original, 60, "astar")
    run(optimized, 60, "distance_map")
    assert original.completed == optimized.completed
    assert original.completion_times == optimized.completion_times
    assert original.robots == optimized.robots
    assert original.assignments == optimized.assignments
