from typing import TYPE_CHECKING

from sc2.unit import Unit
from bot.managers.manager import Manager


if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot


class ExampleManager(Manager):

    def __init__(self, bot: "JeroenBot"):
        super().__init__(bot)

    def on_start(self):
        pass

    def on_step(self, iteration: int):
        pass

    def on_unit_created(self, unit: Unit):
        pass

    def on_unit_destroyed(self, unit_tag: int):
        pass