import sys
from typing import TYPE_CHECKING, Dict

from cython_extensions import cy_distance_to, cy_closest_to, cy_distance_to_squared
from loguru import logger
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units

from bot.behaviours.macro.macro_behaviour import MacroBehaviour
from bot.consts import UnitRole

if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot


class ResourceGathering(MacroBehaviour):

    def __init__(self):
        super().__init__()

        self.locked_action_tags: Dict[int, float] = {}

    def execute(self, ai: "JeroenBot"):

        workers: Units = ai.role_manager.get_units_by_role(UnitRole.GATHERING, ai.race_worker)

        resources_dict: dict[int, Unit] = ai.resource_manager.resource_tag_to_unit_dict

        worker_to_mineral_patch_dict: Dict[int, int] = ai.resource_manager.worker_to_mineral_patch_dict
        worker_to_geyser_dict: Dict[int, int] = ai.resource_manager.worker_to_geyser_dict

        for worker in workers:

            worker_tag: int = worker.tag
            worker_position: Point2 = worker.position

            assigned_mineral_patch: bool = worker_tag in worker_to_mineral_patch_dict
            assigned_gas_building: bool = worker_tag in worker_to_geyser_dict

            dist_to_resource: float = 15.0
            if assigned_mineral_patch or assigned_gas_building:
                resource_tag:int
                if assigned_mineral_patch:
                    resource_tag = worker_to_mineral_patch_dict[worker_tag]
                else:
                    resource_tag = worker_to_geyser_dict[worker_tag]

                try:
                    _resource = resources_dict[resource_tag]
                    resource_position = _resource.position
                    resource_tag = _resource.tag
                    resource = _resource
                    dist_to_resource = cy_distance_to(
                        worker_position, resource_position
                    )
                    if (
                            resource.type_id == UnitTypeId.ASSIMILATOR
                            and resource.vespene_contents == 0
                    ):
                        ai.resource_manager.remove_gas_building(resource_tag)
                except KeyError:
                    if assigned_mineral_patch:
                        logger.info("Remove mineral field")
                        ai.resource_manager.remove_mineral_field(resource_tag)
                    else:
                        logger.info("Remove gas building")
                        ai.resource_manager.remove_gas_building(resource_tag)
                    continue

            if ai.townhalls and (assigned_mineral_patch or assigned_gas_building):

                if dist_to_resource > 6.0 and not worker.is_carrying_resource:
                    worker.move(
                        ai.terrain_manager.find_next_point_in_path(
                            start=worker_position,
                            goal=resource_position,
                            grid=ai.terrain_manager.ground_grid,
                        )
                    )
                elif(
                    len(worker.orders) == 1
                    and worker.orders[0].ability.id == AbilityId.MOVE
                    and ai.townhalls.ready.amount > 0
                    and worker.order_target == cy_closest_to(worker_position, ai.townhalls.ready).tag
                ) or(
                    worker.is_gathering and worker.order_target != resource_tag
                ):
                    worker(AbilityId.SMART, resource)
                else:
                    self.do_standard_mining(ai, worker, resource)
        return True

    def do_standard_mining(self, ai: "JeroenBot", worker: Unit, resource: Unit) -> None:
        worker_tag: int = worker.tag
        # prevent spam clicking workers on patch to reduce APM
        if worker_tag in self.locked_action_tags:
            if ai.time > self.locked_action_tags[worker_tag] + 0.5:
                self.locked_action_tags.pop(worker_tag)
            return

        if worker.is_carrying_vespene and resource.is_mineral_field:
            worker.return_resource()
            self.locked_action_tags[worker_tag] = ai.time

        else:
            # work out when we need to issue command to mine resource
            if worker.is_idle or (
                cy_distance_to_squared(worker.position, resource.position) > 81.0
                and worker.order_target
                and worker.order_target != resource
            ):
                worker.gather(resource)
                self.locked_action_tags[worker_tag] = ai.time
                return

            # force worker to stay on correct resource
            # in game auto mining will sometimes shift worker
            if (
                not worker.is_carrying_minerals
                and not worker.is_carrying_vespene
                and worker.order_target != resource.tag
            ):
                worker.gather(resource)
                # to reduce apm we prevent spam clicking on same mineral
                self.locked_action_tags[worker_tag] = ai.time
