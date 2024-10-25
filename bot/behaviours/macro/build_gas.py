from typing import Dict, TYPE_CHECKING

from cython_extensions import cy_closest_to
from loguru import logger
from sc2.ids.unit_typeid import UnitTypeId
from sc2.units import Units

from bot.behaviours.macro.macro_behaviour import MacroBehaviour
from bot.consts import UnitRole
from bot.jeroen_bot_settings import JeroenBotSettings

if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot


class BuildGas(MacroBehaviour):

    def __init__(self):
        super().__init__()

    def execute(self, ai: "JeroenBot"):

        if ai.can_afford(UnitTypeId.ASSIMILATOR):
            for nexus in ai.townhalls.ready:
                geysers: Units = ai.vespene_geyser.filter(lambda g: g.distance_to(nexus) < 10)

                for geyser in geysers:
                    if ai.gas_buildings and cy_closest_to(geyser.position, ai.gas_buildings).distance_to(geyser) < 1:
                        continue

                    builder = ai.hub.build_manager.get_builder(geyser.position)

                    logger.info(f"{builder}")

                    if builder:
                        builder.build_gas(geyser)
                        builder.stop(queue=True)
                        return

