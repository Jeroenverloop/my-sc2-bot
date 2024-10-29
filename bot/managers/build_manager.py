from typing import TYPE_CHECKING, Optional, Dict, Union, List, Set

from cython_extensions import cy_distance_to_squared, cy_distance_to, cy_closest_to
from loguru import logger
from sc2.data import Race
from sc2.game_data import Cost
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units

from bot.consts import UnitRole
from bot.helpers.structure_helper import GAS_BUILDINGS
from bot.helpers.unit_helper import RACE_WORKER
from bot.jeroen_bot_settings import JeroenBotSettings
from bot.managers.manager import Manager
from bot.models.building_tracker_entry import BuildingTrackerEntry
from bot.models.expansion import Expansion

if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot


class BuildManager(Manager):

    def __init__(self, ai: "JeroenBot"):
        super().__init__(ai)

        self.building_tracker: Dict[int, BuildingTrackerEntry] = {}
        self.building_counter: Dict[UnitTypeId, int] = {}

    async def on_step(self, iteration: int):

        self._handle_construction_orders()

        for worker in self.ai.role_manager.get_units_by_role(UnitRole.BUILDER, self.ai.race_worker):
            if worker.tag not in self.building_tracker:
                self.ai.role_manager.assign_role(worker.tag, UnitRole.GATHERING)

    async def on_unit_destroyed(self, unit_tag: int):
        self._remove_builder(unit_tag)

    async def on_building_construction_started(self, unit: Unit):

        build_order = None

        if unit.type_id in GAS_BUILDINGS:

            logger.info("Started building gass")

            geysers: Units = self.ai.vespene_geyser.filter(
                lambda g: cy_distance_to(g.position , unit.position) < 3
            )

            logger.info(f"geysers found: {geysers.amount}")

            if geysers:
                geyser = geysers.first
                build_order = self.get_build_order(unit.type_id, geyser)
                logger.info(f"build order found: {build_order}")
        else:
            build_order = self.get_build_order(unit.type_id, unit.position)

        if build_order:

            logger.info(f"I found the order for {unit.type_id}. removing order")

            unit_tag: int =self.get_build_order_builder_tag(build_order)
            #logger.info(f"unit_tag: {unit_tag}")
            if not unit_tag is None:
                self._remove_builder(unit_tag)
                self.ai.resource_manager.remove_resource_reservation(unit.type_id)


    def _remove_builder(self, tag: int) -> None:

        if tag in self.building_tracker:

            if self.building_tracker[tag].unit_type in self.building_counter:

                amount: int = self.building_counter[self.building_tracker[tag].unit_type]
                self.building_counter[self.building_tracker[tag].unit_type] = max(0 , amount-1)

            logger.info(f"building: {self.building_tracker[tag].unit_type} took {self.ai.time - self.building_tracker[tag].time_commenced} seconds")

            self.building_tracker.pop(tag)

    def get_builder(self, position:Point2) -> Optional[Unit]:

        builders: Units = self.ai.role_manager.get_units_by_role(UnitRole.BUILDER, self.ai.race_worker).filter(
            lambda u:
            not u.tag in self.building_tracker
        )

        if builders:
            return builders.closest_to(position)

        workers: Units = self.ai.unit_manager.own_workers.filter(lambda u:
            not u.tag in self.building_tracker
        )

        if workers:
            return workers.closest_to(position)

    def build(
        self,
        structure_type: UnitTypeId,
        target: Union[Point2,Unit],
    ):

        target_position: Point2 = target if isinstance(target, Point2) else target.position

        self.build_with_specific_worker(self.get_builder(target_position), structure_type, target)

    def build_with_specific_worker(
        self,
        worker: Unit,
        structure_type: UnitTypeId,
        target: Union[Point2,Unit],
    ) -> bool:

        if not target or not worker:
            return False

        tag: int = worker.tag

        if tag not in self.building_tracker:
            self.building_tracker[tag] = BuildingTrackerEntry(
                structure_type,
                target,
                self.ai.time
            )

            if structure_type in self.building_counter:
                self.building_counter[structure_type] += 1
            else:
                self.building_counter[structure_type] = 1

            self.ai.role_manager.assign_role(tag, UnitRole.BUILDER)
            self.ai.resource_manager.release_worker(worker)
            self.ai.resource_manager.make_resource_reservation(structure_type)

            return True

        return False

    def _handle_construction_orders(self) -> None:

        dead_tags_to_remove: Set[int] = set()
        tags_to_remove: Set[int] = set()
        structures_dict: Dict[UnitTypeId, List[Unit]] = self.ai.unit_manager.own_structures_dict
        building_spots: Set[Point2] = set()

        for worker_tag in self.building_tracker:
            if self.building_tracker[worker_tag].target:
                self.ai.debug_manager.draw_text_on_world(
                    Point2(self.building_tracker[worker_tag].target.position),
                    f"BUILDING TARGET {self.building_tracker[worker_tag].target.position}",
                )

            structure_id: UnitTypeId = self.building_tracker[worker_tag].unit_type

            time_out_time: float = self.building_tracker[worker_tag].time_commenced + JeroenBotSettings.BUILD_WORKER_TIMEOUT

            if self.ai.time > time_out_time:
                tags_to_remove.add(worker_tag)

            target: Union[Point2, Unit] = self.building_tracker[worker_tag].target
            worker = self.ai.unit_manager.own_unit_tag_dict.get(worker_tag, None)

            target_position: Point2 = target if isinstance(target, Point2) else target.position

            if worker:
                self.ai.debug_manager.draw_text_on_world(
                    Point2(worker.position),
                    f"WORKER {worker.position}, {cy_distance_to(worker.position, target_position)}",
                )




            if not worker:
                dead_tags_to_remove.add(worker_tag)
                continue

            if worker.is_carrying_resource:
                worker.return_resource()
                continue

            if not target or target in building_spots:
                tags_to_remove.add(worker_tag)
                continue

            building_spots.add(target)

            if close_structures := self.ai.unit_manager.own_structures.filter(
                lambda s:
                cy_distance_to_squared(s.position, target_position) < 2.0
            ):
                structure: Unit = close_structures[0]
                target_progress: float = 1.0 if JeroenBotSettings.RACE == Race.Terran else 1e-16
                if structure.build_progress >= target_progress:
                    tags_to_remove.add(worker_tag)
                    continue

            distance: float = 3.2 if structure_id in GAS_BUILDINGS else 1.0

            if self.ai.race == Race.Protoss and structure_id in GAS_BUILDINGS:
                if self.ai.can_afford(structure_id):
                    worker.build_gas(target)
                continue

            if cy_distance_to(worker.position, target_position) > distance:

                order_target: Union[int, Point2, None] = worker.order_target

                point: Point2 = self.ai.terrain_manager.find_next_point_in_path(
                    start=worker.position,
                    goal=target_position,
                    grid=self.ai.terrain_manager.ground_grid
                )

                if (
                    order_target
                    and isinstance(order_target, Point2)
                    and order_target == point
                ):
                    continue

                worker.move(point)

            else:
                if structure_id in GAS_BUILDINGS and self.ai.can_afford(structure_id):
                    if self.ai.unit_manager.enemy_structures.filter(
                            lambda u:
                            u.type_id in GAS_BUILDINGS
                            and cy_distance_to_squared(target_position, u.position) < 20.25
                    ):
                        existing_gas_buildings: Units = self.ai.unit_manager.own_gas_buildings
                        if available_geysers := self.ai.vespene_geyser.filter(
                                lambda g:
                                not existing_gas_buildings.closer_than(5.0, g)
                        ):
                            self.building_tracker[worker_tag].target = available_geysers.closest_to(self.ai.start_location)
                            continue
                    else:
                        logger.info("BUILD GASSSS")
                        worker.stop()
                        worker.build_gas(target, queue=True)

                elif structure_id not in GAS_BUILDINGS:
                    if not self.ai.terrain_manager.can_place_structure(
                        position=target_position, structure_type=structure_id
                    ):

                        terrain_height = self.ai.terrain_manager.get_terrain_height(target_position)

                        expansions: List[Expansion] = list(filter(lambda e: e.terrain_height == terrain_height, self.ai.expansion_manager.expansions))

                        if expansions:

                            distance: float = 10000
                            chosen_expansion: Optional[Expansion] = None

                            for e in expansions:
                                calculated_distance: float = cy_distance_to(e.location, target_position)
                                if calculated_distance < distance:
                                    distance = calculated_distance
                                    chosen_expansion = e

                            self.building_tracker[worker_tag].target = chosen_expansion.request_building_placement(
                                structure_id,
                                within_psionic_matrix= JeroenBotSettings.RACE == Race.Protoss,
                            )
                        else:
                            self.building_tracker[worker_tag].target = target.position

                        continue

                if (
                    (not worker.is_constructing_scv or worker.is_idle)
                    and self.ai.can_afford(structure_id)
                ):
                    worker.build(structure_id, target)

    def time_to_reach_target(self, unit: Unit, target:Point2) -> float:

        path: List[Point2] = self.ai.terrain_manager.find_path(unit.position, target, self.ai.terrain_manager.ground_grid)
        path_end = path[len(path) - 1]

        dist_from_target = cy_distance_to(target,path_end)
        if dist_from_target > 3:
            logger.info(f"target:{target}, path end:{path_end}")
            return -1

        path_dist: float = self.ai.terrain_manager.calculate_path_distance(unit.position, path)
        worker_speed = unit.movement_speed * 1.4
        seconds_to_reach_location: float = (path_dist / worker_speed) + 0.5
        return seconds_to_reach_location

    def can_start_build_order(self, structure_type: UnitTypeId, target: Point2, worker: Unit) -> bool:
        if not worker:
            return False

        seconds_to_reach_location: float = self.time_to_reach_target(worker, target)

        if seconds_to_reach_location < 0:
            return False

        minerals_per_second: float = self.ai.resource_manager.minerals_per_minute / 60
        vespene_per_second: float = self.ai.resource_manager.vespene_per_minute / 60
        minerals_mined_before_reaching_target: float = (seconds_to_reach_location * minerals_per_second)
        vespene_mined_before_reaching_target: float = (seconds_to_reach_location * vespene_per_second)
        structure_cost: Cost = self.ai.calculate_cost(structure_type)

        minerals: int = self.ai.resource_manager.minerals
        vespene: int = self.ai.resource_manager.vespene

        return(
            minerals + minerals_mined_before_reaching_target > structure_cost.minerals
            and vespene + vespene_mined_before_reaching_target > structure_cost.vespene
        )

    def has_build_order(self, unit_type: UnitTypeId, target: Union[Unit, Point2]) -> bool:
        for building_tracker_entry in self.building_tracker.values():
            if building_tracker_entry.target == target and building_tracker_entry.unit_type == unit_type:
                return True
        return False

    def get_build_order(self, unit_type: UnitTypeId, target: Union[Unit,Point2]) -> Optional[BuildingTrackerEntry]:
        for building_tracker_entry in self.building_tracker.values():
            bte_pos: Point2 = building_tracker_entry.target if isinstance(building_tracker_entry.target, Point2) else building_tracker_entry.target.position
            target_pos: Point2 = target if isinstance(target, Point2) else target.position
            if bte_pos == target_pos and building_tracker_entry.unit_type == unit_type:
                return building_tracker_entry

    def get_build_order_builder_tag(self, entry: BuildingTrackerEntry) -> Optional[int]:
        for tag, building_tracker_entry in self.building_tracker.items():
            if entry == building_tracker_entry:
                return tag

    def structure_pending(self, structure_type: UnitTypeId) -> int:

        if structure_type in self.building_counter:
            return self.building_counter[structure_type]
        else:
            return 0



