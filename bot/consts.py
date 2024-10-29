from enum import Enum

class UnitValueType(Enum):
    Percentage = 1
    Amount = 2


class UnitRole(str, Enum):
    IDLE = "IDLE"
    GATHERING = "GATHERING"
    BUILDING = "BUILDING"
    BUILDER = "BUILDER"
    ATTACKING = "ATTACKING"