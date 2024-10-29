from typing import Dict, TYPE_CHECKING, Set, Union

from loguru import logger
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units

from bot.behaviours.macro.macro_behaviour import MacroBehaviour
from bot.helpers.upgrade_helper import UNIT_BENEFITTING_UPGRADES, STRUCTURE_NEEDED_FOR_UPGRADE
from bot.jeroen_bot_settings import JeroenBotSettings

if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot


class BuildStructure(MacroBehaviour):

    def __init__(self, structure_type: UnitTypeId, target: Union[Point2, Unit]):
        super().__init__()

        self.structure_type = structure_type
        self.position = target.position if isinstance(target, Unit) else target
        self.target = target

    def execute(self, ai: "JeroenBot") -> bool:

        builder = ai.build_manager.get_builder(self.position)

        if ai.build_manager.can_start_build_order(self.structure_type, self.position, builder):

            ai.build_manager.build_with_specific_worker(
                builder,
                self.structure_type,
                self.target
            )
            return True

        return False
