from sc2.ids.unit_typeid import UnitTypeId

from bot.consts import UnitValueType


class UnitCompositionConfiguration:

    def __init__(self, unit_type: UnitTypeId, value:int, value_type:UnitValueType, priority:int):
        self.unit_type = unit_type
        self.value = value
        self.value_type = value_type
        self.priority = priority
