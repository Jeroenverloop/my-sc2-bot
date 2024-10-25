from typing import TYPE_CHECKING

from bot.managers.build_manager import BuildManager
from bot.managers.manager import Manager
from bot.managers.path_manager import PathManager
from bot.managers.resource_manager import ResourceManager
from bot.managers.role_manager import RoleManager

if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot


class Hub:

    def __init__(self, ai: "JeroenBot"):
        self.ai = ai

        self.role_manager: RoleManager = RoleManager(self.ai)
        self.resource_manager: ResourceManager = ResourceManager(self.ai)
        self.path_manager: PathManager = PathManager(self.ai)
        self.build_manager: BuildManager = BuildManager(self.ai)

        self.managers: list[Manager] = [
            self.role_manager,
            self.resource_manager,
            self.path_manager,
            self.build_manager
        ]

    def on_start(self):
        for manager in self.managers:
            manager.on_start()

    def on_step(self, iteration):
        for manager in self.managers:
            manager.on_step(iteration)

    def on_unit_created(self, unit):
        for manager in self.managers:
            manager.on_unit_created(unit)

    def on_unit_destroyed(self, unit_tag):
        for manager in self.managers:
            manager.on_unit_destroyed(unit_tag)

