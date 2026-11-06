"""Compare repeated-A* allocation with cached distance maps.

Run from src: python benchmark.py --seeds 5 --repetitions 3
"""

import argparse
import csv
import statistics
from time import perf_counter

from evaluate import run
from scenarios import make_random_scenario


def benchmark(seeds, turns, grid_sizes, robot_counts, task_counts, obstacles,
              repetitions=1):
    """Run both allocators on matched worlds; generation is outside timing."""
    rows = []
    for size in grid_sizes:
        for robots in robot_counts:
            for tasks in task_counts:
                for seed in range(seeds):
                    for repetition in range(repetitions):
                        for method in ("astar", "distance_map"):
                            env = make_random_scenario(
                                seed=seed, grid_size=size, n_robots=robots,
                                n_tasks=tasks, n_moving=obstacles,
                            )
                            stats = {}
                            started = perf_counter()
                            metrics = run(env, turns, method, stats)
                            elapsed = perf_counter() - started
                            rows.append({
                                "seed": seed,
                                "repetition": repetition,
                                "allocator": method,
                                "grid_size": size,
                                "robots": robots,
                                "initial_tasks": tasks,
                                "moving_obstacles": obstacles,
                                "turns": turns,
                                "runtime_seconds": elapsed,
                                "astar_bid_searches": stats.get("astar_bids", 0),
                                "distance_map_searches": stats.get("distance_maps", 0),
                                **metrics,
                            })
    return rows


def summarize(rows):
    """Summarize each fixed workload and allocator across repeats/seeds."""
    fields = ("grid_size", "robots", "initial_tasks", "allocator")
    keys = sorted({tuple(row[field] for field in fields) for row in rows})
    output = []
    for key in keys:
        group = [row for row in rows
                 if tuple(row[field] for field in fields) == key]
        summary = dict(zip(fields, key))
        summary.update({
            "runs": len(group),
            "mean_runtime_seconds": statistics.mean(r["runtime_seconds"] for r in group),
            "median_runtime_seconds": statistics.median(r["runtime_seconds"] for r in group),
            "runtime_std_seconds": statistics.pstdev(r["runtime_seconds"] for r in group),
            "mean_tasks_completed": statistics.mean(r["tasks_completed"] for r in group),
            "mean_completion_rate": statistics.mean(
                r["completion_rate"] for r in group if r["completion_rate"] is not None
            ),
            "mean_efficiency": statistics.mean(
                r["efficiency"] for r in group if r["efficiency"] is not None
            ),
            "mean_obstacle_hits": statistics.mean(r["obstacle_hits"] for r in group),
            "mean_astar_bid_searches": statistics.mean(r["astar_bid_searches"] for r in group),
            "mean_distance_map_searches": statistics.mean(r["distance_map_searches"] for r in group),
        })
        output.append(summary)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--turns", type=int, default=60)
    parser.add_argument("--sizes", type=int, nargs="+", default=[10, 20, 30])
    parser.add_argument("--robots", type=int, nargs="+", default=[2, 4, 8])
    parser.add_argument("--tasks", type=int, nargs="+", default=[3, 6, 12])
    parser.add_argument("--obstacles", type=int, default=4)
    parser.add_argument("--csv", default="benchmark.csv")
    args = parser.parse_args()
    if min(args.seeds, args.repetitions, args.turns) < 1 or args.obstacles < 0:
        parser.error("seeds, repetitions, and turns must be positive; obstacles non-negative")

    rows = benchmark(args.seeds, args.turns, args.sizes, args.robots,
                     args.tasks, args.obstacles, args.repetitions)
    summary = summarize(rows)
    summary_path = args.csv.rsplit(".", 1)[0] + "_summary.csv"
    for path, data in ((args.csv, rows), (summary_path, summary)):
        with open(path, "w", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=list(data[0]))
            writer.writeheader()
            writer.writerows(data)

    print(f"Detailed matched runs: {args.csv} ({len(rows)} rows)")
    print(f"Per-configuration averages: {summary_path} ({len(summary)} rows)")
    print("Average runtime by allocator (all configurations; use the CSV for controlled comparisons):")
    for method in ("astar", "distance_map"):
        values = [r["runtime_seconds"] for r in rows if r["allocator"] == method]
        print(f"  {method:12s} {statistics.mean(values):.5f} s/run")


if __name__ == "__main__":
    main()
