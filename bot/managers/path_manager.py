from typing import TYPE_CHECKING, List

from map_analyzer import MapData
from sc2.position import Point2
from sc2.unit import Unit
from bot.managers.manager import Manager
import numpy as np

if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot

class PathManager(Manager):

    map_data: MapData
    ground_grid: np.ndarray
    air_grid: np.ndarray

    def __init__(self, ai: "JeroenBot"):
        super().__init__(ai)

    def on_start(self):

        self.map_data = MapData(self.ai, arcade=False)
        self.ground_grid = self.map_data.get_pyastar_grid()
        self.air_grid = self.map_data.get_clean_air_grid()
        pass

    def on_step(self, iteration: int):
        pass
    
    def on_unit_created(self, unit: Unit):
        pass

    def on_unit_destroyed(self, unit_tag: int):
        pass


    def find_next_point_in_path(self, start:Point2, goal:Point2, grid: np.ndarray, sensitivity: int = 5, smoothing: bool = True) -> Point2:

        path: List[Point2] = self.map_data.pathfind(
            start, goal, grid, sensitivity=sensitivity, smoothing=smoothing
        )

        if not path or len(path) == 0:
            return goal
        else:
            return path[0]