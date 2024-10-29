from typing import Dict, TYPE_CHECKING

from cython_extensions import cy_closest_to
from loguru import logger
from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units

from bot.behaviours.macro.build_structure import BuildStructure
from bot.behaviours.macro.macro_behaviour import MacroBehaviour
from bot.consts import UnitRole
from bot.helpers.structure_helper import RACE_GAS
from bot.jeroen_bot_settings import JeroenBotSettings

if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot


class BuildGas(MacroBehaviour):

    def __init__(self):
        super().__init__()

    def execute(self, ai: "JeroenBot") -> bool:

        if ai.unit_manager.own_structures(UnitTypeId.PYLON).ready.exists:

            gas_building_type = RACE_GAS[JeroenBotSettings.RACE]

            if ai.build_manager.structure_pending(gas_building_type) > 0 or ai.already_pending(gas_building_type) > 0:
                return False

            for expansion in ai.expansion_manager.expansions:
                if not expansion.ready:
                    continue

                geysers: Units = ai.vespene_geyser.filter(lambda g: g.distance_to(expansion.location) < 10)

                for geyser in geysers:

                    gas_buildings_at_geyser = ai.unit_manager.own_gas_buildings.filter(
                        lambda g: g.distance_to(geyser) < 2
                    )

                    if gas_buildings_at_geyser.amount > 0:
                        continue

                    return BuildStructure(gas_building_type, geyser).execute(ai)


        return False