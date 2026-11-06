"""Run the A* + auction baseline over many seeds and report the mean of each
metric. The RL agent should be compared on the same seeds and settings.

    python baseline.py                      # 100 seeds, 60 turns, 3 random obstacles
    python baseline.py --scenario random --task-rate 0.08 --obstacles 4
    python baseline.py --seeds 20 --csv out.csv
"""

import argparse
import csv
import statistics

from evaluate import run
from scenarios import make_main_scenario, make_random_scenario


def run_seeds(seeds, turns, random_obstacles, task_rate, scenario="main"):
    rows = []
    for seed in range(seeds):
        if scenario == "random":
            env = make_random_scenario(seed=seed, n_moving=random_obstacles,
                                       task_rate=task_rate)
        else:
            env = make_main_scenario(seed=seed, random_obstacles=random_obstacles,
                                     task_rate=task_rate)
        metrics = run(env, turns)
        metrics["seed"] = seed
        rows.append(metrics)
    return rows


def summarise(rows):
    summary = {}
    for name in rows[0]:
        if name == "seed":
            continue
        values = [row[name] for row in rows if row[name] is not None]
        if values:
            summary[name] = (statistics.mean(values), statistics.pstdev(values), len(values))
        else:
            summary[name] = (None, None, 0)
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=100)
    parser.add_argument("--turns", type=int, default=60)
    parser.add_argument("--scenario", choices=["main", "random"], default="main",
                        help="main = the fixed map plus random obstacles; "
                             "random = a new random world for every seed")
    parser.add_argument("--obstacles", type=int, default=3,
                        help="random moving obstacles per run")
    parser.add_argument("--task-rate", type=float, default=0.0,
                        help="chance per turn that a random task appears")
    parser.add_argument("--csv", help="also write one row per seed to this file")
    args = parser.parse_args()

    rows = run_seeds(args.seeds, args.turns, args.obstacles, args.task_rate,
                     args.scenario)
    print(f"{args.scenario} scenario, {args.seeds} seeds, {args.turns} turns, "
          f"{args.obstacles} obstacles, task rate {args.task_rate}")
    for name, (mean, std, n) in summarise(rows).items():
        if mean is None:
            print(f"{name:22s} no data")
        else:
            print(f"{name:22s} mean {mean:8.3f}  std {std:7.3f}  (n={n})")

    if args.csv:
        with open(args.csv, "w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        print("wrote", args.csv)


if __name__ == "__main__":
    main()
