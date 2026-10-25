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


if __name__ == "__main__":
    count = 0
    for name, function in list(globals().items()):
        if name.startswith("test_"):
            function()
            print("ok:", name)
            count += 1
    print(count, "tests passed")