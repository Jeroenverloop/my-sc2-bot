from typing import Dict, Set

from sc2.data import Race
from sc2.ids.unit_typeid import UnitTypeId

RACE_GAS: Dict[Race, UnitTypeId] = {
    Race.Protoss: UnitTypeId.ASSIMILATOR,
    Race.Terran: UnitTypeId.REFINERY,
    Race.Zerg: UnitTypeId.EXTRACTOR,
}

RACE_TOWNHALLS_BASE: Dict[Race, UnitTypeId] = {
    Race.Protoss: UnitTypeId.NEXUS,
    Race.Terran: UnitTypeId.COMMANDCENTER,
    Race.Zerg: UnitTypeId.HATCHERY,
}

RACE_TOWNHALLS: Dict[Race, Set[UnitTypeId]] = {
    Race.Protoss: {UnitTypeId.NEXUS},
    Race.Terran: {
        UnitTypeId.COMMANDCENTER,
        UnitTypeId.ORBITALCOMMAND,
        UnitTypeId.PLANETARYFORTRESS,
        UnitTypeId.COMMANDCENTERFLYING,
        UnitTypeId.ORBITALCOMMANDFLYING,
    },
    Race.Zerg: {UnitTypeId.HATCHERY, UnitTypeId.LAIR, UnitTypeId.HIVE},
    Race.Random: {
        # Protoss
        UnitTypeId.NEXUS,
        # Terran
        UnitTypeId.COMMANDCENTER,
        UnitTypeId.ORBITALCOMMAND,
        UnitTypeId.PLANETARYFORTRESS,
        UnitTypeId.COMMANDCENTERFLYING,
        UnitTypeId.ORBITALCOMMANDFLYING,
        # Zerg
        UnitTypeId.HATCHERY,
        UnitTypeId.LAIR,
        UnitTypeId.HIVE,
    },
}

TOWNHALL_TYPES: Set[UnitTypeId] = {
    UnitTypeId.HATCHERY,
    UnitTypeId.LAIR,
    UnitTypeId.HIVE,
    UnitTypeId.COMMANDCENTER,
    UnitTypeId.COMMANDCENTERFLYING,
    UnitTypeId.ORBITALCOMMAND,
    UnitTypeId.ORBITALCOMMANDFLYING,
    UnitTypeId.PLANETARYFORTRESS,
    UnitTypeId.NEXUS,
}

REQUIRE_POWER_STRUCTURE_TYPES: set[UnitTypeId] = {
    UnitTypeId.PHOTONCANNON,
    UnitTypeId.SHIELDBATTERY,
    UnitTypeId.GATEWAY,
    UnitTypeId.WARPGATE,
    UnitTypeId.ROBOTICSFACILITY,
    UnitTypeId.ROBOTICSBAY,
    UnitTypeId.STARGATE,
    UnitTypeId.CYBERNETICSCORE,
    UnitTypeId.FORGE,
    UnitTypeId.TEMPLARARCHIVE,
    UnitTypeId.FLEETBEACON,
    UnitTypeId.TWILIGHTCOUNCIL,
    UnitTypeId.DARKSHRINE,
}


STRUCTURES: set[UnitTypeId] = {
    UnitTypeId.NEXUS,
    UnitTypeId.ASSIMILATOR,
    UnitTypeId.PYLON,
    UnitTypeId.GATEWAY,
    UnitTypeId.FORGE,
    UnitTypeId.CYBERNETICSCORE,
    UnitTypeId.PHOTONCANNON,
    UnitTypeId.SHIELDBATTERY,
    UnitTypeId.TWILIGHTCOUNCIL,
    UnitTypeId.STARGATE,
    UnitTypeId.ROBOTICSFACILITY,
    UnitTypeId.TEMPLARARCHIVE,
    UnitTypeId.DARKSHRINE,
    UnitTypeId.FLEETBEACON,
    UnitTypeId.ROBOTICSBAY,
}

GAS_BUILDINGS: Set[UnitTypeId] = {
    UnitTypeId.ASSIMILATOR,
    UnitTypeId.EXTRACTOR,
    UnitTypeId.REFINERY,
    UnitTypeId.ASSIMILATORRICH,
    UnitTypeId.EXTRACTORRICH,
    UnitTypeId.REFINERYRICH,
}

STRUCTURE_NEEDED_FOR_STRUCTURE: Dict[UnitTypeId, UnitTypeId] = {

    UnitTypeId.PYLON: UnitTypeId.NEXUS,
    UnitTypeId.GATEWAY: UnitTypeId.PYLON,
    UnitTypeId.FORGE: UnitTypeId.PYLON,

    UnitTypeId.CYBERNETICSCORE: UnitTypeId.GATEWAY,
    UnitTypeId.SHIELDBATTERY: UnitTypeId.GATEWAY,
    UnitTypeId.PHOTONCANNON: UnitTypeId.FORGE,

    UnitTypeId.ROBOTICSFACILITY: UnitTypeId.CYBERNETICSCORE,
    UnitTypeId.STARGATE: UnitTypeId.CYBERNETICSCORE,
    UnitTypeId.TWILIGHTCOUNCIL: UnitTypeId.CYBERNETICSCORE,

    UnitTypeId.TEMPLARARCHIVE: UnitTypeId.TWILIGHTCOUNCIL,
    UnitTypeId.DARKSHRINE: UnitTypeId.TWILIGHTCOUNCIL,
    UnitTypeId.FLEETBEACON: UnitTypeId.STARGATE,
    UnitTypeId.ROBOTICSBAY: UnitTypeId.ROBOTICSFACILITY
}