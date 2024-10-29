from typing import TYPE_CHECKING

from bot.behaviours.behaviour import Behaviour

if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot


class MacroBehaviour(Behaviour):

    def __init__(self):
        super().__init__()


    def execute(self, ai: "JeroenBot") -> bool:
        return True