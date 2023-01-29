
from typing import Dict, List, Set, Tuple

from pulp import *

from date_matching.person import Person


# Class that stores possible match variables and actual matches
class MatchTracker:
    def __init__(self, persons):
        self.persons = persons
        self.possible_matches = [tuple(c) for c in allcombinations(range(len(self.persons)), k=2) if len(set(c)) == 2]
        self.possible_matches += [(idx, idx) for idx in range(len(self.persons))]
        self.variables = LpVariable.dicts("match", self.possible_matches, lowBound=0, upBound=1, cat=LpInteger)

    # Get all the variables that a person is tracked by, each variable is linked to 2 participants
    def get_variables_for_person(self, idx) -> List[LpVariable]:
        return [self.variables[possible_match] for possible_match in self.possible_matches if idx in possible_match]

    # Return list of variables and both people that represent this variable
    def get_variables_to_people(self) -> List[Tuple[LpVariable, Person, Person]]:
        return [
            (self.variables[possible_match], self.persons[possible_match[0]], self.persons[possible_match[1]])
            for possible_match in self.possible_matches
        ]

    # Get variables which are set to True
    def get_true_variables(self) -> List[LpVariable]:
        return [self.variables[possible_match] for possible_match in self.get_true_possible_matches()]

    # Return list of pairs of persons that are matched
    def get_matches(self) -> List[Tuple[Person, Person]]:
        return [
            (self.persons[possible_match[0]], self.persons[possible_match[1]])
            for possible_match in self.get_true_possible_matches()
        ]

    # Same as get_matches but returns the indices of the persons instead
    def get_true_possible_matches(self) -> List[Tuple[int, int]]:
        return [
            possible_match for possible_match in self.possible_matches if self.variables[possible_match].varValue > 0
        ]
