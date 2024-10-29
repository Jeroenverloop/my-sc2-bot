from abc import ABCMeta
from typing import TYPE_CHECKING

from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit


if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot

class Manager(metaclass=ABCMeta):

    def __init__(self, ai: "JeroenBot"):
        self.ai = ai

    async def on_start(self):
        pass

    async def on_step(self, iteration: int):
        pass

    async def on_unit_created(self, unit: Unit):
        pass

    async def on_unit_destroyed(self, unit_tag: int):
        pass

    async def on_building_construction_started(self, unit: Unit):
        pass

    async def on_building_construction_complete(self, unit: Unit) -> None:
        pass

    async def on_unit_took_damage(self, unit: Unit, damage: float) -> None:
        pass

    async def on_enemy_unit_entered_vision(self, unit: Unit):
        pass

    async def on_enemy_unit_left_vision(self, unit_tag: int):
        pass

    async def on_unit_type_changed(self, unit: Unit, previous_type: UnitTypeId):
        pass


