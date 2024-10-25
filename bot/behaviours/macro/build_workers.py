from typing import Dict, TYPE_CHECKING

from sc2.ids.unit_typeid import UnitTypeId

from bot.behaviours.macro.macro_behaviour import MacroBehaviour
from bot.jeroen_bot_settings import JeroenBotSettings

if TYPE_CHECKING:
    from bot.jeroen_bot import JeroenBot


class BuildWorkers(MacroBehaviour):

    def __init__(self):
        super().__init__()

    def execute(self, ai: "JeroenBot"):

        worker_count = ai.workers.amount + ai.already_pending(UnitTypeId.PROBE)

        if not ai.can_afford(UnitTypeId.PROBE) or worker_count >= JeroenBotSettings.MAX_WORKERS:
            return


        for nexus in ai.townhalls.ready.idle:
            nexus.train(UnitTypeId.PROBE)
            return

