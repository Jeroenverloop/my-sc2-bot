from typing import Dict, Set, TYPE_CHECKING

from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId

UPGRADE_NEEDED_FOR_UPGRADE: Dict[UpgradeId, UpgradeId] = {

    UpgradeId.PROTOSSAIRARMORSLEVEL2: UpgradeId.PROTOSSAIRARMORSLEVEL1,
    UpgradeId.PROTOSSAIRARMORSLEVEL3: UpgradeId.PROTOSSAIRARMORSLEVEL2,

    UpgradeId.PROTOSSAIRWEAPONSLEVEL2: UpgradeId.PROTOSSAIRWEAPONSLEVEL1,
    UpgradeId.PROTOSSAIRWEAPONSLEVEL3: UpgradeId.PROTOSSAIRWEAPONSLEVEL2,

    UpgradeId.PROTOSSSHIELDSLEVEL2: UpgradeId.PROTOSSSHIELDSLEVEL1,
    UpgradeId.PROTOSSSHIELDSLEVEL3: UpgradeId.PROTOSSSHIELDSLEVEL2,

    UpgradeId.PROTOSSGROUNDWEAPONSLEVEL2: UpgradeId.PROTOSSGROUNDWEAPONSLEVEL1,
    UpgradeId.PROTOSSGROUNDWEAPONSLEVEL3: UpgradeId.PROTOSSGROUNDWEAPONSLEVEL2,

    UpgradeId.PROTOSSGROUNDARMORSLEVEL2: UpgradeId.PROTOSSGROUNDARMORSLEVEL1,
    UpgradeId.PROTOSSGROUNDARMORSLEVEL3: UpgradeId.PROTOSSGROUNDARMORSLEVEL2,
}

PROTOSS_GROUND_UPGRADES: Set[UpgradeId] = {
    UpgradeId.PROTOSSGROUNDARMORSLEVEL1,
    UpgradeId.PROTOSSGROUNDARMORSLEVEL2,
    UpgradeId.PROTOSSGROUNDARMORSLEVEL3,
    UpgradeId.PROTOSSGROUNDWEAPONSLEVEL1,
    UpgradeId.PROTOSSGROUNDWEAPONSLEVEL2,
    UpgradeId.PROTOSSGROUNDWEAPONSLEVEL3,
    UpgradeId.PROTOSSSHIELDSLEVEL1,
    UpgradeId.PROTOSSSHIELDSLEVEL2,
    UpgradeId.PROTOSSSHIELDSLEVEL3,
}

PROTOSS_AIR_UPGRADES: Set[UpgradeId] = {
    UpgradeId.PROTOSSAIRARMORSLEVEL1,
    UpgradeId.PROTOSSAIRARMORSLEVEL2,
    UpgradeId.PROTOSSAIRARMORSLEVEL3,
    UpgradeId.PROTOSSAIRWEAPONSLEVEL1,
    UpgradeId.PROTOSSAIRWEAPONSLEVEL2,
    UpgradeId.PROTOSSAIRWEAPONSLEVEL3,
    UpgradeId.PROTOSSSHIELDSLEVEL1,
    UpgradeId.PROTOSSSHIELDSLEVEL2,
    UpgradeId.PROTOSSSHIELDSLEVEL3,
}

UNIT_BENEFITTING_UPGRADES: Dict[UnitTypeId, Set[UpgradeId]] = {
    UnitTypeId.ZEALOT: {UpgradeId.CHARGE, UpgradeId.WARPGATERESEARCH},
    UnitTypeId.STALKER: {UpgradeId.BLINKTECH, UpgradeId.WARPGATERESEARCH},
    UnitTypeId.SENTRY: {UpgradeId.WARPGATERESEARCH},
    UnitTypeId.ADEPT: {UpgradeId.ADEPTPIERCINGATTACK, UpgradeId.WARPGATERESEARCH},
    UnitTypeId.HIGHTEMPLAR: {UpgradeId.PSISTORMTECH, UpgradeId.WARPGATERESEARCH},
    UnitTypeId.ARCHON: {UpgradeId.WARPGATERESEARCH},
    UnitTypeId.DARKTEMPLAR: {UpgradeId.DARKTEMPLARBLINKUPGRADE, UpgradeId.WARPGATERESEARCH},
    UnitTypeId.IMMORTAL: {},
    UnitTypeId.COLOSSUS: {UpgradeId.EXTENDEDTHERMALLANCE},
    UnitTypeId.OBSERVER: {UpgradeId.OBSERVERGRAVITICBOOSTER},
    UnitTypeId.WARPPRISM: {UpgradeId.GRAVITICDRIVE},
    UnitTypeId.PHOENIX: {UpgradeId.PHOENIXRANGEUPGRADE},
    UnitTypeId.VOIDRAY: {UpgradeId.VOIDRAYSPEEDUPGRADE},
    UnitTypeId.ORACLE: {},
    UnitTypeId.TEMPEST: {UpgradeId.TEMPESTGROUNDATTACKUPGRADE},
    UnitTypeId.CARRIER: {},
    UnitTypeId.MOTHERSHIP: {}
}

UNIT_BENEFITTING_UPGRADES[UnitTypeId.ZEALOT].update(PROTOSS_GROUND_UPGRADES)
UNIT_BENEFITTING_UPGRADES[UnitTypeId.STALKER].update(PROTOSS_GROUND_UPGRADES)
UNIT_BENEFITTING_UPGRADES[UnitTypeId.SENTRY].update(PROTOSS_GROUND_UPGRADES)
UNIT_BENEFITTING_UPGRADES[UnitTypeId.ADEPT].update(PROTOSS_GROUND_UPGRADES)
UNIT_BENEFITTING_UPGRADES[UnitTypeId.HIGHTEMPLAR].update(PROTOSS_GROUND_UPGRADES)
UNIT_BENEFITTING_UPGRADES[UnitTypeId.ARCHON].update(PROTOSS_GROUND_UPGRADES)
UNIT_BENEFITTING_UPGRADES[UnitTypeId.DARKTEMPLAR].update(PROTOSS_GROUND_UPGRADES)
UNIT_BENEFITTING_UPGRADES[UnitTypeId.IMMORTAL] = PROTOSS_GROUND_UPGRADES
UNIT_BENEFITTING_UPGRADES[UnitTypeId.COLOSSUS].update(PROTOSS_GROUND_UPGRADES)

UNIT_BENEFITTING_UPGRADES[UnitTypeId.OBSERVER].update(PROTOSS_AIR_UPGRADES)
UNIT_BENEFITTING_UPGRADES[UnitTypeId.PHOENIX].update(PROTOSS_AIR_UPGRADES)
UNIT_BENEFITTING_UPGRADES[UnitTypeId.VOIDRAY].update(PROTOSS_AIR_UPGRADES)
UNIT_BENEFITTING_UPGRADES[UnitTypeId.ORACLE] = PROTOSS_AIR_UPGRADES
UNIT_BENEFITTING_UPGRADES[UnitTypeId.TEMPEST].update(PROTOSS_AIR_UPGRADES)
UNIT_BENEFITTING_UPGRADES[UnitTypeId.CARRIER] = PROTOSS_AIR_UPGRADES
UNIT_BENEFITTING_UPGRADES[UnitTypeId.MOTHERSHIP] = PROTOSS_AIR_UPGRADES



STRUCTURE_NEEDED_FOR_UPGRADE: Dict[UpgradeId, UnitTypeId] = {
    UpgradeId.ADEPTPIERCINGATTACK: UnitTypeId.TWILIGHTCOUNCIL,
    UpgradeId.BLINKTECH: UnitTypeId.TWILIGHTCOUNCIL,
    UpgradeId.CHARGE: UnitTypeId.TWILIGHTCOUNCIL,
    UpgradeId.EXTENDEDTHERMALLANCE: UnitTypeId.ROBOTICSBAY,
    UpgradeId.DARKTEMPLARBLINKUPGRADE: UnitTypeId.DARKSHRINE,
    UpgradeId.GRAVITICDRIVE: UnitTypeId.ROBOTICSBAY,
    UpgradeId.OBSERVERGRAVITICBOOSTER: UnitTypeId.ROBOTICSBAY,
    UpgradeId.PHOENIXRANGEUPGRADE: UnitTypeId.FLEETBEACON,
    UpgradeId.PROTOSSAIRARMORSLEVEL1: UnitTypeId.CYBERNETICSCORE,
    UpgradeId.PROTOSSAIRARMORSLEVEL2: UnitTypeId.FLEETBEACON,
    UpgradeId.PROTOSSAIRARMORSLEVEL3: UnitTypeId.FLEETBEACON,
    UpgradeId.PROTOSSAIRWEAPONSLEVEL1: UnitTypeId.CYBERNETICSCORE,
    UpgradeId.PROTOSSAIRWEAPONSLEVEL2: UnitTypeId.FLEETBEACON,
    UpgradeId.PROTOSSAIRWEAPONSLEVEL3: UnitTypeId.FLEETBEACON,
    UpgradeId.PROTOSSGROUNDARMORSLEVEL1: UnitTypeId.FORGE,
    UpgradeId.PROTOSSGROUNDARMORSLEVEL2: UnitTypeId.TWILIGHTCOUNCIL,
    UpgradeId.PROTOSSGROUNDARMORSLEVEL3: UnitTypeId.TWILIGHTCOUNCIL,
    UpgradeId.PROTOSSGROUNDWEAPONSLEVEL1: UnitTypeId.FORGE,
    UpgradeId.PROTOSSGROUNDWEAPONSLEVEL2: UnitTypeId.TWILIGHTCOUNCIL,
    UpgradeId.PROTOSSGROUNDWEAPONSLEVEL3: UnitTypeId.TWILIGHTCOUNCIL,
    UpgradeId.PROTOSSSHIELDSLEVEL1: UnitTypeId.FORGE,
    UpgradeId.PROTOSSSHIELDSLEVEL2: UnitTypeId.TWILIGHTCOUNCIL,
    UpgradeId.PROTOSSSHIELDSLEVEL3: UnitTypeId.TWILIGHTCOUNCIL,
    UpgradeId.PSISTORMTECH: UnitTypeId.TEMPLARARCHIVE,
    UpgradeId.TEMPESTGROUNDATTACKUPGRADE: UnitTypeId.FLEETBEACON,
    UpgradeId.VOIDRAYSPEEDUPGRADE: UnitTypeId.FLEETBEACON,
    UpgradeId.WARPGATERESEARCH: UnitTypeId.CYBERNETICSCORE,
}

UPGRADE_RESEARCHED_FROM: Dict[UpgradeId, UnitTypeId] = {
    UpgradeId.ADEPTPIERCINGATTACK: UnitTypeId.TWILIGHTCOUNCIL,
    UpgradeId.ANABOLICSYNTHESIS: UnitTypeId.ULTRALISKCAVERN,
    UpgradeId.BANSHEECLOAK: UnitTypeId.STARPORTTECHLAB,
    UpgradeId.BANSHEESPEED: UnitTypeId.STARPORTTECHLAB,
    UpgradeId.BATTLECRUISERENABLESPECIALIZATIONS: UnitTypeId.FUSIONCORE,
    UpgradeId.BLINKTECH: UnitTypeId.TWILIGHTCOUNCIL,
    UpgradeId.BURROW: UnitTypeId.HATCHERY,
    UpgradeId.CENTRIFICALHOOKS: UnitTypeId.BANELINGNEST,
    UpgradeId.CHARGE: UnitTypeId.TWILIGHTCOUNCIL,
    UpgradeId.CHITINOUSPLATING: UnitTypeId.ULTRALISKCAVERN,
    UpgradeId.DARKTEMPLARBLINKUPGRADE: UnitTypeId.DARKSHRINE,
    UpgradeId.DIGGINGCLAWS: UnitTypeId.LURKERDENMP,
    UpgradeId.DRILLCLAWS: UnitTypeId.FACTORYTECHLAB,
    UpgradeId.EVOLVEGROOVEDSPINES: UnitTypeId.HYDRALISKDEN,
    UpgradeId.EVOLVEMUSCULARAUGMENTS: UnitTypeId.HYDRALISKDEN,
    UpgradeId.EXTENDEDTHERMALLANCE: UnitTypeId.ROBOTICSBAY,
    UpgradeId.GLIALRECONSTITUTION: UnitTypeId.ROACHWARREN,
    UpgradeId.GRAVITICDRIVE: UnitTypeId.ROBOTICSBAY,
    UpgradeId.HIGHCAPACITYBARRELS: UnitTypeId.FACTORYTECHLAB,
    UpgradeId.HISECAUTOTRACKING: UnitTypeId.ENGINEERINGBAY,
    UpgradeId.HURRICANETHRUSTERS: UnitTypeId.FACTORYTECHLAB,
    UpgradeId.INTERFERENCEMATRIX: UnitTypeId.STARPORTTECHLAB,
    UpgradeId.LIBERATORAGRANGEUPGRADE: UnitTypeId.FUSIONCORE,
    UpgradeId.LURKERRANGE: UnitTypeId.LURKERDENMP,
    UpgradeId.MEDIVACCADUCEUSREACTOR: UnitTypeId.FUSIONCORE,
    UpgradeId.NEURALPARASITE: UnitTypeId.INFESTATIONPIT,
    UpgradeId.OBSERVERGRAVITICBOOSTER: UnitTypeId.ROBOTICSBAY,
    UpgradeId.OVERLORDSPEED: UnitTypeId.HATCHERY,
    UpgradeId.PERSONALCLOAKING: UnitTypeId.GHOSTACADEMY,
    UpgradeId.PHOENIXRANGEUPGRADE: UnitTypeId.FLEETBEACON,
    UpgradeId.PROTOSSAIRARMORSLEVEL1: UnitTypeId.CYBERNETICSCORE,
    UpgradeId.PROTOSSAIRARMORSLEVEL2: UnitTypeId.CYBERNETICSCORE,
    UpgradeId.PROTOSSAIRARMORSLEVEL3: UnitTypeId.CYBERNETICSCORE,
    UpgradeId.PROTOSSAIRWEAPONSLEVEL1: UnitTypeId.CYBERNETICSCORE,
    UpgradeId.PROTOSSAIRWEAPONSLEVEL2: UnitTypeId.CYBERNETICSCORE,
    UpgradeId.PROTOSSAIRWEAPONSLEVEL3: UnitTypeId.CYBERNETICSCORE,
    UpgradeId.PROTOSSGROUNDARMORSLEVEL1: UnitTypeId.FORGE,
    UpgradeId.PROTOSSGROUNDARMORSLEVEL2: UnitTypeId.FORGE,
    UpgradeId.PROTOSSGROUNDARMORSLEVEL3: UnitTypeId.FORGE,
    UpgradeId.PROTOSSGROUNDWEAPONSLEVEL1: UnitTypeId.FORGE,
    UpgradeId.PROTOSSGROUNDWEAPONSLEVEL2: UnitTypeId.FORGE,
    UpgradeId.PROTOSSGROUNDWEAPONSLEVEL3: UnitTypeId.FORGE,
    UpgradeId.PROTOSSSHIELDSLEVEL1: UnitTypeId.FORGE,
    UpgradeId.PROTOSSSHIELDSLEVEL2: UnitTypeId.FORGE,
    UpgradeId.PROTOSSSHIELDSLEVEL3: UnitTypeId.FORGE,
    UpgradeId.PSISTORMTECH: UnitTypeId.TEMPLARARCHIVE,
    UpgradeId.PUNISHERGRENADES: UnitTypeId.BARRACKSTECHLAB,
    UpgradeId.SHIELDWALL: UnitTypeId.BARRACKSTECHLAB,
    UpgradeId.SMARTSERVOS: UnitTypeId.FACTORYTECHLAB,
    UpgradeId.STIMPACK: UnitTypeId.BARRACKSTECHLAB,
    UpgradeId.TEMPESTGROUNDATTACKUPGRADE: UnitTypeId.FLEETBEACON,
    UpgradeId.TERRANBUILDINGARMOR: UnitTypeId.ENGINEERINGBAY,
    UpgradeId.TERRANINFANTRYARMORSLEVEL1: UnitTypeId.ENGINEERINGBAY,
    UpgradeId.TERRANINFANTRYARMORSLEVEL2: UnitTypeId.ENGINEERINGBAY,
    UpgradeId.TERRANINFANTRYARMORSLEVEL3: UnitTypeId.ENGINEERINGBAY,
    UpgradeId.TERRANINFANTRYWEAPONSLEVEL1: UnitTypeId.ENGINEERINGBAY,
    UpgradeId.TERRANINFANTRYWEAPONSLEVEL2: UnitTypeId.ENGINEERINGBAY,
    UpgradeId.TERRANINFANTRYWEAPONSLEVEL3: UnitTypeId.ENGINEERINGBAY,
    UpgradeId.TERRANSHIPWEAPONSLEVEL1: UnitTypeId.ARMORY,
    UpgradeId.TERRANSHIPWEAPONSLEVEL2: UnitTypeId.ARMORY,
    UpgradeId.TERRANSHIPWEAPONSLEVEL3: UnitTypeId.ARMORY,
    UpgradeId.TERRANVEHICLEANDSHIPARMORSLEVEL1: UnitTypeId.ARMORY,
    UpgradeId.TERRANVEHICLEANDSHIPARMORSLEVEL2: UnitTypeId.ARMORY,
    UpgradeId.TERRANVEHICLEANDSHIPARMORSLEVEL3: UnitTypeId.ARMORY,
    UpgradeId.TERRANVEHICLEWEAPONSLEVEL1: UnitTypeId.ARMORY,
    UpgradeId.TERRANVEHICLEWEAPONSLEVEL2: UnitTypeId.ARMORY,
    UpgradeId.TERRANVEHICLEWEAPONSLEVEL3: UnitTypeId.ARMORY,
    UpgradeId.TUNNELINGCLAWS: UnitTypeId.ROACHWARREN,
    UpgradeId.VOIDRAYSPEEDUPGRADE: UnitTypeId.FLEETBEACON,
    UpgradeId.WARPGATERESEARCH: UnitTypeId.CYBERNETICSCORE,
    UpgradeId.ZERGFLYERARMORSLEVEL1: UnitTypeId.SPIRE,
    UpgradeId.ZERGFLYERARMORSLEVEL2: UnitTypeId.SPIRE,
    UpgradeId.ZERGFLYERARMORSLEVEL3: UnitTypeId.SPIRE,
    UpgradeId.ZERGFLYERWEAPONSLEVEL1: UnitTypeId.SPIRE,
    UpgradeId.ZERGFLYERWEAPONSLEVEL2: UnitTypeId.SPIRE,
    UpgradeId.ZERGFLYERWEAPONSLEVEL3: UnitTypeId.SPIRE,
    UpgradeId.ZERGGROUNDARMORSLEVEL1: UnitTypeId.EVOLUTIONCHAMBER,
    UpgradeId.ZERGGROUNDARMORSLEVEL2: UnitTypeId.EVOLUTIONCHAMBER,
    UpgradeId.ZERGGROUNDARMORSLEVEL3: UnitTypeId.EVOLUTIONCHAMBER,
    UpgradeId.ZERGLINGATTACKSPEED: UnitTypeId.SPAWNINGPOOL,
    UpgradeId.ZERGLINGMOVEMENTSPEED: UnitTypeId.SPAWNINGPOOL,
    UpgradeId.ZERGMELEEWEAPONSLEVEL1: UnitTypeId.EVOLUTIONCHAMBER,
    UpgradeId.ZERGMELEEWEAPONSLEVEL2: UnitTypeId.EVOLUTIONCHAMBER,
    UpgradeId.ZERGMELEEWEAPONSLEVEL3: UnitTypeId.EVOLUTIONCHAMBER,
    UpgradeId.ZERGMISSILEWEAPONSLEVEL1: UnitTypeId.EVOLUTIONCHAMBER,
    UpgradeId.ZERGMISSILEWEAPONSLEVEL2: UnitTypeId.EVOLUTIONCHAMBER,
    UpgradeId.ZERGMISSILEWEAPONSLEVEL3: UnitTypeId.EVOLUTIONCHAMBER
}
