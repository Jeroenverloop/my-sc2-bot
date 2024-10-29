from typing import List, Dict

from sc2.ids.unit_typeid import UnitTypeId

from bot.models.unit_composition_configuration import UnitCompositionConfiguration


class ArmyComposition:

    def __init__(self, unit_config_dict: Dict[UnitTypeId, UnitCompositionConfiguration]):
        self.unit_config_dict: Dict[UnitTypeId, UnitCompositionConfiguration] = unit_config_dict
