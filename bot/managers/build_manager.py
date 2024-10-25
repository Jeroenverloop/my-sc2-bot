from typing import TYPE_CHECKING, Optional

from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units

from bot.consts import UnitRole
from bot.managers.manager import Manager


if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot


class BuildManager(Manager):

    def __init__(self, ai: "JeroenBot"):
        super().__init__(ai)

    def on_start(self):
        pass

    def on_step(self, iteration: int):
        pass

    def on_unit_created(self, unit: Unit):
        pass

    def on_unit_destroyed(self, unit_tag: int):
        pass

    def get_builder(self, position:Point2) -> Optional[Unit]:

        builders: Units = self.hub.role_manager.get_units_by_role(UnitRole.BUILDER, UnitTypeId.PROBE).idle

        if builders:
            return builders.closest_to(position)

        miners: Units = self.hub.role_manager.get_units_by_role(UnitRole.GATHERING, UnitTypeId.PROBE)

        if miners:
            miner: Unit = miners.closest_to(position)
            if miner.tag in self.hub.resource_manager.worker_to_geyser_dict:
                self.hub.resource_manager.remove_worker_from_vespene(miner.tag)
            elif miner.tag in self.hub.resource_manager.worker_to_mineral_patch_dict:
                self.hub.resource_manager.remove_worker_from_mineral(miner.tag)

            self.hub.role_manager.assign_role(miner.tag, UnitRole.BUILDER)
            return miner



