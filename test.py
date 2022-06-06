import pulp as pl
import csv
import pandas as pd
import collections as cl

# load agent data
agents = pd.read_csv('./agents.csv')
agent_availabilities = cl.defaultdict(dict)
agent_names = pd.unique(agents['user_id'])

for agent in agent_names:
    agent_availabilities[agent] = []

for index, row in agents.iterrows():
    agent_availabilities[row['user_id']].append(
        [row['first_shift'], row['second_shift']])

# possible shift combination
shift_combinations = cl.defaultdict(dict)
possible_combination = pd.read_csv('./possible_combination.csv')
shifts = pd.unique(possible_combination['shift'])


for agent in agent_names:
    shift_combinations[agent] = {}
    for shift in shifts:
        shift_combinations[agent][shift] = {}
    for index, row in possible_combination.iterrows():
        shift_combinations[agent][row['shift']][row['pattern_1']] = 0
        shift_combinations[agent][row['shift']][row['pattern_2']] = 0

# define the model: we want to minimize the cost
prob = pl.LpProblem("scheduling", pl.LpMinimize)

schedule = []

# Initialize dict
vars_by_shift = cl.defaultdict(dict)
vars_by_pattern = cl.defaultdict(dict)

for shift in shifts:
    vars_by_shift[shift] = []

for agent in agent_names:
    vars_by_pattern[agent] = []

# create variables
for agent in agent_names:
    for shift in range(1, 6):
        for pattern in shift_combinations[agent][shift]:
            var = pl.LpVariable(
                f"{pattern},{shift},{agent}", 0, 1, pl.LpInteger)
            vars_by_shift[shift].append(var)
            vars_by_pattern[agent].append(var)
            schedule.append(var)

# objective
prob += sum(schedule)

# constraint 1: must schedule someone at shift 1, 2, 5
for shift, patterns in vars_by_shift.items():
    if shift == 1 or shift == 2 or shift == 5:
        prob += sum(vars_by_shift[shift]) >= 1
    elif shift == 4 or shift == 5:  # and 2 persons at shift 4 and 5
        prob += sum(vars_by_shift[shift]) >= 2

# constraint 2: agent can at most be scheduled 1 time
for agent in agent_names:
    prob += sum(vars_by_pattern[agent]) <= 1


status = prob.solve()
print("Result:", pl.LpStatus[status])