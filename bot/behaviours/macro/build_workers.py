from typing import Dict, TYPE_CHECKING

from sc2.ids.unit_typeid import UnitTypeId

from bot.behaviours.macro.macro_behaviour import MacroBehaviour
from bot.jeroen_bot_settings import JeroenBotSettings

if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot


class BuildWorkers(MacroBehaviour):

    def __init__(self):
        super().__init__()

    def execute(self, ai: "JeroenBot") -> bool:

        worker_count = ai.unit_manager.own_workers.amount + ai.already_pending(ai.race_worker)

        if not ai.resource_manager.can_afford(ai.race_worker) or worker_count >= JeroenBotSettings.MAX_WORKERS:
            return False

        for townhall in ai.townhalls.ready.idle:
            townhall.train(ai.race_worker)
            return True

        return False

