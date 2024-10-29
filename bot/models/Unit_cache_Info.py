from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2
from sc2.unit import Unit


class UnitCacheInfo:

    def __init__(self, unit: Unit, last_seen: float):
        self.unit_type: UnitTypeId = unit.type_id
        self.position: Point2 = unit.position
        self.last_seen: float = last_seen

    def update(self, unit: Unit, time: float):
        self.position = unit.position
        self.last_seen = time