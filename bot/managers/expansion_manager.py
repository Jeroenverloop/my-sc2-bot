from typing import TYPE_CHECKING, List, Dict, Optional, Tuple

import numpy as np
from loguru import logger
from sc2.position import Point2
from sc2.unit import Unit

from bot.helpers.building_helper import BuildingSize, STRUCTURE_TO_BUILDING_SIZE
from bot.managers.manager import Manager
from bot.models.expansion import Expansion

if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot


class ExpansionManager(Manager):

    def __init__(self, bot: "JeroenBot"):
        super().__init__(bot)

        self.expansions: List[Expansion] = []
        self.main_base: Optional[Expansion] = None
        self.worker_is_building_expansion: bool = False

    async def on_step(self, iteration: int):

        if len(self.expansions) == 0:
            for th in self.ai.unit_manager.own_townhalls:
                e:Expansion = self.create_expansion(th.position)
                e.townhall = th

        for th in self.ai.unit_manager.own_townhalls:
            for e in self.expansions:
                if e.location == th.position:
                    e.townhall = th


    async def on_unit_destroyed(self, unit_tag: int):
        self.delete_expansion(unit_tag)

    async def on_building_construction_started(self, unit: Unit):

        #we do this for gas buildings
        if not unit.type_id in STRUCTURE_TO_BUILDING_SIZE:
            return

        building_size: BuildingSize = STRUCTURE_TO_BUILDING_SIZE[unit.type_id]

        for e in self.expansions:
            if building_size not in e.placement_info.building_placements:
                continue
            if unit.position in e.placement_info.building_placements[building_size]:
                e.make_placement_unavailable(building_size, unit.position, unit.tag)

    def create_expansion(self, location: Point2):
        e = Expansion(self.ai, location)
        if not self.main_base:
            self.main_base = e
        self.expansions.append(e)
        return e

    def delete_expansion(self, unit_tag: int):

        expansion_to_delete: Optional[Expansion] = None

        for e in self.expansions:
            if e.townhall and e.townhall.tag == unit_tag:
                expansion_to_delete = e
                break
        if expansion_to_delete:
            self.expansions.remove(expansion_to_delete)

    def get_expansion_locations(self) -> List[Tuple[Point2, float]]:

        expansion_distances: List[Tuple[Point2, float]] = []

        if not self.main_base:
            return expansion_distances


        grid: np.ndarray = self.ai.terrain_manager.ground_grid

        available_locations = list(filter(lambda l: l not in self.taken_expansion_locations, self.ai.expansion_locations_list))

        for location in available_locations:

            if path := self.ai.terrain_manager.map_data.pathfind(
                self.main_base.location, location, grid
            ):
                expansion_distances.append((location, len(path)))

        # sort by path length to each expansion
        expansion_distances = sorted(expansion_distances, key=lambda x: x[1])
        return expansion_distances

    @property
    def taken_expansion_locations(self) -> List[Point2]:

        taken_expansion_locations: List[Point2] = []

        for expansion in self.expansions:
            taken_expansion_locations.append(expansion.location)

        return taken_expansion_locations



