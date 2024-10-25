from random import randrange
from typing import Dict, TYPE_CHECKING

from cython_extensions import cy_closest_to
from loguru import logger
from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit

from bot.behaviours.macro.macro_behaviour import MacroBehaviour

if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot


class BuildPylons(MacroBehaviour):

    def __init__(self):
        super().__init__()

    def execute(self, ai: "JeroenBot"):

        if self.supply_needed(ai) > 0:
            if ai.can_afford(UnitTypeId.PYLON) and ai.townhalls:

                position = ai.townhalls.random.position.random_on_distance(randrange(1,8)).towards(ai.enemy_start_locations[0], 8)

                builder: Unit = ai.hub.build_manager.get_builder(position)

                if builder:
                    builder.build(UnitTypeId.PYLON, position)
                    builder.stop(queue=True)
                    return

    @staticmethod
    def supply_needed(ai: "JeroenBot") -> int:

        supply_left: int = int(ai.supply_left + (ai.already_pending(UnitTypeId.PYLON)*8))
        supply_required: int = 0

        supply_required += ai.townhalls.ready.amount*3

        return supply_required - supply_left

