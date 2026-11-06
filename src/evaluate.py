from allocation import assign_waiting_tasks
from navigation import plan_actions
from scenarios import make_main_scenario


def run(env, turns, allocation_method="astar", allocation_stats=None):
    for _ in range(turns):
        assign_waiting_tasks(env, allocation_method, allocation_stats)
        env.step(plan_actions(env, env.assignments))
    return env.metrics()


if __name__ == "__main__":
    results = run(make_main_scenario(), 60)
    for name, value in results.items():
        print(name, ":", value)
