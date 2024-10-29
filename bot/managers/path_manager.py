from typing import TYPE_CHECKING, List, Optional

from map_analyzer import MapData
from sc2.position import Point2
from sc2.unit import Unit
from bot.managers.manager import Manager
import numpy as np

if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot

class PathManager(Manager):

    def __init__(self, ai: "JeroenBot"):
        super().__init__(ai)