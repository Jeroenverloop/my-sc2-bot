from typing import TYPE_CHECKING, Optional, Dict, List

from cython_extensions import cy_pylon_matrix_covers, cy_distance_to_squared
from loguru import logger
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units

from bot.consts import UnitRole
from bot.helpers.building_helper import BuildingSize, STRUCTURE_TO_BUILDING_SIZE
from bot.managers.resource_manager import ResourceManager
from bot.managers.role_manager import RoleManager
from bot.models.expansion_placement_info import ExpansionPlacementInfo
from bot.models.placement_position import PlacementPosition

if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot


class Expansion:

    def __init__(self, ai: "JeroenBot", location: Point2):
        self.ai: "JeroenBot" = ai
        logger.info(f"New expansion @ {location}")
        self.townhall: Unit = None
        self.location: Point2 = location
        self.terrain_height: float = ai.terrain_manager.get_terrain_height(location)

        self.placement_info: ExpansionPlacementInfo = ExpansionPlacementInfo(ai, self)

    def get_remaining_minerals(self) -> int:
        return self.resource_manager.get_total_minerals_at_position(self.location)

    def get_remaining_gas(self) -> int:
        return self.resource_manager.get_total_gas_at_position(self.location)

    def get_assigned_workers(self) -> Units:

        assigned_workers: Units = Units([], self.ai)

        if not self.townhall:
            return assigned_workers

        workers: Units = self.role_manager.get_units_by_role(UnitRole.GATHERING, self.ai.race_worker)

        if not workers:
            return assigned_workers

        for item in self.resource_manager.worker_tag_to_nexus_tag_dict.items():
            if item[1] == self.townhall.tag:
                worker_at_nexus = self.ai.workers.find_by_tag(item[0])
                if worker_at_nexus:
                    assigned_workers.append(worker_at_nexus)

        return assigned_workers

    def make_placement_unavailable(
            self, size: BuildingSize, building_pos: Point2, tag: int
    ) -> None:

        placement_position: PlacementPosition = self.building_placements[size][building_pos]
        placement_position.available = False
        placement_position.building_tag = tag
        placement_position.worker_on_route = False

    def request_building_placement(
            self,
            structure_type: UnitTypeId,
            wall: bool = False,
            reserve_placement: bool = True,
            within_psionic_matrix: bool = False,
            pylon_build_progress: float = 1.0,
            closest_to: Optional[Point2] = None,
    ) -> Optional[Point2]:

        assert (
                structure_type in STRUCTURE_TO_BUILDING_SIZE
        ), f"{structure_type} not found in STRUCTURE_TO_BUILDING_SIZE dict"

        building_size: BuildingSize = STRUCTURE_TO_BUILDING_SIZE[structure_type]

        if building_size in self.building_placements:
            available: list[Point2] = self.get_potential_placements(
                building_size,
                structure_type,
                within_psionic_matrix,
                pylon_build_progress,
            )

            if len(available) == 0:
                """
                logger.warning(
                    f"No available {building_size} found near expansion:"
                    f" {self.location}"
                )
                """
                return

            if not closest_to:
                final_placement: Point2 = min(
                    available, key=lambda k: cy_distance_to_squared(k, self.location)
                )
            else:
                final_placement: Point2 = min(
                    available, key=lambda k: cy_distance_to_squared(k, closest_to)
                )

            if wall:
                if _available := [
                    a
                    for a in available
                    if self.building_placements[building_size][a].is_wall
                ]:
                    final_placement = min(
                        _available,
                        key=lambda k: cy_distance_to_squared(k, self.location),
                    )
                else:
                    final_placement = min(
                        available,
                        key=lambda k: cy_distance_to_squared(
                            k, self.ai.main_base_ramp.top_center
                        ),
                    )

            elif structure_type == UnitTypeId.PYLON:
                if available_opt := [
                    a
                    for a in available
                    if self.building_placements[building_size][a].optimal_pylon
                    # don't wall in, user should intentionally pass wall parameter
                    and not self.building_placements[building_size][a].is_wall
                ]:
                    final_placement = min(
                        available_opt,
                        key=lambda k: cy_distance_to_squared(k, self.location),
                    )
                elif available := [
                    a
                    for a in available
                    if self.building_placements[building_size][a].production_pylon
                    # don't wall in, user should intentionally pass wall parameter
                    and not self.building_placements[building_size][a].is_wall
                ]:
                    final_placement = min(
                        available,
                        key=lambda k: cy_distance_to_squared(k, self.location),
                    )
            elif within_psionic_matrix:
                build_near: Point2 = self.location

                if optimal_pylon := [
                    a
                    for a in self.building_placements[BuildingSize.TWO_BY_TWO]
                    if self.building_placements[BuildingSize.TWO_BY_TWO][a].optimal_pylon
                ]:
                    potential_build_near: Point2 = optimal_pylon[0]
                    three_by_threes: dict = self.building_placements[BuildingSize.THREE_BY_THREE]

                    close_to_pylon: list[Point2] = [
                        p
                        for p in three_by_threes
                        if cy_distance_to_squared(p, potential_build_near) < 42.25
                    ]
                    if len(close_to_pylon) < 4:
                        build_near = optimal_pylon[0]

                    final_placement = self.find_placement_near_pylon(available, build_near)

                    if not final_placement:
                        logger.warning(
                            f"Can't find placement near pylon near {build_near}."
                        )
                        return
            return final_placement

        return None

    def find_placement_near_pylon(
            self,
            available: list[Point2],
            base_location: Point2,
    ) -> Optional[Point2]:

        pylons = self.ai.unit_manager.own_structures(UnitTypeId.PYLON).ready

        if available := [
            a
            for a in available
            if cy_pylon_matrix_covers(
                a,
                pylons,
                self.ai.terrain_manager.terrain_height,
                pylon_build_progress=1,
            )
        ]:
            return min(
                available, key=lambda k: cy_distance_to_squared(k, base_location)
            )


    def get_potential_placements(

            self,
            building_size: BuildingSize,
            structure_type: UnitTypeId,
            within_psionic_matrix: bool,
            pylon_build_progress: float = 1.0,

    ) -> list[Point2]:

        potential_placements: Dict[Point2, PlacementPosition] = self.building_placements[building_size]

        available: list[Point2] = [
            placement
            for placement in potential_placements
            if potential_placements[placement].available
               and not potential_placements[placement].worker_on_route
               and self.ai.terrain_manager.can_place_structure(placement, structure_type)
        ]

        if within_psionic_matrix:
            pylons = self.ai.unit_manager.own_structures(UnitTypeId.PYLON).ready
            available = [
                a
                for a in available
                if cy_pylon_matrix_covers(
                    a,
                    pylons,
                    self.ai.game_info.terrain_height.data_numpy,
                    pylon_build_progress=pylon_build_progress,
                )
            ]

        return available

    @property
    def building_placements(self):
        return self.placement_info.building_placements

    @property
    def ready(self):
        return self.townhall and self.townhall.build_progress > 0.8

    @property
    def resource_manager(self) -> "ResourceManager":
        return self.ai.resource_manager

    @property
    def role_manager(self) -> "RoleManager":
        return self.ai.role_manager