from typing import TYPE_CHECKING, Optional

from typing import TypeVar

from loguru import logger

T = TypeVar('T')

from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit

from bot.managers.build_manager import BuildManager
from bot.managers.debug_manager import DebugManager
from bot.managers.expansion_manager import ExpansionManager
from bot.managers.manager import Manager
from bot.managers.path_manager import PathManager
from bot.managers.resource_manager import ResourceManager
from bot.managers.role_manager import RoleManager
from bot.managers.tech_manager import TechManager
from bot.managers.terrain_manager import TerrainManager
from bot.managers.unit_manager import UnitManager

if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot


class Hub:

    def __init__(self, ai: "JeroenBot"):
        self.ai = ai

        self._role_manager: RoleManager = RoleManager(self.ai)
        self._resource_manager: ResourceManager = ResourceManager(self.ai)
        self._path_manager: PathManager = PathManager(self.ai)
        self._build_manager: BuildManager = BuildManager(self.ai)
        self._expansion_manager: ExpansionManager = ExpansionManager(self.ai)
        self._tech_manager: TechManager = TechManager(self.ai)
        self._terrain_manager: TerrainManager = TerrainManager(self.ai)
        self._debug_manager: DebugManager = DebugManager(self.ai)
        self._unit_manager: UnitManager = UnitManager(self.ai)

        self._managers: list[Manager] = [
            self._unit_manager,
            self._terrain_manager,
            self._expansion_manager,
            self._role_manager,
            self._resource_manager,
            self._path_manager,
            self._build_manager,
            self._tech_manager,
            self._debug_manager,
        ]

        self._manager_dict = {}

    def __call__(self, manager_name: str) -> Optional[T]:

        if manager_name in self._manager_dict:
            return self._manager_dict[manager_name]

        for manager in self._managers:
            if manager.__class__.__name__ == manager_name:
                self._manager_dict[manager_name] = manager
                return manager
        return None

    async def on_start(self):
        for manager in self._managers:
            await manager.on_start()

    async def on_step(self, iteration):
        for manager in self._managers:
            await manager.on_step(iteration)

    async def on_unit_created(self, unit):
        for manager in self._managers:
            await manager.on_unit_created(unit)

    async def on_unit_destroyed(self, unit_tag):
        for manager in self._managers:
            await manager.on_unit_destroyed(unit_tag)

    async def on_building_construction_started(self, unit: Unit):
        for manager in self._managers:
            await manager.on_building_construction_started(unit)

    async def on_building_construction_complete(self, unit: Unit) -> None:
        for manager in self._managers:
            await manager.on_building_construction_complete(unit)

    async def on_unit_took_damage(self, unit: Unit, damage: float) -> None:
        for manager in self._managers:
            await manager.on_unit_took_damage(unit, damage)

    async def on_enemy_unit_entered_vision(self, unit: Unit):
        for manager in self._managers:
            await manager.on_enemy_unit_entered_vision(unit)

    async def on_enemy_unit_left_vision(self, unit_tag: int):
        for manager in self._managers:
            await manager.on_enemy_unit_left_vision(unit_tag)

    async def on_unit_type_changed(self, unit: Unit, previous_type: UnitTypeId):
        for manager in self._managers:
            await manager.on_unit_type_changed(unit, previous_type)

