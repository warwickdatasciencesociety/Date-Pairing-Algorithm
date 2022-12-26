
from typing import Dict, List, Set, Tuple

from pulp import *

from date_matching.person import Person


# # Class that stores possible matches and actual matches
class MatchTracker:
    def __init__(self, persons):
        self.persons = persons
        self.possible_matches = [tuple(c) for c in allcombinations(range(len(self.persons)), k=2) if len(set(c)) == 2]
        self.possible_matches += [(idx, idx) for idx in range(len(self.persons))]
        self.variables = LpVariable.dicts("match", self.possible_matches, lowBound=0, upBound=1, cat=LpInteger)

    def get_variables_for_person(self, idx) -> List[LpVariable]:
        return [self.variables[possible_match] for possible_match in self.possible_matches if idx in possible_match]

    # return list of variables and both people that represent this variable
    def get_variables_to_people(self) -> List[Tuple[LpVariable, Person, Person]]:
        return [
            (self.variables[possible_match], self.persons[possible_match[0]], self.persons[possible_match[1]])
            for possible_match in self.possible_matches
        ]

    # get variables which are set to True
    def get_true_variables(self) -> List[LpVariable]:
        return [self.variables[possible_match] for possible_match in self.get_true_possible_matches()]

    # return list of pairs of persons that are matched
    def get_matches(self) -> List[Tuple[Person, Person]]:
        return [
            (self.persons[possible_match[0]], self.persons[possible_match[1]])
            for possible_match in self.get_true_possible_matches()
        ]

    def get_true_possible_matches(self) -> List[Tuple[int, int]]:
        return [
            possible_match for possible_match in self.possible_matches if self.variables[possible_match].varValue > 0
        ]
