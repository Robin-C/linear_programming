import csv
import pulp as pl
import collections as cl
import pandas as pd

cov_file = 'coverage.csv'

coverages = dict()
with open(cov_file, 'r') as src:
    for line in src:
        data = line.strip().split(',')
        pattern = data[0]
        shifts = [int(t) for t in data[1:]]
        coverages[pattern] = shifts

shifts = [1, 2, 3, 4, 5]
patterns = coverages.keys()

coverage_map = dict()
for (p, s) in [(p, s) for p in patterns for s in shifts]:
    coverage_map[p, s] = 1 if s in coverages[p] else 0

# define the model: we want to minimize the cost
prob = pl.LpProblem("scheduling", pl.LpMinimize)

agents = ['robin', 'mathew', 'george', 'elisa']


vars_by_shift = {1: [],
                 2: [],
                 3: [],
                 4: [],
                 5: []
                 }

vars_by_agent = {'robin': [],
                 'mathew': [],
                 'george': [],
                 'elisa': []
                 }
schedule = []


def shift_to_be_sent_to(pattern):
    shifts = []
    for shift in range(1, 6):
        if coverage_map[pattern, shift] == 1:
            shifts.append(shift)
    return shifts


# for combination, coverage in coverage_map.items():
for pattern in patterns:
    for agent in agents:
        shifts = shift_to_be_sent_to(pattern)
        var = pl.LpVariable(
            f"{agent},{pattern}", 0, 1, pl.LpInteger)
        for shift in shifts:
            # we want to send the variable to vars_by_shift in all corresponding vars_by_shift[shift] and send it to vars_by_shift only once
            vars_by_shift[shift].append(var)
        schedule.append(var)
        vars_by_agent[agent].append(var)

prob += sum(schedule)

# constraint 1: must schedule someone at shift 1, 2, 5
for shift in vars_by_shift:
    if shift == 1 or shift == 2 or shift == 5:
        prob += sum(vars_by_shift[shift]) >= 1
    if shift == 3 or shift == 4:
        prob += sum(vars_by_shift[shift]) >= 2

# constraint 2: agent cant be scheduled once per day
for agent in agents:
    prob += sum(vars_by_agent[agent]) <= 1

status = prob.solve()
print(pl.LpStatus[status])

# Results handling
results = list()
for shift, vars in vars_by_shift.items():
    for var in vars:
        if var.varValue == 1:
            agent = var.name.split(',')[0]
            results.append({
                "shift": shift,
                "worker": agent
            })

data = []
for result in results:
    data.append([result['shift'], result['worker']])


print("Result:", pl.LpStatus[status])


result_df = pd.DataFrame(data, columns=['shift', 'agent'])
result_df = result_df.sort_values(by=['shift', 'agent'])
result_df.to_csv('./schedule.csv', index=False)
