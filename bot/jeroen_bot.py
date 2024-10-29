from typing import Set, List

from cython_extensions import cy_distance_to
from loguru import logger
from s2clientprotocol.debug_pb2 import Color
from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2, Point3
from sc2.unit import Unit

from bot.behaviours.macro.build_gas import BuildGas
from bot.behaviours.macro.build_pylons import BuildPylons
from bot.behaviours.macro.build_workers import BuildWorkers
from bot.behaviours.macro.expand import Expand
from bot.behaviours.macro.production_controller import ProductionController
from bot.behaviours.macro.resource_gathering import ResourceGathering
from bot.behaviours.macro.upgrade_controller import UpgradeController
from bot.consts import UnitValueType
from bot.helpers.structure_helper import RACE_TOWNHALLS, RACE_TOWNHALLS_BASE
from bot.helpers.unit_helper import RACE_WORKER
from bot.jeroen_bot_settings import JeroenBotSettings
from bot.managers.build_manager import BuildManager
from bot.managers.debug_manager import DebugManager
from bot.managers.expansion_manager import ExpansionManager
from bot.managers.hub import Hub
from bot.managers.path_manager import PathManager
from bot.managers.resource_manager import ResourceManager
from bot.managers.role_manager import RoleManager
from bot.managers.tech_manager import TechManager
from bot.managers.terrain_manager import TerrainManager
from bot.managers.unit_manager import UnitManager
from bot.models.army_composition import ArmyComposition
from bot.models.expansion import Expansion
from bot.models.unit_composition_configuration import UnitCompositionConfiguration


class JeroenBot(BotAI):

    hub: Hub

    def __init__(self):

        self.army_composition: ArmyComposition = ArmyComposition({
            UnitTypeId.ZEALOT : UnitCompositionConfiguration(UnitTypeId.ZEALOT, 50, UnitValueType.Amount, 5),
            UnitTypeId.IMMORTAL : UnitCompositionConfiguration(UnitTypeId.IMMORTAL, 3, UnitValueType.Amount, 1),
            UnitTypeId.COLOSSUS: UnitCompositionConfiguration(UnitTypeId.COLOSSUS, 3, UnitValueType.Amount, 0),
            UnitTypeId.STALKER: UnitCompositionConfiguration(UnitTypeId.STALKER, 50, UnitValueType.Amount, 4),
            UnitTypeId.TEMPEST: UnitCompositionConfiguration(UnitTypeId.TEMPEST, 5, UnitValueType.Amount, 1),
            UnitTypeId.VOIDRAY: UnitCompositionConfiguration(UnitTypeId.VOIDRAY, 5, UnitValueType.Amount, 2),
            UnitTypeId.CARRIER: UnitCompositionConfiguration(UnitTypeId.CARRIER, 5, UnitValueType.Amount, 0),
        })

        self.hub = Hub(self)


    async def on_start(self) -> None:
        await self.hub.on_start()

    async def _prepare_step(self, state, proto_game_info):
        await super(JeroenBot, self)._prepare_step(state, proto_game_info)

        self.unit_manager.prepare_units()


    async def on_step(self, iteration: int) -> None:
        await self.hub.on_step(iteration)

        BuildWorkers().execute(self)
        ResourceGathering().execute(self)
        BuildGas().execute(self)
        BuildPylons().execute(self)
        Expand().execute(self)
        ProductionController().execute(self)
        #upgrades: UpgradeController = UpgradeController().execute(self)

        goal: Point2 = self.enemy_start_locations[0]
        closest_expansion_to_enemy: Expansion = self.expansion_manager.main_base
        chosen_path: List[Point2] = []
        smallest_dist: float = -1

        for e in self.expansion_manager.expansions:

            path_to_enemy: List[Point2] = self.terrain_manager.find_path(e.location, goal, self.terrain_manager.ground_grid, 1, True)
            path_dist: float = self.terrain_manager.calculate_path_distance(e.location, path_to_enemy)

            if smallest_dist < 0:
                closest_expansion_to_enemy = e
                smallest_dist = path_dist
                chosen_path = path_to_enemy
            elif path_dist < smallest_dist:
                closest_expansion_to_enemy = e
                smallest_dist = path_dist
                chosen_path = path_to_enemy

        chosen_point: Point2 = closest_expansion_to_enemy.location
        for p in chosen_path:
            if cy_distance_to(p,closest_expansion_to_enemy.location) > 30:
                chosen_point = p
                break

        color: Point3 = Point3((255,0,0))
        height: int = 15

        for i, p in enumerate(chosen_path):
            if i == 0:
                el = closest_expansion_to_enemy.location
                point1 = Point3((el.x, el.y, height))
                point2 = Point3((p.x, p.y, height))

                self.client.debug_line_out(point1,point2, color)
            else:
                el = chosen_path[i-1]
                point1 = Point3((el.x, el.y, height))
                point2 = Point3((p.x, p.y, height))
                self.client.debug_line_out(point1, point2, color)


        for unit in self.unit_manager.own_army:

            if self.unit_manager.own_army_value > 4000:
                unit.attack(self.enemy_start_locations[0])
            else:
                if closest_expansion_to_enemy and chosen_path:
                    if unit.is_idle:
                        unit.attack(chosen_point)


        for expansion in self.expansion_manager.expansions:
            await expansion.placement_info.draw_building_placements()


    async def on_unit_created(self, unit: Unit) -> None:
        await self.hub.on_unit_created(unit)

    async def on_unit_destroyed(self, unit_tag: int) -> None:
        await self.hub.on_unit_destroyed(unit_tag)

    async def on_building_construction_started(self, unit: Unit):
        await self.hub.on_building_construction_started(unit)

    async def on_building_construction_complete(self, unit: Unit) -> None:
        await self.hub.on_building_construction_complete(unit)

    async def on_unit_took_damage(self, unit: Unit, damage: float) -> None:
        await self.hub.on_unit_took_damage(unit, damage)

    async def on_enemy_unit_entered_vision(self, unit: Unit):
        await self.hub.on_enemy_unit_entered_vision(unit)

    async def on_enemy_unit_left_vision(self, unit_tag: int):
        await self.hub.on_enemy_unit_left_vision(unit_tag)

    async def on_unit_type_changed(self, unit: Unit, previous_type: UnitTypeId):
        await self.hub.on_unit_type_changed(unit, previous_type)

    @property
    def build_manager(self) -> BuildManager:
        return self.hub(BuildManager.__name__)

    @property
    def debug_manager(self) -> DebugManager:
        return self.hub(DebugManager.__name__)

    @property
    def expansion_manager(self) -> ExpansionManager:
        return self.hub(ExpansionManager.__name__)

    @property
    def path_manager(self) -> PathManager:
        return self.hub(PathManager.__name__)

    @property
    def resource_manager(self) -> ResourceManager:
        return self.hub(ResourceManager.__name__)

    @property
    def role_manager(self) -> RoleManager:
        return self.hub(RoleManager.__name__)

    @property
    def tech_manager(self) -> TechManager:
        return self.hub(TechManager.__name__)

    @property
    def terrain_manager(self) -> TerrainManager:
        return self.hub(TerrainManager.__name__)

    @property
    def unit_manager(self) -> UnitManager:
        return self.hub(UnitManager.__name__)

    @property
    def race_worker(self) -> UnitTypeId:
        return RACE_WORKER[JeroenBotSettings.RACE]

    @property
    def race_townhalls(self) -> Set[UnitTypeId]:
        return RACE_TOWNHALLS[JeroenBotSettings.RACE]

    @property
    def race_townhall_base(self) -> UnitTypeId:
        return RACE_TOWNHALLS_BASE[JeroenBotSettings.RACE]