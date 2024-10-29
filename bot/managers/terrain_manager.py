from typing import TYPE_CHECKING, Optional, List, Set, Union

import numpy as np
from cython_extensions import cy_flood_fill_grid, cy_distance_to_squared, cy_can_place_structure, cy_distance_to
from map_analyzer import MapData
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units

from bot.helpers.building_helper import STRUCTURE_TO_BUILDING_SIZE, BuildingSize, BUILDING_SIZE_ENUM_TO_RADIUS, \
    BUILDING_SIZE_ENUM_TO_TUPLE
from bot.helpers.structure_helper import GAS_BUILDINGS
from bot.managers.manager import Manager


if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot


class TerrainManager(Manager):

    def __init__(self, bot: "JeroenBot"):
        super().__init__(bot)

        self._map_data: Optional[MapData] = None
        self._ground_grid: Optional[np.ndarray] = None
        self._air_grid: Optional[np.ndarray] = None

        self.choke_points: Set[Point2] = set()


    async def on_start(self):

        self._map_data = MapData(self.ai, arcade=False)
        self._ground_grid = self._map_data.get_pyastar_grid()
        self._air_grid = self._map_data.get_clean_air_grid()

        self.choke_points = set(
            [
                point
                for ch in self._map_data.map_chokes
                for point in ch.points
            ]
        )

    def get_terrain_height(self, pos: Union[Point2, Unit]):
        return self.ai.get_terrain_height(pos)

    def find_next_point_in_path(self, start: Point2, goal: Point2, grid: np.ndarray, sensitivity: int = 5, smoothing: bool = True) -> Point2:
        return self.find_path(start, goal, grid, sensitivity, smoothing)[0]


    def find_path(self, start:Point2, goal:Point2, grid: np.ndarray, sensitivity: int = 5, smoothing: bool = True) -> List[Point2]:

        path: List[Point2] = self.map_data.pathfind(
            start, goal, grid, sensitivity=sensitivity, smoothing=smoothing
        )

        if not path or len(path) == 0:
            return [goal]
        else:
            return path

    def calculate_path_distance(self, start: Point2, path: List[Point2]) -> float:
        path_dist: float = 0
        for i, p in enumerate(path):
            if i == 0:
                path_dist += cy_distance_to(start, p)
            path_dist += cy_distance_to(p, path[i - 1])
        return path_dist

    def get_flood_fill_area(self, start_point: Point2, max_dist: int = 25):
        """
        Given a point, flood fill outward from it and return the valid points.
        Does not continue through chokes.
        """

        return cy_flood_fill_grid(
            start_point=start_point.rounded,
            terrain_grid=self.terrain_height,
            pathing_grid=self.pathing_grid,
            max_distance=max_dist,
            cutoff_points=self.choke_points
        )

    def can_place_structure(
        self, position: Point2, structure_type: UnitTypeId, avoid_creep:bool = True, include_addon: bool = False
    ) -> bool:
        """Check if structure can be placed at a given position.

        Faster cython alternative to `python-sc2` `await self.can_place()`

        Parameters
        ----------
        avoid_creep: bool
            Do we avoid creep when placing structure
        position : Point2
            The intended building position.
        structure_type : UnitID
            Structure we are trying to place.
        include_addon : bool, optional
            For Terran structures, check addon will place too.

        Returns
        ----------
        bool :
            Indicating if structure can be placed at given position.
        """
        assert structure_type in STRUCTURE_TO_BUILDING_SIZE, (
            f"{structure_type}, " f"not present in STRUCTURE_TO_BUILDING_SIZE dict"
        )

        if structure_type in GAS_BUILDINGS:
            pos: Point2 = position.position
            existing_gas_buildings: Units = self.ai.all_units.filter(
                lambda u: u.type_id in GAS_BUILDINGS
                          and cy_distance_to_squared(pos, u.location) < 12.25
            )
            return len(existing_gas_buildings) == 0

        size: BuildingSize = STRUCTURE_TO_BUILDING_SIZE[structure_type]
        offset: float = BUILDING_SIZE_ENUM_TO_RADIUS[size]
        origin_x: int = int(position[0] - offset)
        origin_y: int = int(position[1] - offset)

        size: tuple[int, int] = BUILDING_SIZE_ENUM_TO_TUPLE[size]
        return cy_can_place_structure(
            (origin_x, origin_y),
            size,
            self.creep_grid,
            self.placement_grid,
            self.pathing_grid,
            avoid_creep=avoid_creep,
            include_addon=include_addon,
        )

    @property
    def map_data(self) -> MapData:
        return self._map_data

    @property
    def terrain_height(self) -> np.ndarray:
        return self.ai.game_info.terrain_height.data_numpy.T

    @property
    def ground_grid(self) -> np.ndarray:
        return self._ground_grid

    @property
    def air_grid(self) -> np.ndarray:
        return self._air_grid

    @property
    def creep_grid(self) -> np.ndarray:
        return self.ai.state.creep.data_numpy

    @property
    def placement_grid(self) -> np.ndarray:
        return self.ai.game_info.placement_grid.data_numpy

    @property
    def pathing_grid(self) -> np.ndarray:
        return self.ground_grid.astype(np.uint8).T
