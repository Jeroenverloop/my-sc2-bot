import random
from typing import List

from cython_extensions import cy_closest_to
from loguru import logger
from sc2.bot_ai import BotAI
from sc2.data import Race
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units

from bot.behaviours.macro.build_gas import BuildGas
from bot.behaviours.macro.build_pylons import BuildPylons
from bot.behaviours.macro.build_workers import BuildWorkers
from bot.behaviours.macro.resource_gathering import ResourceGathering
from bot.jeroen_bot_settings import JeroenBotSettings
from bot.consts import UnitRole
from bot.managers.hub import Hub


class JeroenBot(BotAI):

    def __init__(self):

        self.hub: Hub = Hub(self)
        self.need_builder: bool = False

    async def on_start(self) -> None:
        self.hub.on_start()

    async def on_step(self, iteration: int) -> None:
        self.hub.on_step(iteration)

        minerals_left:int = self.hub.resource_manager.get_total_minerals_at_nexus(self.townhalls.ready.first)
        gas_left:int = self.hub.resource_manager.get_total_gas_at_nexus(self.townhalls.ready.first)

        #logger.info(f"minerals left: {minerals_left} gas left: {gas_left}")

        build_workers: BuildWorkers = BuildWorkers().execute(self)
        gather: ResourceGathering = ResourceGathering().execute(self)
        build_gas: BuildGas = BuildGas().execute(self)
        build_pylons: BuildPylons = BuildPylons().execute(self)
        return




        builders:Units = self.hub.role_manager.get_units_by_role(UnitRole.BUILDING, UnitTypeId.PROBE)

        if not builders:
            self.need_builder = True
        else:
            self.need_builder = False
            builder = builders.random
            #logger.info(builder)

            supply_left = self.supply_left + (self.already_pending(UnitTypeId.PYLON)*8)

            if self.can_afford(UnitTypeId.PYLON) and supply_left < 2 + self.townhalls.ready.amount*2:
                townhall = self.townhalls.ready.random
                if townhall:
                    location = townhall.position.random_on_distance(random.randrange(1,6)).towards(self.enemy_start_locations[0],6)
                    if builder.orders:
                        order_exists = filter(lambda order: order.target == location, builder.orders)
                        if not order_exists:
                            builder.build(UnitTypeId.PYLON, location, queue=True)
                    else:
                        builder.build(UnitTypeId.PYLON, location)
                    return

            if self.can_afford(UnitTypeId.ASSIMILATOR):
                for nexus in self.townhalls.ready:
                    geysers: Units = self.vespene_geyser.filter(lambda g: g.distance_to(nexus) < 10)

                    for geyser in geysers:
                        if self.gas_buildings and cy_closest_to(geyser.position, self.gas_buildings).distance_to(geyser) < 1:
                            continue
                        if builder.orders:
                            order_exists = filter(lambda order: order.target == geyser, builder.orders)
                            if not order_exists:
                                builder.build_gas(geyser, queue=True)
                                builder.stop(queue=True)
                        else:
                            builder.build_gas(geyser)
                            builder.stop(queue=True)
                        return

            workers_on_gas = len(self.hub.resource_manager.worker_to_geyser_dict)
            workers_on_minerals = len(self.hub.resource_manager.worker_to_mineral_patch_dict)

            mining_workers = workers_on_gas + workers_on_minerals

            if self.townhalls.amount < 7 and ((self.can_afford(UnitTypeId.NEXUS) and mining_workers > self.townhalls.amount*14) or self.minerals > 1000):

                location: Point2 = await self.get_next_expansion()

                if builder.orders:
                    order_exists = filter(lambda order: order.target == location, builder.orders)
                    if not order_exists:
                        builder.build(UnitTypeId.NEXUS, location, queue=True)
                else:
                    builder.build(UnitTypeId.NEXUS, location)
                return

        workers_on_gas = self.hub.resource_manager.worker_to_geyser_dict.copy()
        workers_on_minerals = self.hub.resource_manager.worker_to_mineral_patch_dict.copy()

        mining_workers = len(workers_on_gas) + len(workers_on_minerals)

        unit_tags: set[int] = set()

        if mining_workers >= 30 and self.minerals >= 1000:
            while len(workers_on_gas) > 0:
                worker_tag = workers_on_gas.popitem()[0]
                self.hub.resource_manager.remove_worker_from_vespene(worker_tag)
                self.hub.role_manager.assign_role(worker_tag, UnitRole.ATTACKING)
                unit_tags.add(worker_tag)
            while len(workers_on_minerals) > 16:
                worker_tag = workers_on_minerals.popitem()[0]
                self.hub.resource_manager.remove_worker_from_mineral(worker_tag)
                self.hub.role_manager.assign_role(worker_tag, UnitRole.ATTACKING)
                unit_tags.add(worker_tag)

            for unit in self.state.observation_raw.units:
                if unit.tag in unit_tags:

                    unit_obj = Unit(
                        unit,
                        self
                    )
                    logger.info(unit_obj.type_id)
                    unit_obj.attack(self.enemy_start_locations[0].random_on_distance(random.randrange(1,30)).towards(self.start_location, 20))





    async def on_unit_created(self, unit: Unit) -> None:
        self.hub.on_unit_created(unit)
        logger.info(f"Unit {unit.type_id} was created")

    async def on_unit_destroyed(self, unit_tag: int) -> None:
        self.hub.on_unit_destroyed(unit_tag)
        logger.info(f"Unit with tag {unit_tag} was created")

    async def on_building_construction_complete(self, unit: Unit) -> None:
        logger.info(f"Building {unit.type_id} has finished")

    async def on_unit_took_damage(self, unit: Unit, amount_damage_taken: float) -> None:
        logger.info(f"Unit {unit.type_id} has taken {amount_damage_taken} damage")


    """
    Can use `python-sc2` hooks as usual, but make a call the inherited method in the superclass
    Examples:
    """
    # async def on_start(self) -> None:
    #     await super(MyBot, self).on_start()
    #
    #     # on_start logic here ...
    #
    # async def on_end(self, game_result: Result) -> None:
    #     await super(MyBot, self).on_end(game_result)
    #
    #     # custom on_end logic here ...
    #
    # async def on_building_construction_complete(self, unit: Unit) -> None:
    #     await super(MyBot, self).on_building_construction_complete(unit)
    #
    #     # custom on_building_construction_complete logic here ...
    #
    # async def on_unit_created(self, unit: Unit) -> None:
    #     await super(MyBot, self).on_unit_created(unit)
    #
    #     # custom on_unit_created logic here ...
    #
    # async def on_unit_destroyed(self, unit_tag: int) -> None:
    #     await super(MyBot, self).on_unit_destroyed(unit_tag)
    #
    #     # custom on_unit_destroyed logic here ...
    #
    # async def on_unit_took_damage(self, unit: Unit, amount_damage_taken: float) -> None:
    #     await super(MyBot, self).on_unit_took_damage(unit, amount_damage_taken)
    #
    #     # custom on_unit_took_damage logic here ...
