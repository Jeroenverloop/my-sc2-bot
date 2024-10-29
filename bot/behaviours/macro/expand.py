import sys
from random import randrange
from typing import Dict, TYPE_CHECKING, List, Tuple

from cython_extensions import cy_closest_to
from loguru import logger
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units

from bot.behaviours.macro.build_structure import BuildStructure
from bot.behaviours.macro.macro_behaviour import MacroBehaviour
from bot.jeroen_bot_settings import JeroenBotSettings
from bot.managers.expansion_manager import ExpansionManager
from bot.models.expansion import Expansion

if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot


class Expand(MacroBehaviour):

    def __init__(self):
        super().__init__()

    def execute(self, ai: "JeroenBot") -> bool:

        if self.expansions_needed(ai, ai.expansion_manager.expansions) > 0:

            expansion_locations: List[Tuple[Point2,float]] = ai.expansion_manager.get_expansion_locations()

            if expansion_locations:

                expansion_location: Point2 = expansion_locations[0][0]

                if BuildStructure(ai.race_townhall_base, expansion_location).execute(ai):
                    ai.expansion_manager.create_expansion(expansion_location)
                    return True

        return False

    @staticmethod
    def expansions_needed(ai: "JeroenBot", expansions: List[Expansion]) -> int:

        total_minerals: int = 0
        total_gas: int = 0

        #logger.info(f"total expansions: {len(expansions)}")

        for expansion in expansions:
            total_minerals += expansion.get_remaining_minerals()
            total_gas += expansion.get_remaining_gas()


        #logger.info(f"total minerals: {total_minerals}: total gas: {total_gas}")

        if total_gas < JeroenBotSettings.EXPAND_WHEN_GAS_LEFT or total_minerals < JeroenBotSettings.EXPAND_WHEN_MINERALS_LEFT:
            return 1

        bases_wanted: int = 1 + int((ai.workers.amount + 12) / 22)
        base_count: int = len(expansions)

        return bases_wanted - base_count
