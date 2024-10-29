from sc2.data import Race


class JeroenBotSettings:


    MAX_WORKERS: int = 80
    RACE: Race = Race.Protoss
    NAME: str = "Jeroen Bot"

    MINERAL_GAS_DISTRIBUTION: float = 2.7

    EXPAND_WHEN_MINERALS_LEFT: int = 3000
    EXPAND_WHEN_GAS_LEFT: int = 1500

    BUILD_WORKER_TIMEOUT: int = 120