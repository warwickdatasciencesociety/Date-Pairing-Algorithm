#%%
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from person import Person
from pulp import *
import logging

pd.set_option("display.precision", 2)
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

logging.basicConfig(format='%(levelname)s: %(message)s', level = logging.DEBUG)


dfr = pd.read_csv('data/romantic_dates.csv', header=0)
# print(len(dfr))
dfr = dfr[:5]
# dfr = dfr.sample(frac=1).reset_index(drop=True)
persons = []

for index, row in dfr.iterrows():
    person = Person.build(row)
    persons.append(person)
    print(index, person)

logging.info(f'Registered {len(persons)} persons for matching.')

prob = LpProblem("The Date pairing Problem", LpMaximize)
# %%
possible_matches = [tuple(c) for c in allcombinations(range(len(persons)), k=2) if len(set(c)) == 2]
possible_matches += [(idx, idx) for idx in range(len(persons))]

x = LpVariable.dicts(
    "match", possible_matches, lowBound=0, upBound=1, cat=LpInteger
)
x

#%%
# Ensure that each person is matched with one other person
for idx, person in enumerate(persons):
    b_matches_for_person = []
    for possible_match in possible_matches:
        if idx in possible_match:
            b_matches_for_person.append(x[possible_match])
    prob += lpSum(b_matches_for_person) == 1

#%%
# Scoring function
prob += lpSum([x[(idx1, idx2)] * persons[idx1].matrix_similarity(persons[idx2]) for idx1, idx2 in possible_matches])


#%%
# pairability_constraint = LpConstraint(x_1_2, sense=LpConstraintLE, rhs=is_pairable(1, 2))

# add constraint that each pair in x is pairable
for idx, person in enumerate(persons):
    for idx2, person2 in enumerate(persons):
        if idx<=idx2:
            prob += x[(idx, idx2)] <= person.is_pairable(person2)



#%%
prob.writeLP("DatingModel.lp")
prob.solve(solver=PULP_CBC_CMD(msg=0))
print("Status:", LpStatus[prob.status])
print("Mean Score:", value(prob.objective)/len(persons))

scores = [persons[idx1].matrix_similarity(persons[idx2]) for idx1, idx2 in possible_matches if x[(idx1, idx2)].varValue > 0]
print("Scores:", scores)


for v in prob.variables():
    if v.varValue > 0:
        print(v.name, "=", v.varValue)

num_matches = 0
for possible_match in possible_matches:
    if x[possible_match].varValue > 0 and possible_match[0] != possible_match[1]:
        num_matches += 2

# print number of matches, number of pairs, and how many people are not matched
print("Number of matches:", num_matches)
print("Number of people not matched:", len(persons) - num_matches)

# print which solver was used
# print("Solver:", prob.solver)