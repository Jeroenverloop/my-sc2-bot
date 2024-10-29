from typing import TYPE_CHECKING

from bot.managers.manager import Manager


if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot


class ExampleManager(Manager):

    def __init__(self, bot: "JeroenBot"):
        super().__init__(bot)