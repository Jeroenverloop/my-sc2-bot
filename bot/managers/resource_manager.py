from typing import List, Callable, Dict, Set, Optional, Union

from loguru import logger
from sc2.game_data import Cost
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units
from scipy.constants import proton_mass

from bot.consts import UnitRole
from bot.jeroen_bot_settings import JeroenBotSettings
from bot.managers.manager import Manager

from cython_extensions import (
    cy_distance_to,
    cy_sorted_by_distance_to,
    cy_closest_to
)

class ResourceManager(Manager):

    WORKERS_PER_GAS:int = 3
    WORKERS_PER_MINERAL_FIELD:int = 2

    def __init__(self, bot):
        super().__init__(bot)

        self.split: bool = True

        self.worker_to_mineral_patch_dict: Dict[int, int] = {}
        self.mineral_patch_to_worker_dict: Dict[int, Set[int]] = {}

        self.worker_to_geyser_dict: Dict[int, int] = {}
        self.geyser_to_worker_dict: Dict[int, Set[int]] = {}

        self.worker_tag_to_nexus_tag_dict: Dict[int, int] = {}

        self.available_mineral_fields: Units = Units([], self.ai)

        self.resource_reservation: Cost = Cost(minerals=0,vespene=0)

    async def on_step(self, iteration: int):

        self.available_mineral_fields = self.get_available_mineral_fields()

        workers:Units = self.ai.role_manager.get_units_by_role(UnitRole.GATHERING)

        #logger.info(f"Gathering workers: {workers.amount}")

        if iteration % 4 == 0 or len(self.worker_to_mineral_patch_dict) == 0:
            self.assign_workers(workers)

    async def on_unit_destroyed(self, unit_tag: int):
        self.release_worker_by_tag(unit_tag)

    def release_worker_by_tag(self, worker_tag: int):
        if worker_tag in self.worker_to_mineral_patch_dict:
            self.remove_worker_from_mineral(worker_tag)
        if worker_tag in self.worker_to_geyser_dict:
            self.remove_worker_from_vespene(worker_tag)

    def release_worker(self, worker: Unit):
        if worker.tag in self.worker_to_mineral_patch_dict:
            self.remove_worker_from_mineral(worker.tag)
        if worker.tag in self.worker_to_geyser_dict:
            self.remove_worker_from_vespene(worker.tag)

    def release_workers(self, workers: Units):
        for worker in workers:
            self.release_worker(worker)

    def assign_workers(self, workers: Units) -> None:

        if not workers or not self.ai.townhalls:
            return

        if len(self.worker_to_mineral_patch_dict) > len(self.worker_to_geyser_dict)*JeroenBotSettings.MINERAL_GAS_DISTRIBUTION:
            if self.ai.gas_buildings.ready.filter(lambda g: g.vespene_contents > 0):
                self.assign_worker_to_gas_buildings()

        #logger.info(f"mineral_fields: {self.available_mineral_fields.amount}")

        if self.available_mineral_fields:
            unassigned_workers: Units = workers.filter(
                lambda w: not self.is_worker_assigned(w)
            )

            #logger.info(f"available mineral fields: {self.available_mineral_fields.amount} and unassigned workers: {unassigned_workers.amount}")

            self.assign_workers_to_mineral_patches(unassigned_workers)

    def is_worker_assigned(self, worker:Unit) -> bool:
        return (
            worker.tag in self.worker_to_mineral_patch_dict
            or worker.tag in self.worker_to_geyser_dict
        )

    def assign_workers_to_mineral_patches(self, workers:Units):

        if len(workers) == 0 or len(self.available_mineral_fields) == 0 or not self.ai.townhalls:
            return


        for worker in workers:

            if self.is_worker_assigned(worker):
                continue

            if self.available_mineral_fields.amount == 0:
                return

            closest_mineral: Unit = cy_closest_to(worker.position, self.available_mineral_fields)
            nearby_minerals: Units = self.available_mineral_fields.closer_than(10, closest_mineral)
            nexus: Unit = cy_closest_to(closest_mineral.position, self.ai.townhalls)
            mineral: Unit = cy_closest_to(nexus.position, nearby_minerals)

            if self.is_mineral_field_available(mineral):
                self.assign_worker_to_mineral_patch(mineral, worker)

            if not self.is_mineral_field_available(mineral):
                self.available_mineral_fields.remove(mineral)

    def assign_worker_to_mineral_patch(self, mineral_field: Unit, worker: Unit):

        #logger.info(f"Assigning worker {worker.tag} to mineral field {mineral_field.tag}")

        if self.miners_on_mineral_field(mineral_field) == 0:
            self.mineral_patch_to_worker_dict[mineral_field.tag] = {worker.tag}
        else:
            if worker.tag not in self.mineral_patch_to_worker_dict[mineral_field.tag]:
                workers_on_patch = len(self.mineral_patch_to_worker_dict[mineral_field.tag])
                self.mineral_patch_to_worker_dict[mineral_field.tag].add(worker.tag)

        self.worker_to_mineral_patch_dict[worker.tag] = mineral_field.tag
        self.worker_tag_to_nexus_tag_dict[worker.tag] = cy_closest_to(
            mineral_field.position, self.ai.townhalls
        ).tag

    def is_mineral_field_available(self, mineral_field: Unit) -> bool:

        if not mineral_field.tag in self.mineral_patch_to_worker_dict:
            return True

        return len(self.mineral_patch_to_worker_dict[mineral_field.tag]) < self.WORKERS_PER_MINERAL_FIELD


    def miners_on_mineral_field(self, mineral_field: Unit) -> int:
        return len(self.mineral_patch_to_worker_dict.get(mineral_field.tag, set()))

    def assign_worker_to_gas_buildings(self):

        if (
            not self.ai.gas_buildings
            or not self.ai.unit_manager.own_townhalls.ready
            or not self.ai.unit_manager.own_workers
        ):
            return

        for gas_building in self.ai.gas_buildings.ready:

            if gas_building.vespene_contents == 0:
                continue
            #logger.info(f"gas_building: {gas_building}")

            if not self.ai.townhalls.ready.closer_than(12, gas_building):
                continue

            workers_on_gas_building: Set[int] = self.get_workers_on_geyser(gas_building)
            workers_on_gas_building_amount = len(workers_on_gas_building)
            #logger.info(f"Workers on gas building {gas_building.tag}: {workers_on_gas_building_amount}")

            if workers_on_gas_building_amount > self.WORKERS_PER_GAS:
                #remove worker from gas
                pass
            elif workers_on_gas_building_amount == self.WORKERS_PER_GAS:
                continue
            else:
                worker: Optional[Unit] = self.select_worker(gas_building.position)

                #logger.info(f"selected gas worker: {worker}")

                if not worker:
                    continue

                if workers_on_gas_building_amount > 0:
                    if not worker.tag in workers_on_gas_building:
                        self.geyser_to_worker_dict[gas_building.tag].add(worker.tag)
                    else:
                        continue
                else:
                    self.geyser_to_worker_dict[gas_building.tag] = {worker.tag}

                closest_nexus = cy_closest_to(gas_building.position, self.ai.townhalls)
                self.worker_to_geyser_dict[worker.tag] = gas_building.tag
                self.worker_tag_to_nexus_tag_dict[worker.tag] = closest_nexus.tag
                self.remove_worker_from_mineral(worker.tag)

                #logger.info(f"{self.get_workers_on_geyser(gas_building)}")

                break


    def select_worker(self, target_position: Point2) -> Optional[Unit]:

        workers: Units = self.ai.role_manager.get_units_by_role(UnitRole.GATHERING, self.ai.race_worker)

        unassigned_workers: Units = workers.tags_not_in(
            list(self.worker_to_mineral_patch_dict) + list(self.worker_to_geyser_dict)
        )

        if unassigned_workers:
            worker: Unit = cy_closest_to(target_position, unassigned_workers)
            self.remove_worker_from_mineral(worker.tag)
            return worker

        available_workers = workers.filter(
            lambda w:
                w.tag in self.worker_to_mineral_patch_dict
                and not w.is_carrying_resource
        )

        if available_workers:

            nexuses: list[Unit] = cy_sorted_by_distance_to(
                self.ai.townhalls.filter(
                    lambda th: th.is_ready
                               and self.ai.mineral_field.closer_than(10, th).amount >= 8
                ),
                target_position,
            )

            if not nexuses:
                worker = cy_closest_to(target_position, available_workers)
                self.remove_worker_from_mineral(worker.tag)
                return worker

            for nexus in nexuses:

                mineral_fields_sorted_by_distance: list[Unit] = cy_sorted_by_distance_to(
                    self.ai.mineral_field.closer_than(10, nexus), nexus.position, reverse=True
                )

                for mineral_field in mineral_fields_sorted_by_distance:

                    selected_workers = available_workers.filter(
                        lambda w:
                            w.tag in self.get_workers_on_mineral_patch(mineral_field)
                        and not w.is_carrying_resource
                        and not w.is_collecting
                    )

                    if selected_workers:
                        worker: Unit = selected_workers.first
                        self.remove_worker_from_mineral(worker.tag)
                        return worker

            worker: Unit = cy_closest_to(target_position, available_workers)
            self.remove_worker_from_mineral(worker.tag)
            return worker



    def remove_worker_from_mineral(self, worker_tag: int) -> None:

        if worker_tag in self.worker_to_mineral_patch_dict:

            mineral_patch_tag: int = self.worker_to_mineral_patch_dict[worker_tag]
            del self.worker_to_mineral_patch_dict[worker_tag]
            if worker_tag in self.worker_tag_to_nexus_tag_dict:
                del self.worker_tag_to_nexus_tag_dict[worker_tag]

            self.mineral_patch_to_worker_dict[mineral_patch_tag].remove(worker_tag)

    def remove_worker_from_vespene(self, worker_tag: int) -> None:

        if worker_tag in self.worker_to_geyser_dict:

            gas_building_tag: int = self.worker_to_geyser_dict[worker_tag]
            del self.worker_to_geyser_dict[worker_tag]
            if worker_tag in self.worker_tag_to_nexus_tag_dict:
                del self.worker_tag_to_nexus_tag_dict[worker_tag]


            self.geyser_to_worker_dict[gas_building_tag].remove(worker_tag)


    def get_available_mineral_fields(self) -> Units:

        available_minerals: Units = Units([], self.ai)
        progress: float = 0.85
        townhalls: Units = self.ai.townhalls.filter(
            lambda th: th.build_progress > progress
        )

        for townhall in townhalls:
            if self.ai.mineral_field:
                minerals_sorted = cy_sorted_by_distance_to(
                    self.ai.mineral_field.filter(
                        lambda mineral_field:
                        mineral_field.is_visible
                        and not mineral_field.is_snapshot
                        and cy_distance_to(mineral_field.position, townhall.position) < 10
                        and len(self.mineral_patch_to_worker_dict.get(mineral_field.tag, [])) < self.WORKERS_PER_MINERAL_FIELD
                    ),
                    townhall.position
                )

                if minerals_sorted:
                    available_minerals.extend(minerals_sorted)

        return available_minerals

    def remove_gas_building(self, building_tag: int):
        #logger.info(f"remove_gas_building {building_tag}")
        if building_tag in self.geyser_to_worker_dict:
            del self.geyser_to_worker_dict[building_tag]
            self.worker_to_geyser_dict = {
                key: val
                for key, val in self.worker_to_geyser_dict.items()
                if val != building_tag
            }

    def remove_mineral_field(self, mineral_field_tag: int) -> None:

        if mineral_field_tag in self.mineral_patch_to_worker_dict:
            del self.mineral_patch_to_worker_dict[mineral_field_tag]
            self.worker_to_mineral_patch_dict = {
                key: val
                for key, val in self.worker_to_mineral_patch_dict.items()
                if val != mineral_field_tag
            }

    def get_workers_on_mineral_patch(self, mineral_patch: Unit) -> Set[int]:
        return self.mineral_patch_to_worker_dict.get(mineral_patch.tag, set())

    def get_workers_on_geyser(self, geyser: Unit) -> Set[int]:
        return self.geyser_to_worker_dict.get(geyser.tag, set())

    def get_mineral_fields_at_nexus(self, nexus: Unit) -> Units:
        return self.ai.mineral_field.filter(
            lambda mineral_field:
            mineral_field.is_visible
            and not mineral_field.is_snapshot
            and cy_distance_to(mineral_field.position, nexus.position) < 10
        )

    def get_mineral_fields_at_position(self, position: Point2) -> Units:
        return self.ai.mineral_field.filter(
            lambda mineral_field:
            mineral_field.is_visible
            and not mineral_field.is_snapshot
            and cy_distance_to(mineral_field.position, position) < 10
        )

    def get_total_minerals_at_nexus(self, nexus: Unit) -> int:
        return self.get_total_minerals_at_position(nexus.position)

    def get_total_minerals_at_position(self, position: Point2) -> int:
        total_minerals: int = 0
        mineral_fields = self.get_mineral_fields_at_position(position)
        for mf in mineral_fields:
            total_minerals += mf.mineral_contents
        return total_minerals

    def get_total_gas_at_nexus(self, nexus: Unit) -> int:
        return self.get_total_gas_at_position(nexus.position)

    def get_total_gas_at_position(self, position: Point2) -> int:

        total_gas: int = 0

        geysers: Units = self.ai.vespene_geyser.filter(
            lambda vespene_geyser:
            vespene_geyser.is_visible
            and not vespene_geyser.is_snapshot
            and cy_distance_to(vespene_geyser.position, position) < 10
        )

        if not geysers:
            return total_gas

        for g in geysers:
            total_gas += g.vespene_contents


        return total_gas

    def make_resource_reservation(self, item_id: Union[UnitTypeId, UpgradeId, AbilityId]):
        cost: Cost = self.ai.calculate_cost(item_id)
        if cost:
            self.resource_reservation.minerals += cost.minerals
            self.resource_reservation.vespene += cost.vespene

    def remove_resource_reservation(self, item_id: Union[UnitTypeId, UpgradeId, AbilityId]):
        cost: Cost = self.ai.calculate_cost(item_id)
        if cost:
            self.resource_reservation.minerals =  max(0, self.resource_reservation.minerals -cost.minerals)
            self.resource_reservation.vespene = max(0, self.resource_reservation.vespene -cost.vespene)

    def can_afford(self, item_id: Union[UnitTypeId, UpgradeId, AbilityId]):
        cost: Cost = self.ai.calculate_cost(item_id)
        if self.minerals >= cost.minerals and self.vespene >= cost.vespene:
            return True
        return False

    @property
    def minerals(self):
        return self.ai.minerals - self.resource_reservation.minerals

    @property
    def vespene(self):
        return self.ai.vespene - self.resource_reservation.vespene



    @property
    def resource_tag_to_unit_dict(self) -> Dict[int, Unit]:

        resource_dict: Dict[int, Unit] = {}

        mineral_fields = self.ai.mineral_field

        for mf in mineral_fields:
            resource_dict[mf.tag] = mf

        geysers = self.ai.gas_buildings

        for g in geysers:
            resource_dict[g.tag] = g

        return resource_dict

    @property
    def minerals_per_minute(self):
        return self.ai.state.score.collection_rate_minerals + 1

    @property
    def vespene_per_minute(self):
        return self.ai.state.score.collection_rate_vespene + 1



