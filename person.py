from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Tuple, Union
import pandas as pd
import numpy as np
from functools import partial
from scipy.spatial.distance import cosine

class Identification(Enum):
    MAN = "MAN"
    WOMAN = "WOMAN"
    ANY = "ANY"
    UNDEFINED = "UNDEFINED"

    @classmethod
    def from_string(cls:'Identification', s: str)->'Identification':
        s = s.upper()

        # TODO: move to configs
        gender_map = {
            cls.ANY: ["NON-BINARY", "EVERYONE", "ANYONE", "ANY", "ALL"],
            cls.WOMAN: ["WOMAN", "WOMEN"],
            cls.MAN: ["MAN","MEN"]
        }
        for gender_enum, aliases in gender_map.items():
            if s in aliases:
                return gender_enum
        
        return cls.UNDEFINED

    def __str__(self):
        return self.value


@dataclass
class Person:
    name: str
    student_id: str
    gender: Identification = field()
    seeking: Identification
    matrix: Dict[str, Union[int, float]] = field(repr=False)
    day_choice: str

    @classmethod
    def build(cls:'Person', row:pd.Series)->'Person':
        # TODO: move to configs
        name = row['Name (Full Name)']
        student_id = row['Student ID']
        gender = Identification.from_string(row['I identify as...'])
        seeking = Identification.from_string(row['I am interested in...'])
        which_day = row['Which day would you prefer the date to be on?']
        
        # identify columns that are of type float64
        matrix_cols = {k:v for k,v in row.items() if isinstance(v, float)}

        return cls(name, student_id, gender, seeking, matrix_cols, which_day)


    def matrix_similarity(self, other:'Person')->float:
        """
        Returns the similarity between the two people based on their matrix
        """
        if self==other:
            return 0.0

        common_keys = set(self.matrix.keys()).intersection(set(other.matrix.keys()))
        if len(common_keys) == 0:
            return 0

        vector1 = np.array([self.matrix[k] for k in common_keys])
        vector2 = np.array([other.matrix[k] for k in common_keys])

        # return np.linalg.norm(vector1 - vector2)
        return 1 - cosine(vector1, vector2)

    def is_pairable(self, other:'Person')->bool:
        """
        Returns True if the two people are pairable
        This defines hard constraints that must be satisfied

        A person is pairable if:
            Allow pairing with self
            They are seeking each others' gender
            They can meet on the same day
        """
        if self==other:
            return True
        
        def constraint(func):
            return partial(func, other)

        constraints = [self._gender_seeking_constraint, self._day_preference_constraint]

        return all(map(constraint, constraints))

    def is_pairing_preferred(self, other:'Person')->bool:
        """
        Returns True if the two people are preferred to be paired
        This defines soft constraints that are preferred to be satisfied
        """

    def _gender_seeking_constraint(self, other:'Person')->bool:
        """
        Returns True if the two people are seeking each others
        """
        wanting = self.seeking == Identification.ANY or self.seeking == other.gender
        other_wanting = other.seeking == Identification.ANY or other.seeking == self.gender
        return wanting and other_wanting

    def _day_preference_constraint(self, other:'Person')->bool:
        """
        Returns True if the two people can meet on the same day
        """
        return self.day_choice == other.day_choice or self.day_choice == "Either" or other.day_choice == "Either"