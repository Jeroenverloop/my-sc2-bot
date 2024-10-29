from sc2.position import Point2

from bot.helpers.building_helper import BuildingSize


class PlacementPosition:


    def __init__(
            self,
            available: bool,
            has_addon: bool,
            is_wall: bool,
            building_tag: int,
            worker_on_route: bool,
            time_requested: float,
            production_pylon: bool,
            bunker: bool,
            optimal_pylon: bool,
    ):
        self.available = available
        self.has_addon = has_addon
        self.is_wall = is_wall
        self.building_tag = building_tag
        self.worker_on_route = worker_on_route
        self.time_requested = time_requested
        self.production_pylon = production_pylon
        self.bunker = bunker
        self.optimal_pylon = optimal_pylon
