import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from person import Person
from pulp import *
import logging


class MatchMaker:
    def __init__(self, rows) -> None:
        self.persons = []
        self._initialise_participants(rows)
        self._create_match_variables()
        self._initialse_problem()

    def _initialise_participants(self, rows: pd.DataFrame):
        for index, row in rows.iterrows():
            person = Person.build(row)
            self.persons.append(person)

        logging.info(f"Registered {len(self.persons)} persons for matching.")

    def _create_match_variables(self):
        self.possible_matches = [tuple(c) for c in allcombinations(range(len(self.persons)), k=2) if len(set(c)) == 2]
        self.possible_matches += [(idx, idx) for idx in range(len(self.persons))]

        self.variables = LpVariable.dicts("match", self.possible_matches, lowBound=0, upBound=1, cat=LpInteger)

    def _initialse_problem(self):
        self.prob = LpProblem("Date_Pairing_Problem", LpMaximize)

        # Scoring function
        self.prob += lpSum(
            [
                self.variables[(idx1, idx2)] * self.persons[idx1].matrix_similarity(self.persons[idx2])
                for idx1, idx2 in self.possible_matches
            ]
        )

        # Ensure that each person is matched with one other person
        for idx, _ in enumerate(self.persons):
            b_matches_for_person = []
            for possible_match in self.possible_matches:
                if idx in possible_match:
                    b_matches_for_person.append(self.variables[possible_match])
            self.prob += lpSum(b_matches_for_person) == 1


        # # add constraint that each pair in x is pairable
        for idx, person in enumerate(self.persons):
            for idx2, person2 in enumerate(self.persons):
                if idx<=idx2:
                    self.prob += self.variables[(idx, idx2)] <= person.is_pairable(person2)

        self.prob.writeLP("DatingModel.lp")


    def solve(self):
        self.prob.solve(solver=PULP_CBC_CMD(msg=False))

        logging.info(f"Status: {LpStatus[self.prob.status]}")
        logging.info(f"Mean Score: {value(self.prob.objective) / len(self.persons)}")

        scores = []
        num_matches = 0
        for idx1, idx2 in self.possible_matches:
            if self.variables[(idx1, idx2)].varValue > 0:
                # print(f"{self.persons[idx1].name} - {self.persons[idx2].name}")
                scores.append(self.persons[idx1].matrix_similarity(self.persons[idx2]))
                if idx1 != idx2:
                    num_matches += 2

        logging.info(f"Scores: {scores}")

        for v in self.prob.variables():
            if v.varValue > 0:
                print(v.name, "=", v.varValue)

        print("Number of matches:", num_matches)
        print("Number of people not matched:", len(self.persons) - num_matches)


# # Class that stores possible matches and actual matches
# class Match:

#     @property
#     def matches(self):
#         return self._matches
