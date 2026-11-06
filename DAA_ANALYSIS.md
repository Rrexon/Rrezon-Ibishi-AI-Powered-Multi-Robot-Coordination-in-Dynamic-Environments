# DAA analysis

This document analyzes the non-learning simulator. The benchmark compares the
original repeated-A* auction with an allocator that computes one shortest-path
distance map per bidding robot and reuses distances for task bids. Robot movement
planning still uses A* in both modes.

## Complexity

Let `V` be the number of free grid cells, `E` the number of adjacent free-cell
pairs, `R` the number of robots, and `K` the number of waiting tasks. A binary
heap implementation of A* has worst-case time `O((V + E) log V)` and space
`O(V)`. On this four-neighbor grid, `E = O(V)`, so this is `O(V log V)` time.

The original auction can run one A* search for each eligible robot/task bid.
In a round with up to `R` robots and `K` tasks, its worst-case allocation time is
`O(R K V log V)`. Priority pre-emption can add bids for assigned robots, still
bounded by `O(R K)` searches. Navigation adds up to a constant number of A*
searches per robot, or `O(R V log V)` per turn. These are worst-case bounds;
searches often stop before visiting the whole grid.

The distance-map allocator runs Dijkstra once for each robot that bids. Its
worst-case allocation time is `O(R (V + E) log V + R K)`, simplified to
`O(R V log V + R K)` on this grid. It uses `O(R V)` extra space to retain maps
for all bidders during the allocation round. This trades memory and full-map
search work for fewer searches when there are many candidate tasks. With few
tasks, ordinary A* can be faster because it stops when it reaches its goal.

## Reproducible experiments

`benchmark.py` runs both allocation methods on identical seeds and settings. It
times the simulation (scenario generation is excluded), repeats configurations,
and records allocation search counts along with runtime and task/safety metrics.
The raw CSV retains each run; the summary CSV groups only identical grid, robot,
task, and allocator settings.

For a controlled grid-size sweep, hold robot/task counts fixed:

```powershell
python benchmark.py --sizes 10 20 30 40 --robots 4 --tasks 6 --seeds 10 --repetitions 5 --csv grid_sweep.csv
```

For robot-count and task-count sweeps, vary only the corresponding option while
holding the others at one value:

```powershell
python benchmark.py --sizes 20 --robots 1 2 4 8 --tasks 6 --seeds 10 --repetitions 5 --csv robot_sweep.csv
python benchmark.py --sizes 20 --robots 4 --tasks 1 3 6 12 --seeds 10 --repetitions 5 --csv task_sweep.csv
```

Compare the two allocators within each matching workload. Check runtime and
search counts together with completion rate, completion time, efficiency, and
obstacle hits. Do not infer a speedup from a single run; Python and operating
system scheduling add timing noise, especially on small grids. Keep the actual
CSV outputs with the report so numerical claims can be traced to measured runs.

## Measured results

The grid-size sweep was run on this machine with 3 seeds, 3 timing repetitions,
60 turns, 4 robots, 6 initial tasks, and 4 moving obstacles. Each row below is
the mean of 9 runs. Runtime is the full simulation time; both methods produced
the same task and safety metrics for every matched configuration.

| Grid | Repeated A* mean runtime | Distance-map mean runtime | A* bid searches/turn | Distance maps/turn |
|---:|---:|---:|---:|---:|
| 10x10 | 0.0085 s | 0.0104 s | 33.0 | 23.0 |
| 20x20 | 0.0110 s | 0.0259 s | 23.7 | 17.3 |
| 30x30 | 0.0314 s | 0.0642 s | 21.0 | 15.0 |
| 40x40 | 0.0356 s | 0.0980 s | 22.0 | 15.7 |

The distance-map method made fewer allocation searches, but took longer in this
experiment. The per-search work is greater because Dijkstra explores all
reachable cells, while A* can stop when it reaches the particular task. So the
distance-map version remains an experimental comparison; repeated A* stays the
default. The robot-count and task-count sweeps are in `daa_results/robots.csv`
and `daa_results/tasks.csv` with corresponding summary CSV files.

These timings are small and machine-dependent. Treat them as evidence for these
settings, not as universal speed ratios. Larger turn counts and more repetitions
would reduce timing noise for a final report.
