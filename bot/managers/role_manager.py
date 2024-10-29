import math
from typing import Dict, Set, List, Optional

from loguru import logger
from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units

from bot.consts import UnitRole
from bot.managers.manager import Manager


class RoleManager(Manager):

    first: bool = True

    def __init__(self, bot):
        super().__init__(bot)

        self.unit_roles: Dict[str, Set[int]] = {
            role.name: set() for role in UnitRole
        }

    async def on_step(self, iteration):

        #if we have workers without a role set them GATHERING
        for worker in self.ai.unit_manager.own_workers:
            if not self.has_role(worker.tag):
                self.assign_role(worker.tag, UnitRole.GATHERING)


    async def on_unit_destroyed(self, unit_tag: int):
        self.remove_unit_from_role(unit_tag)
    

    def assign_role(self, unit_tag: int, role: UnitRole):
        self.remove_unit_from_role(unit_tag)
        self.unit_roles[role.name].add(unit_tag)
        #logger.info(f"Assigned {role.name} to {unit_tag}")

    def remove_unit_from_role(self, unit_tag: int):
        
        for role in self.unit_roles:
            if unit_tag in self.unit_roles[role]:
                self.unit_roles[role].remove(unit_tag)
                return

    def has_role(self, unit_tag: int) -> bool:
        for role in self.unit_roles:
            if unit_tag in self.unit_roles[role]:
                return True
        return False

    def get_unit_tags_by_role(self, role: UnitRole) -> Set[int]:
        return self.unit_roles.get(role.name, set())

    def get_unit_tags_by_roles(self, roles: Set[UnitRole]) -> Set[int]:

        all_tags: Set[int] = set()

        for role in roles:
            tags: Set[int] = self.get_unit_tags_by_role(role)
            all_tags.update(tags)

        return all_tags

    def get_units_by_role(self, role: UnitRole, unit_type: Optional[UnitTypeId] = None) -> Units:

        return self._get_units_from_tags(
            unit_tags = self.get_unit_tags_by_role(role),
            unit_type = unit_type
        )

    def get_units_by_roles(self, roles: Set[UnitRole], unit_type: Optional[UnitTypeId] = None) -> Units:

        return self._get_units_from_tags(
            unit_tags = self.get_unit_tags_by_roles(roles),
            unit_type = unit_type
        )

    def _get_units_from_tags(self, unit_tags: Set[int], unit_type: Optional[UnitTypeId] = None) -> Units:
        if not unit_tags:
            return Units([], self.ai)

        if unit_type:
            return self.ai.all_own_units.filter(lambda u: u.tag in unit_tags and u.type_id == unit_type)

        return self.ai.all_own_units.filter(lambda u: u.tag in unit_tags)


