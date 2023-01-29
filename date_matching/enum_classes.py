from enum import Enum


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
