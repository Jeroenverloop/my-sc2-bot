from typing import TYPE_CHECKING, List, Dict, Optional

from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units

from bot.helpers.structure_helper import TOWNHALL_TYPES, GAS_BUILDINGS
from bot.helpers.unit_helper import ALL_WORKER_TYPES
from bot.managers.manager import Manager
from bot.models.Unit_cache_Info import UnitCacheInfo

if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot


class UnitManager(Manager):

    def __init__(self, ai: "JeroenBot"):
        super().__init__(ai)

        self.own_workers: Units = Units([], ai)
        self.own_army: Units = Units([], ai)
        self.own_structures: Units = Units([], ai)
        self.own_army_dict: Dict[UnitTypeId, List[Unit]] = {}
        self.own_structures_dict: Dict[UnitTypeId, List[Unit]] = {}

        self.own_unit_tag_dict: Dict[int, Unit] = {}

        self.own_townhalls: Units = Units([], ai)
        self.own_gas_buildings: Units = Units([], ai)

        self.enemy_workers: Units = Units([], ai)
        self.enemy_army: Units = Units([], ai)
        self.enemy_structures: Units = Units([], ai)
        self.enemy_army_tag_dict: Dict[int, UnitCacheInfo] = {}
        self.enemy_worker_tag_dict: Dict[int, UnitCacheInfo] = {}
        self.enemy_structure_tag_dict: Dict[int, UnitCacheInfo] = {}
        self.enemy_type_dict: Dict[UnitTypeId, List[int]] = {}

    def _clear(self):
        self.own_army_dict.clear()
        self.own_structures_dict.clear()
        self.own_unit_tag_dict.clear()
        self.enemy_type_dict.clear()

    def prepare_units(self):

        self._clear()

        _own_workers: List[Unit] = []
        _own_army: List[Unit] = []
        _own_structures: List[Unit] = []
        _own_townhalls: List[Unit] = []
        _own_gas_buildings: List[Unit] = []

        _enemy_workers: List[Unit] = []
        _enemy_army: List[Unit] = []
        _enemy_structures: List[Unit] = []


        for unit in self.ai.all_own_units:
            self.own_unit_tag_dict[unit.tag] = unit
            if unit.is_structure:
                if unit.type_id in TOWNHALL_TYPES:
                    _own_townhalls.append(unit)
                elif unit.type_id in GAS_BUILDINGS:
                    _own_gas_buildings.append(unit)
                _own_structures.append(unit)
                self.add_to_unit_dict(self.own_structures_dict, unit)
            else:
                if unit.type_id in ALL_WORKER_TYPES:
                    _own_workers.append(unit)
                else:
                    _own_army.append(unit)
                    self.add_to_unit_dict(self.own_army_dict, unit)

        for unit in self.ai.all_enemy_units:
            if unit.is_structure:
                _enemy_structures.append(unit)
                self.add_to_cache_dict(self.enemy_structure_tag_dict, unit)
            else:
                if unit.type_id in ALL_WORKER_TYPES:
                    _enemy_workers.append(unit)
                    self.add_to_cache_dict(self.enemy_worker_tag_dict, unit)
                else:
                    _enemy_army.append(unit)
                    self.add_to_cache_dict(self.enemy_army_tag_dict, unit)

            self.add_to_enemy_type_cache_dict(unit)

        self.own_workers = Units(_own_workers, self.ai)
        self.own_army = Units(_own_army, self.ai)
        self.own_structures = Units(_own_structures, self.ai)

        self.own_townhalls = Units(_own_townhalls, self.ai)
        self.own_gas_buildings = Units(_own_gas_buildings, self.ai)

        self.enemy_workers = Units(_enemy_workers, self.ai)
        self.enemy_army = Units(_enemy_army, self.ai)
        self.enemy_structures = Units(_enemy_structures, self.ai)

    def add_to_enemy_type_cache_dict(self, unit: Unit):
        if unit.type_id in self.enemy_type_dict:
            self.enemy_type_dict[unit.type_id].append(unit.tag)
        else:
            self.enemy_type_dict[unit.type_id] = [unit.tag]

    def add_to_cache_dict(self, cache_dict: Dict[int, UnitCacheInfo], unit: Unit):
        if unit.tag in cache_dict and unit.type_id == cache_dict[unit.tag].unit_type:
            cache_dict[unit.tag].update(unit, self.ai.time)
        else:
            cache_dict[unit.tag] = self._create_cache_info(unit)

    def _create_cache_info(self, unit: Unit) -> UnitCacheInfo:
        return UnitCacheInfo(unit, self.ai.time)

    def add_to_unit_dict(self, unit_dict: Dict[UnitTypeId, List[Unit]], unit: Unit):
        if not unit.type_id in unit_dict:
            unit_dict[unit.type_id] = [unit]
        else:
            unit_dict[unit.type_id].append(unit)

    @property
    def enemy_army_value(self) -> int:
        """Combined mineral and vespene cost of the enemy army.

        Returns
        -------
        int :
            Total resource value of the enemy army.

        """
        value: int = 0
        for cache_info in self.enemy_army_tag_dict.values():
            unit_cost = self.ai.calculate_unit_value(cache_info.unit_type)
            value += unit_cost.minerals + unit_cost.vespene
        return value

    @property
    def own_army_value(self) -> int:
        """Combined mineral and vespene cost of the enemy army.

        Returns
        -------
        int :
            Total resource value of the enemy army.

        """
        value: int = 0
        for unit in self.own_army:
            unit_cost = self.ai.calculate_unit_value(unit.type_id)
            value += unit_cost.minerals + (unit_cost.vespene*2)
        return value

    async def on_step(self, iteration: int):
        pass

    async def on_unit_created(self, unit: Unit):
        pass

    async def on_unit_destroyed(self, unit_tag: int):

        cache_info: Optional[UnitCacheInfo] = None

        if unit_tag in self.enemy_structure_tag_dict:
            cache_info = self.enemy_structure_tag_dict[unit_tag]
            del self.enemy_structure_tag_dict[unit_tag]
        elif unit_tag in self.enemy_worker_tag_dict:
            cache_info = self.enemy_worker_tag_dict[unit_tag]
            del self.enemy_worker_tag_dict[unit_tag]
        elif unit_tag in self.enemy_army_tag_dict:
            cache_info = self.enemy_army_tag_dict[unit_tag]
            del self.enemy_army_tag_dict[unit_tag]

        if (
            cache_info
            and cache_info.unit_type in self.enemy_type_dict
            and unit_tag in self.enemy_type_dict[cache_info.unit_type]
        ):
            self.enemy_type_dict[cache_info.unit_type].remove(unit_tag)
