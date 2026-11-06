from environment import Environment
from navigation import action_toward, plan_actions


def expect_error(function):
    try:
        function()
    except ValueError:
        return
    assert False, "Expected a ValueError"


def test_action_toward_each_direction():
    assert action_toward((5, 5), (4, 5)) == 0, "up"
    assert action_toward((5, 5), (6, 5)) == 1, "down"
    assert action_toward((5, 5), (5, 4)) == 2, "left"
    assert action_toward((5, 5), (5, 6)) == 3, "right"


def test_action_toward_rejects_cells_that_are_not_adjacent():
    expect_error(lambda: action_toward((5, 5), (5, 5)))   # same cell
    expect_error(lambda: action_toward((5, 5), (4, 6)))   # diagonal
    expect_error(lambda: action_toward((5, 5), (5, 8)))   # too far


def test_plan_actions_moves_toward_the_target():
    env = Environment(20, set(), [(0, 0)], [])
    assert plan_actions(env, [(0, 5)]) == [3]
    assert plan_actions(env, [(5, 0)]) == [1]


def test_plan_actions_idle_robot_stays():
    env = Environment(20, set(), [(0, 0), (3, 3)], [])
    assert plan_actions(env, [None, None]) == [4, 4]


def test_plan_actions_stays_when_the_target_is_unreachable():
    env = Environment(20, {(0, 1), (1, 0)}, [(0, 0)], [])
    assert plan_actions(env, [(5, 5)]) == [4], "Boxed in: no path, so stay"


def test_plan_actions_stays_when_already_on_the_target():
    env = Environment(20, set(), [(3, 3)], [])
    assert plan_actions(env, [(3, 3)]) == [4]


def test_plan_actions_treats_a_busy_robot_as_blocked():
    env = Environment(20, {(1, 0), (1, 1)}, [(0, 0), (0, 1)], [])
    # Robot 0 is in a corridor behind robot 1, which is working and moving off.
    assert plan_actions(env, [(0, 5), (0, 9)]) == [4, 3]


def run_turns(env, turns):
    from allocation import assign_waiting_tasks
    for _ in range(turns):
        assign_waiting_tasks(env)
        env.step(plan_actions(env, env.assignments))


# ---------- idle robots give way ----------

def test_idle_robot_in_a_corridor_does_not_block_a_working_robot():
    walls = {(1, col) for col in range(10)}          # only row 0 is open
    env = Environment(10, walls, [(0, 0), (0, 1)], [(0, 6)])
    env.assignments[0] = (0, 6)        # robot 0 works, robot 1 stays idle
    run_turns(env, 20)
    assert env.completed == 1, "The idle robot must not wall the corridor off"


def test_idle_robot_steps_into_a_side_pocket_when_there_is_one():
    walls = {(1, col) for col in range(10) if col != 3}    # pocket at (1, 3)
    env = Environment(10, walls, [(0, 0), (0, 3)], [(0, 6)])
    env.assignments[0] = (0, 6)        # robot 0 works, robot 1 stays idle
    run_turns(env, 20)
    assert env.completed == 1
    assert env.robots[0] == (0, 6)
    assert env.robots[1] == (1, 3), "It should pull into the pocket, not run ahead"


def test_a_busy_robot_is_never_asked_to_give_way():
    walls = {(1, col) for col in range(10)}
    env = Environment(10, walls, [(0, 0), (0, 1)], [])
    # Robot 1 is working (target behind robot 0), so robot 0 must not push it.
    actions = plan_actions(env, [(0, 6), (0, 0)])
    assert actions[1] == 4, "Robot 1 cannot move into robot 0 and is not displaced"


def test_lower_priority_busy_robot_yields_into_a_side_pocket():
    walls = {(1, col) for col in range(10) if col != 4}
    tasks = [(0, 0), (0, 8)]
    env = Environment(10, walls, [(0, 2), (0, 4)], tasks, priorities={
        (0, 8): 3, (0, 0): 1,
    })
    env.assignments = [(0, 8), (0, 0)]
    for _ in range(12):
        env.step(plan_actions(env, env.assignments))
    assert env.completed == 2, "Both robots should pass using the side pocket"


# ---------- moving obstacles are avoided ahead of time ----------

def test_obstacle_forecast_is_exact_and_bounces():
    env = Environment(20, set(), [(0, 0)], [], [((8, 18), (0, 1))])
    assert env.obstacle_forecast(3) == [{(8, 19)}, {(8, 18)}, {(8, 17)}]


def test_robot_does_not_walk_into_an_oncoming_obstacle():
    env = Environment(20, set(), [(5, 5)], [(5, 9)], [((5, 7), (0, -1))])
    env.assignments[0] = (5, 9)
    for _ in range(15):
        env.step(plan_actions(env, env.assignments))
    assert env.obstacle_hits == 0
    assert env.completed == 1, "It still gets to its task"


def test_idle_robot_dodges_an_oncoming_obstacle():
    env = Environment(20, set(), [(5, 5)], [], [((5, 10), (0, -1))])
    for _ in range(15):
        env.step(plan_actions(env, [None]))
    assert env.obstacle_hits == 0
