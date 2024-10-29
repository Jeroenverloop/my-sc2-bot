from typing import TYPE_CHECKING

from sc2.position import Point3, Point2
from sc2.unit import Unit
from bot.managers.manager import Manager


if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot


class DebugManager(Manager):

    def __init__(self, bot: "JeroenBot"):
        super().__init__(bot)

    def draw_text_on_world(
            self,
            pos: Point2,
            text: str,
            size: int = 12,
            y_offset: int = 0,
            color=(0, 255, 255),
    ) -> None:  # pragma: no cover

        z_height: float = self.ai.get_terrain_z_height(pos)
        self.ai.client.debug_text_world(
            text,
            Point3((pos.x, pos.y + y_offset, z_height)),
            color=color,
            size=size,
        )