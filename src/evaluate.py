from environment import Environment
from allocation import assign_waiting_tasks
from navigation import plan_actions


def make_main_scenario():
    walls = {(5, 8), (5, 9), (5, 10)}
    robot_starts = [(0, 0), (19, 0), (19, 19)]
    tasks = [(12, 5), (3, 14)]
    moving = [((10, 0), (0, 1)), ((2, 17), (1, 0))]
    new_tasks = {10: (15, 15), 20: (4, 4)}
    priorities = {(15, 15): 3, (4, 4): 2}
    return Environment(20, walls, robot_starts, tasks, moving, new_tasks, priorities)


def run(env, turns):
    for _ in range(turns):
        assign_waiting_tasks(env)
        env.step(plan_actions(env, env.assignments))
    return env.metrics()


if __name__ == "__main__":
    results = run(make_main_scenario(), 60)
    for name, value in results.items():
        print(name, ":", value)