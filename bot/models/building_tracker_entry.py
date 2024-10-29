from typing import Union

from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2
from sc2.unit import Unit


class BuildingTrackerEntry:

    def __init__(self, unit_type: UnitTypeId, target: Union[Unit,Point2], time_commenced: float):
        self.unit_type: UnitTypeId = unit_type
        self.target: Union[Unit,Point2] = target
        self.time_commenced: float = time_commenced
