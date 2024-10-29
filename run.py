import random
import sys
from pathlib import Path
from typing import List

from sc2 import maps
from sc2.data import AIBuild, Difficulty, Race
from sc2.main import run_game
from sc2.player import Bot, Computer

from bot.jeroen_bot_settings import JeroenBotSettings

sys.path.append("ares-sc2/src/ares")
sys.path.append("ares-sc2/src")
sys.path.append("ares-sc2")


from bot.jeroen_bot import JeroenBot
from ladder import run_ladder_game

MAPS_PATH: str = "C:\\Program Files (x86)\\StarCraft II\\Maps"
MAP_FILE_EXT: str = "SC2Map"


def main():


    jeroen_bot:JeroenBot = JeroenBot()

    bot1 = Bot(JeroenBotSettings.RACE, jeroen_bot, JeroenBotSettings.NAME)

    if "--LadderServer" in sys.argv:
        # Ladder game started by LadderManager
        print("Starting ladder game...")
        result, opponent_id = run_ladder_game(bot1)
        print(result, " against opponent ", opponent_id)
    else:
        # Local game
        map_list: List[str] = [
            p.name.replace(f".{MAP_FILE_EXT}", "")
            for p in Path(MAPS_PATH).glob(f"*.{MAP_FILE_EXT}")
            if p.is_file()
        ]


        random_race = random.choice([Race.Zerg, Race.Terran, Race.Protoss])
        print("Starting local game...")
        run_game(
            maps.get(random.choice(map_list)),
            [
                bot1,
                Computer(random_race, Difficulty.VeryEasy, ai_build=AIBuild.Macro),
            ],
            realtime=False,
        )


# Start game
if __name__ == "__main__":
    main()
