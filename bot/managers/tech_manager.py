from typing import TYPE_CHECKING, Union, List

from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.unit import Unit

from bot.helpers.structure_helper import STRUCTURES, STRUCTURE_NEEDED_FOR_STRUCTURE
from bot.helpers.unit_helper import UNITS, STRUCTURE_NEEDED_FOR_UNIT
from bot.helpers.upgrade_helper import UPGRADE_NEEDED_FOR_UPGRADE, STRUCTURE_NEEDED_FOR_UPGRADE
from bot.managers.manager import Manager


if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot


class TechManager(Manager):

    def __init__(self, bot: "JeroenBot"):
        super().__init__(bot)

    def get_tech_requirements(self, tech: Union[UnitTypeId,UpgradeId], needed_tech: List[Union[UnitTypeId, UpgradeId]]) -> List[Union[UnitTypeId, UpgradeId]]:

        if isinstance(tech, UpgradeId):

            if tech in UPGRADE_NEEDED_FOR_UPGRADE:
                upgrade: UpgradeId = UPGRADE_NEEDED_FOR_UPGRADE[tech]
                if not upgrade in needed_tech:
                    needed_tech.append(UPGRADE_NEEDED_FOR_UPGRADE[tech])
                    needed_tech = self.get_tech_requirements(upgrade, needed_tech)

            if tech in STRUCTURE_NEEDED_FOR_UPGRADE:
                structure: UnitTypeId = STRUCTURE_NEEDED_FOR_UPGRADE[tech]
                if not structure in needed_tech:
                    needed_tech.append(STRUCTURE_NEEDED_FOR_UPGRADE[tech])
                    needed_tech = self.get_tech_requirements(structure, needed_tech)

        elif isinstance(tech, UnitTypeId):

            if tech in STRUCTURES:
                if tech in STRUCTURE_NEEDED_FOR_STRUCTURE:
                    structure: UnitTypeId = STRUCTURE_NEEDED_FOR_STRUCTURE[tech]
                    if not structure in needed_tech:
                        needed_tech.append(structure)
                        needed_tech = self.get_tech_requirements(structure, needed_tech)
            elif tech in UNITS:
                if tech in STRUCTURE_NEEDED_FOR_UNIT:
                    structure: UnitTypeId = STRUCTURE_NEEDED_FOR_UNIT[tech]
                    if not structure in needed_tech:
                        needed_tech.append(structure)
                        needed_tech = self.get_tech_requirements(structure, needed_tech)

        return needed_tech

    def get_needed_tech(self, tech: Union[UnitTypeId, UpgradeId]) -> List[Union[UnitTypeId, UpgradeId]]:

        tech_requirements: List[Union[UnitTypeId, UpgradeId]] = self.get_tech_requirements(tech, [])

        needed_tech: List[Union[UnitTypeId, UpgradeId]] = []

        for tech_requirement in tech_requirements:
            if isinstance(tech_requirement, UpgradeId):
                if not self.has_upgrade(tech_requirement):
                    needed_tech.append(tech_requirement)
            elif isinstance(tech_requirement, UnitTypeId):
                if not self.is_structure_ready(tech_requirement):
                    needed_tech.append(tech_requirement)

        return needed_tech

    def get_next_tech(self, asked_tech: Union[UnitTypeId, UpgradeId]) -> List[Union[UnitTypeId, UpgradeId]]:

        needed_tech = self.get_needed_tech(asked_tech)

        tech_list: List[Union[UnitTypeId, UpgradeId]] = []

        if needed_tech:
            for tech in needed_tech:
                needed_tech_for_tech = self.get_needed_tech(tech)
                if not needed_tech_for_tech:
                    tech_list.append(tech)

            return tech_list
        else:
            return []



    def is_structure_ready(self, structure: UnitTypeId) -> bool:
        return self.ai.unit_manager.own_structures(structure).ready.exists

    def structure_exists(self, structure: UnitTypeId) -> bool:
        return (
                self.ai.unit_manager.own_structures(structure).exists
                or self.ai.build_manager.structure_pending(structure) > 0
        )

    def has_upgrade(self, upgrade: UpgradeId) -> bool:
        return upgrade in self.ai.state.upgrades