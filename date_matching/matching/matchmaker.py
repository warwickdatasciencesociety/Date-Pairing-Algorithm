import logging
from collections import defaultdict

import numpy as np
import pandas as pd
from pulp import *

from date_matching.config import (LOG_LP_FILE_PATH, PENALTY_MULTIPLIER,
                                  PROBLEM_NAME)
from date_matching.matching.matchtracker import MatchTracker
from date_matching.matching.utils import print_terminal_line
from date_matching.person import Person


class MatchMaker:
    def __init__(self, rows) -> None:
        self.persons = []
        self._initialise_participants(rows)
        self._create_match_variables()
        self._initialse_problem()

    def _initialise_participants(self, rows: pd.DataFrame):
        print_terminal_line("Registered participants")
        for index, row in rows.iterrows():
            person = Person.build(row)
            self.persons.append(person)
            print(index, person)

        print_terminal_line("Solution information")
        logging.info(f"Registered {len(self.persons)} persons for matching.")

    def _create_match_variables(self):
        self.match_tracker = MatchTracker(self.persons)

    def _initialse_problem(self):
        '''
        Initialise the problem and add the objective function
        Then add each of the constraints to represent the problem
        '''
        self.prob = LpProblem(f"{PROBLEM_NAME}_problem".title(), LpMaximize)

        # Scoring function, maximise the sum of the scores while penalising for any soft constraints that are violated
        score_vars = []
        for variable, person1, person2 in self.match_tracker.get_variables_to_people():
            reward = person1.compatibility_score(person2)
            penalty = 1 - person1.is_pairing_preferred(person2)  # positive penalty
            score = reward - (PENALTY_MULTIPLIER * penalty)
            score_vars.append(variable * score)
        self.prob += lpSum(score_vars)

        # Ensure that each person is matched with one other person
        for idx, _ in enumerate(self.persons):
            variables_for_person = self.match_tracker.get_variables_for_person(idx)
            self.prob += lpSum(variables_for_person) == 1

        # Add constraint that each pair in x is pairable
        for variable, person1, person2 in self.match_tracker.get_variables_to_people():
            self.prob += variable <= person1.is_pairable(person2)

        # Log the problem to a file, inspect the file to see the linear function being optimised
        self.prob.writeLP(LOG_LP_FILE_PATH)

    def solve(self):
        '''Solve the problem and log some critical information'''
        self.prob.solve(solver=PULP_CBC_CMD(msg=False))

        logging.info(f"Status: {LpStatus[self.prob.status]}")
        logging.info(f"Mean Score per person: {2*value(self.prob.objective) / len(self.persons)}")

        scores = []
        num_matches = 0

        for person1, person2 in self.match_tracker.get_matches():
            scores.append(person1.compatibility_score(person2))
            if person1 != person2:
                num_matches += 2

        logging.info(f"Scores: {np.round(scores, 2)}")
        logging.info(f"Number of people matched: {num_matches}/{len(self.persons)}")

        print_terminal_line("Logging")
        self.log_matches()
        print_terminal_line()

    def log_matches(self):
        '''
        Perform any additional logging of the matches
        Use this section to retrieve the matches and write to console or a file
        All necessary information is stored in the MatchTracker object
        Two examples are provided below
        '''
        self.log_scheduling_info()
        self.log_gender_pairing_stats()

    def log_scheduling_info(self):
        def get_day_or_either(day1: str, day2: str):
            return day1 if day1 != "Either" else day2

        day_dict = defaultdict(list)
        for idx1, idx2 in self.match_tracker.get_true_possible_matches():
            if idx1 == idx2:
                day_dict["Unmatched"].append((idx1, idx2))
            else:
                day_dict[get_day_or_either(self.persons[idx1].day_choice, self.persons[idx2].day_choice)].append(
                    (idx1, idx2)
                )

        for k, matches in day_dict.items():
            print(f"------ {k} ------ [{len(matches)} pairs]")
            for idx1, idx2 in matches:
                person1, person2 = self.persons[idx1], self.persons[idx2]
                out = f"({idx1}) {person1.name}"
                if idx1!=idx2:
                    out += f" - ({idx2}) {person2.name}"
                print(out)
            print()

    def log_gender_pairing_stats(self):
        # Count and log how many man/woman man/man and woman/woman pairs
        num = defaultdict(int)
        for person1, person2 in self.match_tracker.get_matches():
            if person1 != person2:
                g1, g2 = person1.gender.value.title(), person2.gender.value.title()
                g1, g2 = min(g1, g2), max(g1, g2)
                num[f"{g1}/{g2}"] += 1

        for k, v in num.items():
            print(f"{k}: {v}")