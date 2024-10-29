import random
from typing import Dict, TYPE_CHECKING, Set, Union, Optional

from loguru import logger
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units

from bot.behaviours.macro.build_structure import BuildStructure
from bot.behaviours.macro.macro_behaviour import MacroBehaviour
from bot.helpers.structure_helper import REQUIRE_POWER_STRUCTURE_TYPES
from bot.helpers.upgrade_helper import UNIT_BENEFITTING_UPGRADES, STRUCTURE_NEEDED_FOR_UPGRADE, UPGRADE_RESEARCHED_FROM
from bot.jeroen_bot_settings import JeroenBotSettings
from bot.models.expansion import Expansion

if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot


class UpgradeController(MacroBehaviour):

    def __init__(self):
        super().__init__()

    def execute(self, ai: "JeroenBot"):

        if not ai.unit_manager.own_structures(UnitTypeId.CYBERNETICSCORE).ready.exists:
            return False

        if not ai.tech_manager.has_upgrade(UpgradeId.WARPGATERESEARCH):
            if ai.resource_manager.can_afford(UpgradeId.WARPGATERESEARCH):
                ai.unit_manager.own_structures(UnitTypeId.CYBERNETICSCORE).ready.first.research(UpgradeId.WARPGATERESEARCH)
                return True
            return False

        for unit_type in ai.army_composition.unit_config_dict:

            if ai.unit_manager.own_army(unit_type).amount < 1:
               continue

            if unit_type in UNIT_BENEFITTING_UPGRADES:

                upgrades: Set[UpgradeId] = UNIT_BENEFITTING_UPGRADES[unit_type]

                for upgrade in upgrades:

                    if ai.tech_manager.has_upgrade(upgrade):
                        continue

                    next_tech: Union[UnitTypeId,UpgradeId] = ai.tech_manager.get_next_tech(upgrade)

                    if isinstance(next_tech, UnitTypeId):

                        if ai.tech_manager.structure_exists(next_tech):
                            continue

                        position: Point2 = self._get_structure_placement(ai, next_tech)
                        if position:
                            if BuildStructure(next_tech, position).execute(ai):
                                logger.info(f"NEXT_TECH STRUCTURE BUILD FOR: {upgrade} is {next_tech.name}")
                                return True

                        return False

                    else:

                        if next_tech in STRUCTURE_NEEDED_FOR_UPGRADE and ai.resource_manager.can_afford(next_tech):
                            structure_type: UnitTypeId = STRUCTURE_NEEDED_FOR_UPGRADE[next_tech]

                            if not ai.unit_manager.own_structures(structure_type).ready.exists:
                                continue

                            if not next_tech in UPGRADE_RESEARCHED_FROM:
                                continue

                            production_building_type: UnitTypeId = UPGRADE_RESEARCHED_FROM[next_tech]

                            logger.info(f"NEXT TECH: {next_tech} build from {production_building_type}")

                            for unit in ai.unit_manager.own_structures(production_building_type).ready:
                                if unit.orders:
                                    logger.info(unit.orders[0].ability.id)


                            available_structures: Units = ai.unit_manager.own_structures(production_building_type).ready.idle
                            if available_structures.amount == 0:

                                if (
                                    ai.resource_manager.can_afford(production_building_type)
                                    and ai.build_manager.structure_pending(production_building_type) == 0
                                    and ai.already_pending(production_building_type) == 0
                                ):
                                    position: Point2 = self._get_structure_placement(ai, production_building_type)
                                    if position:
                                        return BuildStructure(production_building_type, position).execute(ai)
                                else:
                                    continue
                            else:
                                selected_structure: Unit = available_structures.random
                                selected_structure.research(next_tech)
                                return True


    def _get_structure_placement(self, ai: "JeroenBot", structure_type:UnitTypeId) -> Optional[Point2]:

        expansion: Expansion = random.choice(ai.expansion_manager.expansions)

        needs_power = structure_type in REQUIRE_POWER_STRUCTURE_TYPES

        position: Point2 = expansion.request_building_placement(
            structure_type=structure_type,
            within_psionic_matrix=needs_power
        )

        return position

