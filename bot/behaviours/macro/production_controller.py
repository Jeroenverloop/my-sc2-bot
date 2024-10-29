import random
from typing import TYPE_CHECKING, Set, Union, Optional, List

from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.position import Point2

from bot.behaviours.macro.build_structure import BuildStructure
from bot.behaviours.macro.macro_behaviour import MacroBehaviour
from bot.consts import UnitValueType
from bot.helpers.structure_helper import STRUCTURES, REQUIRE_POWER_STRUCTURE_TYPES
from bot.helpers.unit_helper import UNIT_TRAINED_FROM, ALL_WORKER_TYPES
from bot.models.army_composition import ArmyComposition
from bot.models.expansion import Expansion

if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot


class ProductionController(MacroBehaviour):

    def __init__(self):
        super().__init__()

    def execute(self, ai: "JeroenBot") -> bool:

        army_comp: ArmyComposition = ai.army_composition

        unit_types: list[UnitTypeId] = [*army_comp.unit_config_dict]

        num_total_units: int = 0

        mpm: float = ai.resource_manager.minerals_per_minute
        vpm: float = ai.resource_manager.vespene_per_minute

        for unit_type in unit_types:

            if unit_type not in STRUCTURES and unit_type not in ALL_WORKER_TYPES:

                if army_comp.unit_config_dict[unit_type].value_type == UnitValueType.Percentage:
                    num_total_units += ai.units.filter(lambda u: u.type_id == unit_type).amount


        collection_rate_minerals: int = ai.state.score.collection_rate_minerals + 1
        collection_rate_vespene: int = ai.state.score.collection_rate_vespene + 1

        #logger.info(f"mpm: {collection_rate_minerals} vpm: {collection_rate_vespene}")

        percentage: int = 0



        for unit_type_id, unit_config in sorted(army_comp.unit_config_dict.items(), key=lambda x: x[1].priority):

            assert isinstance(unit_type_id, UnitTypeId), (
                f"army_composition_dict expects UnitTypeId type as keys, "
                f"got {type(unit_type_id)}"
            )

            next_tech: List[Union[UnitTypeId, UpgradeId]] = ai.tech_manager.get_next_tech(unit_type_id)

            #for tech in next_tech:
            #    logger.info(f"Can make tech: {tech}")
            #logger.info('-----------------------------------')

            if not next_tech:

                max_units: int = 0

                if unit_config.value_type == UnitValueType.Amount:
                    max_units = unit_config.value

                if ai.unit_manager.own_army(unit_type_id).amount + ai.already_pending(unit_type_id) >= max_units:
                    continue

                if unit_type_id in UNIT_TRAINED_FROM and ai.resource_manager.can_afford(unit_type_id):

                    trained_from_buildings: Set[UnitTypeId] = UNIT_TRAINED_FROM[unit_type_id]

                    for building in trained_from_buildings:

                        if building == UnitTypeId.WARPGATE:
                            continue

                        available_buildings = ai.unit_manager.own_structures(building).ready.idle
                        if available_buildings:
                            available_buildings.random.train(unit_type_id)
                        else:
                            if (
                                ai.build_manager.structure_pending(building) == 0
                                and ai.already_pending(building) == 0
                            ):
                                position: Point2 = self._get_building_placement(ai, building)
                                if position:
                                    return BuildStructure(building, position).execute(ai)
                                continue

                continue
            else:
                for tech_to_build in next_tech:

                    if isinstance(tech_to_build, UnitTypeId):
                        if tech_to_build in STRUCTURES:

                            if ai.tech_manager.structure_exists(tech_to_build):
                                continue

                            structure_placement = self._get_building_placement(ai, tech_to_build)
                            if not structure_placement:
                                continue

                            return BuildStructure(tech_to_build, structure_placement).execute(ai)

        return False


    def _get_building_placement(self, ai: "JeroenBot", structure_type: UnitTypeId) -> Optional[Point2]:

        expansion: Expansion = random.choice(ai.expansion_manager.expansions)

        needs_power = structure_type in REQUIRE_POWER_STRUCTURE_TYPES

        position: Point2 = expansion.request_building_placement(
            structure_type=structure_type,
            within_psionic_matrix=needs_power
        )

        return position



