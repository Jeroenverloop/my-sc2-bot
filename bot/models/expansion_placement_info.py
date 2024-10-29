from typing import Dict, List, TYPE_CHECKING

import numpy as np
from cython_extensions import cy_get_bounding_box, cy_find_building_locations, cy_distance_to_squared
from loguru import logger
from sc2.position import Point2, Point3

from bot.helpers.building_helper import NOT_BUILDABLE, BuildingSize, BUILDING_SIZE_ENUM_TO_TUPLE

if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot
    from bot.models.expansion import Expansion
from bot.models.placement_position import PlacementPosition


class ExpansionPlacementInfo:

    EMPTY_SPACE_AROUND_NEXUS: int = 9

    def __init__(self, ai: "JeroenBot", expansion: "Expansion"):

        self.ai: "JeroenBot" = ai
        self.expansion: "Expansion" = expansion

        self.points_to_avoid_grid = self.create_avoidance_grid()

        self.max_dist: int = 16
        if self.expansion.location == self.ai.start_location:
            self.max_dist = 22

        self.add_not_buildables_to_avoid_grid()
        self.building_placements = self.get_building_placements()

        #logger.info(self.building_placements)


    def create_avoidance_grid(self):
        return np.zeros(self.ai.terrain_manager.placement_grid.shape, np.uint8)

    def add_not_buildables_to_avoid_grid(self):

        for destructible in self.ai.destructables:
            if destructible.type_id in NOT_BUILDABLE:
                if destructible.distance_to(self.expansion.location) > self.max_dist:
                    continue
                pos: Point2 = destructible.position
                start_x: int = int(pos.x - 1)
                start_y: int = int(pos.y - 1)
                self.points_to_avoid_grid[
                    start_y : start_y + 2, start_x : start_x + 2
                ] = 1

    def get_building_placements(self) -> Dict[BuildingSize, Dict[Point2, PlacementPosition]]:

        building_placements: Dict[BuildingSize, Dict[Point2, PlacementPosition]] = {
            BuildingSize.THREE_BY_THREE: {},
            BuildingSize.TWO_BY_TWO: {}
        }

        start_x: int = int(self.expansion.location.x - 4.5)
        start_y: int = int(self.expansion.location.y - 4.5)
        self.points_to_avoid_grid[start_y: start_y + self.EMPTY_SPACE_AROUND_NEXUS, start_x: start_x + self.EMPTY_SPACE_AROUND_NEXUS] = 1

        area_points: set[tuple[int, int]] = self.ai.terrain_manager.get_flood_fill_area(
            start_point = self.expansion.location,
            max_dist = self.max_dist
        )

        raw_x_bounds: tuple[int,int]
        raw_y_bounds: tuple[int,int]

        raw_x_bounds, raw_y_bounds = cy_get_bounding_box(area_points)

        production_pylon_positions: List[tuple[float,float]] = cy_find_building_locations(
            kernel = np.ones((2, 2), dtype = np.uint8),
            x_stride = 7,
            y_stride = 7,
            x_bounds = raw_x_bounds,
            y_bounds = raw_y_bounds,
            building_width = 2,
            building_height = 2,
            creep_grid = self.ai.terrain_manager.creep_grid,
            placement_grid = self.ai.terrain_manager.placement_grid,
            pathing_grid = self.ai.terrain_manager.pathing_grid,
            points_to_avoid_grid = self.points_to_avoid_grid,
            avoid_creep = True
        )

        for pos in production_pylon_positions:
            x: float = pos[0]
            y: float = pos[1]

            build_pos: Point2 = Point2((x, y))

            if self.ai.get_terrain_height(build_pos) == self.ai.get_terrain_height(self.expansion.location):

                building_placements[BuildingSize.TWO_BY_TWO][build_pos] = self.create_placement_position(production_pylon= True)
                self.add_building_to_avoidance_grid(int(x), int(y), BuildingSize.TWO_BY_TWO)

        three_by_three_positions: list = cy_find_building_locations(
            kernel = np.ones((3, 3), dtype = np.uint8),
            x_stride = 3,
            y_stride = 4,
            x_bounds = raw_x_bounds,
            y_bounds = raw_y_bounds,
            building_width = 3,
            building_height = 3,
            creep_grid = self.ai.terrain_manager.creep_grid,
            placement_grid = self.ai.terrain_manager.placement_grid,
            pathing_grid = self.ai.terrain_manager.pathing_grid,
            points_to_avoid_grid = self.points_to_avoid_grid,
            avoid_creep = True,
        )

        num_found: int = len(three_by_three_positions)

        for i, pos in enumerate(three_by_three_positions):
            # drop some placements to avoid walling in
            if num_found > 6 and i % 4 == 0:
                continue

            x: float = pos[0]
            y: float = pos[1]
            build_pos: Point2 = Point2((x, y))

            if self.ai.get_terrain_height(build_pos) == self.ai.get_terrain_height(self.expansion.location):

                building_placements[BuildingSize.THREE_BY_THREE][build_pos] = self.create_placement_position()
                self.add_building_to_avoidance_grid(int(x), int(y), BuildingSize.THREE_BY_THREE)

        two_by_two_positions = cy_find_building_locations(
            kernel=np.ones((2, 2), dtype=np.uint8),
            x_stride=2,
            y_stride=3,
            x_bounds=raw_x_bounds,
            y_bounds=raw_y_bounds,
            building_width=2,
            building_height=2,
            creep_grid=self.ai.terrain_manager.creep_grid,
            placement_grid=self.ai.terrain_manager.placement_grid,
            pathing_grid=self.ai.terrain_manager.pathing_grid,
            points_to_avoid_grid=self.points_to_avoid_grid,
            avoid_creep=True,
        )

        num_found: int = len(two_by_two_positions)

        for i, pos in enumerate(two_by_two_positions):
            # drop some placements to avoid walling in
            if num_found > 6 and i % 5 == 0:
                continue
            x: float = pos[0]
            y: float = pos[1]
            build_pos: Point2 = Point2((x, y))

            if self.ai.get_terrain_height(build_pos) == self.ai.get_terrain_height(self.expansion.location):

                building_placements[BuildingSize.TWO_BY_TWO][build_pos] = self.create_placement_position()

                self.add_building_to_avoidance_grid(int(x), int(y), BuildingSize.TWO_BY_TWO)

        two_by_twos: Dict[Point2,PlacementPosition] = building_placements[BuildingSize.TWO_BY_TWO]
        three_by_threes: Dict[Point2, PlacementPosition] = building_placements[BuildingSize.THREE_BY_THREE]

        production_pylons: list[Point2] = [
            placement
            for placement in two_by_twos
            if two_by_twos[placement].production_pylon
        ]

        best_pylon_pos: Point2 = self.expansion.location
        most_three_by_threes: int = 0

        for pylon_pos in production_pylons:
            num_three_by_threes: int = 0
            for three_by_three in three_by_threes:
                if cy_distance_to_squared(pylon_pos, three_by_three) < 42.25:
                    num_three_by_threes += 1
            if num_three_by_threes > most_three_by_threes:
                most_three_by_threes = num_three_by_threes
                best_pylon_pos = pylon_pos

        #logger.info(production_pylons)
        if best_pylon_pos in building_placements[BuildingSize.TWO_BY_TWO]:
            building_placements[BuildingSize.TWO_BY_TWO][best_pylon_pos].optimal_pylon = True

        return building_placements


    def add_building_to_avoidance_grid(self, x: int, y: int, building_size: BuildingSize):

        if building_size in BUILDING_SIZE_ENUM_TO_TUPLE:

            size: tuple[int, int] = BUILDING_SIZE_ENUM_TO_TUPLE[building_size]

            y_start = int(y - (size[1] / 2))
            x_start = int(x - (size[0] / 2))
            self.points_to_avoid_grid[y_start: y_start + size[1], x_start: x_start+ size[0]] = 1

    def create_placement_position(
        self,
        production_pylon: bool = False,
        wall: bool = False,
        bunker: bool = False,
        optimal_pylon: bool = False,
    ) -> PlacementPosition:

        return PlacementPosition(
            available = True,
            has_addon = False,
            is_wall = wall,
            building_tag = 0,
            worker_on_route = False,
            time_requested = 0.0,
            production_pylon = production_pylon,
            bunker = bunker,
            optimal_pylon = optimal_pylon,
        )

    async def draw_building_placements(self):
        """Draw all found building placements.

        Debug and DebugOptions.ShowBuildingFormation should be True in config to enable.
        """
        for a in self.building_placements.items():


            building_size: BuildingSize = a[0]
            draw_size: tuple[int,int] = BUILDING_SIZE_ENUM_TO_TUPLE[building_size]
            placements_dict: Dict[Point2, PlacementPosition] = a[1]

            z = self.ai.get_terrain_height(self.expansion.location)
            z = -16 + 32 * z / 255

            for b in placements_dict.items():

                position: Point2 = b[0]
                placement_position: PlacementPosition = b[1]
                self.ai.debug_manager.draw_text_on_world(position, f"{position}")

                x_division = draw_size[0]/2
                y_division = draw_size[1]/2

                pos_min = Point3((position.x - x_division, position.y - y_division, z))
                pos_max = Point3((position.x + x_division, position.y + y_division, z + 2))
                if placement_position.available:
                    colour = Point3((0, 255, 0))
                else:
                    colour = Point3((255, 0, 0))
                self.ai.client.debug_box_out(pos_min, pos_max, colour)
