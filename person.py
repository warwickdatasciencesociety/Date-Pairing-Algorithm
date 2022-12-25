from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Tuple, Union
import pandas as pd
import numpy as np

class Identification(Enum):
    MAN = "MAN"
    WOMAN = "WOMAN"
    ANY = "ANY"
    UNDEFINED = "UNDEFINED"

    @classmethod
    def from_string(cls:'Identification', s: str)->'Identification':
        s = s.upper()

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
            return -1.0

        common_keys = set(self.matrix.keys()).intersection(set(other.matrix.keys()))
        if len(common_keys) == 0:
            return 0

        vector1 = np.array([self.matrix[k] for k in common_keys])
        vector2 = np.array([other.matrix[k] for k in common_keys])

        return np.linalg.norm(vector1 - vector2)

    def is_pairable(self, other:'Person')->bool:
        """
        Returns True if the two people are pairable

        A person is pairable if:
        They are seeking each others' gender
        """
        if self==other:
            return True
        
        wanting = self.seeking == Identification.ANY or self.seeking == other.gender
        other_wanting = other.seeking == Identification.ANY or other.seeking == self.gender
        gender_preference = wanting and other_wanting


        day_preference = self.day_choice == other.day_choice or self.day_choice == "Either" or other.day_choice == "Either"

        return day_preference and gender_preference
        # return gender_preference