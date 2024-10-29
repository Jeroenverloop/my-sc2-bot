from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot


class Behaviour:


    @abstractmethod
    def execute(self, ai: "JeroenBot") -> bool:
        return True