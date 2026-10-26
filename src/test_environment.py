from environment import Environment
from allocation import run_auction, assign_waiting_tasks
from navigation import plan_actions


# ---------- movement ----------

def test_robot_moves_one_cell():
    env = Environment(20, set(), [(5, 5)], [])
    env.step([3])
    assert env.robots == [(5, 6)], "Right should add 1 to the column"


def test_robot_stops_at_grid_edge():
    env = Environment(20, set(), [(0, 0)], [])
    env.step([0])
    assert env.robots == [(0, 0)], "Robot must not leave the grid"


def test_robot_stops_at_wall():
    env = Environment(20, {(5, 6)}, [(5, 5)], [])
    env.step([3])
    assert env.robots == [(5, 5)], "Robot must not enter a wall"


# ---------- conflicts between robots ----------

def test_two_robots_want_same_cell():
    env = Environment(20, set(), [(2, 2), (2, 4)], [])
    env.step([3, 2])
    assert env.robots == [(2, 3), (2, 4)], "Lower number wins, other waits"
    assert env.collisions_avoided == 1


def test_robot_cannot_enter_a_standing_robot():
    env = Environment(20, set(), [(0, 0), (0, 1)], [])
    env.step([3, 4])
    assert env.robots == [(0, 0), (0, 1)], "The robot that stays keeps its cell"


def test_chain_of_blocked_robots():
    env = Environment(20, set(), [(0, 0), (0, 1), (0, 2)], [])
    env.step([3, 3, 4])
    assert env.robots == [(0, 0), (0, 1), (0, 2)], "Nobody can move"
    assert env.collisions_avoided == 2


def test_swap_is_blocked():
    env = Environment(20, set(), [(0, 0), (0, 1)], [])
    env.step([3, 2])
    assert env.robots == [(0, 0), (0, 1)], "Robots must not pass through each other"


def test_same_blocked_pair_is_counted_once():
    env = Environment(20, set(), [(0, 0), (0, 1)], [])
    for turn in range(3):
        env.step([3, 2])
    assert env.collisions_avoided == 1, "One ongoing conflict is one event"


# ---------- tasks ----------

def test_task_is_completed_and_robot_freed():
    env = Environment(20, set(), [(0, 0), (5, 5)], [(0, 1)])
    env.assignments[0] = (0, 1)
    env.step([3, 4])
    assert env.completed == 1
    assert env.tasks == []
    assert env.assignments == [None, None]


def test_assigned_robot_is_freed_when_another_robot_finishes_its_task():
    env = Environment(20, set(), [(0, 0), (0, 4)], [(0, 3)])
    env.assignments[0] = (0, 3)
    env.step([4, 2])
    assert env.completed == 1
    assert env.assignments[0] is None, "Robot 0 had that task, so it is free now"


def test_scheduled_task_appears_on_its_turn():
    env = Environment(20, set(), [(0, 0)], [], None, {3: (5, 5)})
    env.step([4])
    env.step([4])
    assert env.tasks == [], "Not yet"
    env.step([4])
    assert env.tasks == [(5, 5)], "Appears on turn 3"


# ---------- moving obstacles ----------

def test_obstacle_bounces_at_grid_edge():
    env = Environment(20, set(), [(0, 0)], [], [((8, 18), (0, 1))])
    env.step([4])
    assert env.obstacles == {(8, 19)}
    env.step([4])
    assert env.obstacles == {(8, 18)}, "Bounced back"


def test_obstacle_bounces_off_wall():
    env = Environment(20, {(8, 6)}, [(0, 0)], [], [((8, 3), (0, 1))])
    for turn in range(3):
        env.step([4])
    assert env.obstacles == {(8, 6), (8, 4)}, "Wall stays, obstacle turned around"


def test_obstacle_hit_is_counted():
    env = Environment(20, set(), [(8, 5)], [], [((8, 4), (0, 1))])
    env.step([4])
    assert env.obstacle_hits == 1


# ---------- bad input ----------

def expect_error(function):
    try:
        function()
    except ValueError:
        return
    assert False, "Expected a ValueError"


def test_bad_setups_are_rejected():
    expect_error(lambda: Environment(20, set(), [(3, 3), (3, 3)], []))
    expect_error(lambda: Environment(20, {(5, 5)}, [(0, 0)], [(5, 5)]))
    expect_error(lambda: Environment(20, set(), [(0, 0)], [(25, 3)]))
    env = Environment(20, set(), [(0, 0), (5, 5)], [])
    expect_error(lambda: env.step([3]))


# ---------- planning and auction ----------

def test_planning_goes_around_a_parked_robot():
    env = Environment(20, set(), [(0, 5), (0, 0)], [(0, 10)])
    env.assignments[1] = (0, 10)
    for turn in range(40):
        env.step(plan_actions(env, env.assignments))
    assert env.robots[1] == (0, 10), "Robot 1 must reach its task"
    assert env.completed == 1


def test_idle_robot_stays_put():
    env = Environment(20, set(), [(0, 0), (5, 5)], [(0, 3)])
    for turn in range(5):
        assign_waiting_tasks(env)
        env.step(plan_actions(env, env.assignments))
    assert env.robots[1] == (5, 5), "Robot 1 has no task, so it stays"


def test_closest_robot_wins_the_auction():
    env = Environment(20, set(), [(0, 0), (0, 10)], [])
    assert run_auction(env, (0, 8)) == 1


def test_busy_robot_does_not_bid():
    env = Environment(20, set(), [(0, 0), (0, 10)], [])
    env.assignments[1] = (5, 5)
    assert run_auction(env, (0, 8)) == 0


def test_urgent_task_is_auctioned_first():
    env = Environment(20, set(), [(0, 0)], [(0, 3), (0, 8)], None, None,
                      {(0, 3): 1, (0, 8): 5})
    assign_waiting_tasks(env)
    assert env.assignments == [(0, 8)], "Priority 5 beats priority 1"
    assert env.waiting_tasks() == [(0, 3)]

    # ---------- preemption ----------

def test_urgent_task_takes_a_robot_from_a_routine_task():
    env = Environment(20, set(), [(0, 0)], [(0, 10), (5, 5)], None, None, {(5, 5): 5})
    env.assignments[0] = (0, 10)
    assign_waiting_tasks(env)
    assert env.assignments == [(5, 5)], "The urgent task takes the robot"
    assert env.waiting_tasks() == [(0, 10)], "The routine task is waiting again"


def test_equal_priority_does_not_preempt():
    env = Environment(20, set(), [(0, 0)], [(0, 10), (5, 5)])
    env.assignments[0] = (0, 10)
    assign_waiting_tasks(env)
    assert env.assignments == [(0, 10)], "Same priority must not take the robot"


def test_preemption_takes_the_cheapest_robot():
    env = Environment(20, set(), [(0, 0), (0, 19)], [(0, 5), (0, 15), (3, 2)],
                      None, None, {(3, 2): 5})
    env.assignments = [(0, 5), (0, 15)]
    assign_waiting_tasks(env)
    assert env.assignments == [(3, 2), (0, 15)], "Robot 0 is much closer to (3, 2)"
    assert env.waiting_tasks() == [(0, 5)]


def test_urgent_task_arriving_mid_run_is_done_quickly():
    env = Environment(20, set(), [(0, 0), (0, 19)], [(0, 15), (0, 5)],
                      None, {2: (3, 2)}, {(3, 2): 5})
    finished_on = None
    for turn in range(60):
        assign_waiting_tasks(env)
        env.step(plan_actions(env, env.assignments))
        if finished_on is None and env.turn >= 2 and (3, 2) not in env.tasks:
            finished_on = env.turn
    assert finished_on is not None and finished_on <= 6, "Urgent task done by turn 6"
    assert env.completed == 3, "The routine tasks still get done"

# ---------- metrics ----------

def test_completion_time_counts_from_the_turn_a_task_appears():
    env = Environment(20, set(), [(0, 0)], [], None, {2: (0, 3)})
    for turn in range(10):
        assign_waiting_tasks(env)
        env.step(plan_actions(env, env.assignments))
    assert env.completion_times == [3], "Appeared on turn 2, finished on turn 5"


def test_task_present_from_the_start_counts_from_turn_zero():
    env = Environment(20, set(), [(0, 0)], [(0, 3)])
    for turn in range(10):
        assign_waiting_tasks(env)
        env.step(plan_actions(env, env.assignments))
    assert env.completion_times == [3]


def test_efficiency_drops_when_a_robot_with_a_task_is_blocked():
    env = Environment(20, set(), [(0, 0), (0, 1)], [])
    env.assignments = [(0, 5), (0, 9)]
    env.step([3, 4])
    assert env.metrics()["efficiency"] == 0.0, "Neither robot made progress"


def test_idle_robots_do_not_count_in_efficiency():
    env = Environment(20, set(), [(0, 0), (5, 5)], [])
    env.assignments = [(0, 5), None]
    env.step([3, 4])
    assert env.metrics()["efficiency"] == 1.0, "Only the working robot counts"


def test_metrics_are_none_before_anything_happens():
    env = Environment(20, set(), [(0, 0)], [])
    results = env.metrics()
    assert results["avg_completion_time"] is None
    assert results["efficiency"] is None
    assert results["tasks_per_turn"] is None


# ---------- randomness ----------

def tasks_after(seed, rate=0.2, turns=30):
    env = Environment(20, set(), [(0, 0)], [], seed=seed, task_rate=rate)
    for _ in range(turns):
        env.step([4])
    return env.tasks


def test_same_seed_gives_the_same_random_tasks():
    assert tasks_after(5) == tasks_after(5), "Same seed must replay exactly"


def test_different_seeds_give_different_random_tasks():
    assert tasks_after(5) != tasks_after(6)


def test_no_random_tasks_when_the_rate_is_zero():
    assert tasks_after(5, rate=0.0) == []


def test_random_tasks_never_land_on_walls_or_robots():
    walls = {(r, c) for r in range(10) for c in range(20)}
    env = Environment(20, walls, [(15, 5)], [], seed=2, task_rate=1.0)
    for _ in range(50):
        env.step([4])
    assert len(env.tasks) > 0
    for task in env.tasks:
        assert task not in walls, "Task on a wall"
        assert task != (15, 5), "Task on a robot"


def test_random_obstacles_start_on_free_cells():
    env = Environment(20, {(5, 8)}, [(0, 0), (19, 0)], [(12, 5)], seed=1, random_obstacles=3)
    assert len(env.moving_obstacles) == 3
    for cell, direction in env.moving_obstacles:
        assert cell not in {(5, 8), (0, 0), (19, 0), (12, 5)}


def test_reset_with_a_seed_replays_the_same_obstacles():
    env = Environment(20, set(), [(0, 0)], [], seed=1, random_obstacles=3)
    first = list(env.moving_obstacles)
    env.reset()
    assert env.moving_obstacles != first, "A plain reset gives a new layout"
    env.reset(seed=1)
    assert env.moving_obstacles == first, "Reset with the same seed replays it"
    
if __name__ == "__main__":
    count = 0
    for name, function in list(globals().items()):
        if name.startswith("test_"):
            function()
            print("ok:", name)
            count += 1
    print(count, "tests passed")