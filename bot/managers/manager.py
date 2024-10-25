from abc import abstractmethod, ABCMeta
from typing import TYPE_CHECKING

from sc2.unit import Unit


if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot
    from bot.managers.hub import Hub

class Manager(metaclass=ABCMeta):

    @property
    def hub(self) -> "Hub":
        return self.ai.hub

    def __init__(self, ai: "JeroenBot"):
        self.ai = ai

    @abstractmethod
    def on_start(self):
        pass

    @abstractmethod
    def on_step(self, iteration: int):
        pass

    @abstractmethod
    def on_unit_created(self, unit: Unit):
        pass

    @abstractmethod
    def on_unit_destroyed(self, unit_tag: int):
        pass


