from enum import Enum


class UnitRole(str, Enum):
    IDLE = "IDLE"
    GATHERING = "GATHERING"
    BUILDING = "BUILDING"
    BUILDER = "BUILDER"
    ATTACKING = "ATTACKING"