from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Tuple, Union
import pandas as pd
import numpy as np
from functools import partial
from scipy.spatial.distance import cosine

class StrRepr:
    def __repr__(self):
        return self.value

class Identity(StrRepr, Enum):
    MAN = "MAN"
    WOMAN = "WOMAN"
    ANY = "ANY"
    UNDEFINED = "UNDEFINED"

    @classmethod
    def from_string(cls: "Identity", s: str) -> "Identity":
        s = s.upper()

        # TODO: move to configs
        gender_map = {
            cls.ANY: ["NON-BINARY", "EVERYONE", "ANYONE", "ANY", "ALL"],
            cls.WOMAN: ["WOMAN", "WOMEN"],
            cls.MAN: ["MAN", "MEN"],
        }
        for gender_enum, aliases in gender_map.items():
            if s in aliases:
                return gender_enum

        return cls.UNDEFINED

class Year(StrRepr, Enum):
    FIRST = "1st Year"
    SECOND = "2nd Year"
    THIRD = "3rd Year"
    FOURTH = "4th Year"
    POSTGRAD = "Postgraduate"

    @classmethod
    def from_string(cls: "Year", s: str) -> "Year":
        return cls(s)


class YearPreference(StrRepr, Enum):
    ANY = "ANY"
    SAME = "SAME"
    DIFFERENT = "DIFFERENT"

    @classmethod
    def from_string(cls: "YearPreference", s: str) -> "YearPreference":
        s = s.upper()
        if "SAME" in s:
            return cls.SAME
        elif "DIFFERENT" in s:
            return cls.DIFFERENT
        elif "OPEN" in s:
            return cls.ANY


@dataclass
class Person:
    name: str
    student_id: str
    gender: Identity = field()
    seeking: Identity
    matrix: Dict[str, Union[int, float]] = field(repr=False)
    day_choice: str
    year: Year
    year_preference: YearPreference

    @classmethod
    def build(cls: "Person", row: pd.Series) -> "Person":
        # TODO: move to configs
        name = row["Name (Full Name)"]
        student_id = row["Student ID"]
        gender = Identity.from_string(row["I identify as..."])
        seeking = Identity.from_string(row["I am interested in..."])
        which_day = row["Which day would you prefer the date to be on?"]
        year = Year.from_string(row["Which year are you in?"])
        year_preference = YearPreference.from_string(row["I would like to go on a date with someone who is..."])

        # identify columns that are of type float64
        matrix_cols = {k: v for k, v in row.items() if isinstance(v, float)}

        return cls(name, student_id, gender, seeking, matrix_cols, which_day, year, year_preference)

    def matrix_similarity(self, other: "Person") -> float:
        """
        Returns the similarity between the two people based on their matrix
        """
        if self == other:
            return 0.0

        common_keys = set(self.matrix.keys()).intersection(set(other.matrix.keys()))
        if len(common_keys) == 0:
            return 0

        vector1 = np.array([self.matrix[k] for k in common_keys])
        vector2 = np.array([other.matrix[k] for k in common_keys])

        # return np.linalg.norm(vector1 - vector2)
        score = 1 - cosine(vector1, vector2)
        assert 0 <= score <= 1
        return score

    def is_pairable(self, other: "Person") -> bool:
        """
        Returns True if the two people are pairable
        This defines hard constraints that must be satisfied

        A person is pairable if:
            Allow pairing with self
            They are seeking each others' gender
            They can meet on the same day
        """
        if self == other:
            return True

        constraints = [self._gender_seeking_constraint, self._day_preference_constraint]

        return self._evaluate_constraints(constraints)(other)

    def is_pairing_preferred(self, other: "Person") -> bool:
        """
        Returns True if the two people are preferred to be paired
        This defines soft constraints that are preferred to be satisfied

        1. Attempt to match people with their year preference
        """
        if self == other:
            return True

        constraints = [self._year_preference_constraint]

        return self._evaluate_constraints(constraints)(other)

    def _year_preference_constraint(self, other: "Person") -> bool:

        is_same_year = self.year == other.year

        def wants_same_year(year_preference):
            return (
                year_preference == YearPreference.ANY
                or (year_preference == YearPreference.SAME and is_same_year)
                or (year_preference == YearPreference.DIFFERENT and not is_same_year)
            )

        wanting = wants_same_year(self.year_preference)
        other_wanting = wants_same_year(other.year_preference)

        return wanting and other_wanting

    def _gender_seeking_constraint(self, other: "Person") -> bool:
        """
        Returns True if the two people are seeking each others
        """
        wanting = self.seeking == Identity.ANY or self.seeking == other.gender
        other_wanting = other.seeking == Identity.ANY or other.seeking == self.gender
        return wanting and other_wanting

    def _day_preference_constraint(self, other: "Person") -> bool:
        """
        Returns True if the two people can meet on the same day
        """
        return self.day_choice == other.day_choice or self.day_choice == "Either" or other.day_choice == "Either"

    def _evaluate_constraints(self, constraints):
        return lambda other: all([constraint(other) for constraint in constraints])
