from environment import Environment

env = Environment(20, set(), [(0, 0), (0, 2)], [(10, 10)])
print(env.desired_position(0, 3))
print(env.desired_position(0, 0))
print(env.robots)