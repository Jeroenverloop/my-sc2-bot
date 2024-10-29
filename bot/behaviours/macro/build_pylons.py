import random
from typing import TYPE_CHECKING, Optional, List

from cython_extensions import cy_distance_to
from loguru import logger
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2
from sc2.unit import Unit

from bot.behaviours.macro.build_structure import BuildStructure
from bot.behaviours.macro.macro_behaviour import MacroBehaviour
from bot.helpers.building_helper import BuildingSize, STRUCTURE_TO_BUILDING_SIZE
from bot.models.expansion import Expansion

if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot


class BuildPylons(MacroBehaviour):

    def __init__(self):
        super().__init__()

    def execute(self, ai: "JeroenBot") -> bool:

        if self.supply_needed(ai) > 0 and ai.townhalls:

            pylon_placement: Optional[Point2] = self._get_pylon_placement(ai)

            if pylon_placement:

                return BuildStructure(UnitTypeId.PYLON, pylon_placement).execute(ai)

        return False

    def _get_pylon_placement(self, ai: "JeroenBot") -> Optional[Point2]:

        expansion: Expansion = random.choice(ai.expansion_manager.expansions)

        position: Point2 = expansion.request_building_placement(
            structure_type=UnitTypeId.PYLON
        )

        return position

    @staticmethod
    def supply_needed(ai: "JeroenBot") -> int:

        building_pylons: int = ai.unit_manager.own_structures(UnitTypeId.PYLON).filter(lambda p: p.build_progress < 1).amount
        pending_pylons: int = ai.build_manager.structure_pending(UnitTypeId.PYLON)

        supply_incoming: int = (building_pylons + pending_pylons) * 8

        supply_left: int = int(ai.supply_left + supply_incoming)
        supply_required: int = 0

        supply_required += ai.unit_manager.own_townhalls.ready.amount*3

        supply_required += ai.unit_manager.own_structures([UnitTypeId.GATEWAY, UnitTypeId.WARPGATE]).ready.amount * 3
        supply_required += ai.unit_manager.own_structures([UnitTypeId.ROBOTICSFACILITY]).ready.amount * 4
        supply_required += ai.unit_manager.own_structures([UnitTypeId.STARGATE]).ready.amount * 5

        return supply_required - supply_left

