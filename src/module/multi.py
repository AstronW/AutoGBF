from ..autogbf import AutoGBF
from ..utils.logger import logger
from ..autogbf.metadata.status import Status
from ..autogbf.metadata.constants import Url, Loc


class Multi(AutoGBF):
    def __init__(self):
        super().__init__()

    def check_reward(self):
        self.page.get(Url.PENDING_BATTLE)
        while True:
            if ele := self.page.ele(Loc.BTN_REWARD_RAID, timeout=5):
                ele.click()
                self.page.listen.wait(timeout=10)
                return
            self.page.refresh()
            self.page.wait.doc_loaded()
            self.page.stop_loading()

    def start_mission(self, data: dict):
        # method = data.get("method")
        hp_min = data.get("boss_hp")[0]
        hp_max = data.get("boss_hp")[1]
        join_min = data.get("player_count")[0]
        join_max = data.get("player_count")[1]
        repeat_times = data.get("repeat_count")
        treasure_id = data.get("treasure_id")
        treasure_count = data.get("treasure_count")
        goal_turn = data.get("target_turn")
        custom = data.get("custom_battle")

        count = 0
        count_wait_raid = 0
        max_wait = 3 if goal_turn else 1

        self.start_listen()
        while (
            (not repeat_times + treasure_count)
            | (count < repeat_times)
            | (self.find_treasure(treasure_id) < treasure_count)
        ):
            logger.info(f"开始第{count+1}次任务")
            self.find_raid((hp_min, hp_max, join_min, join_max))
            while not self.check_party():
                self.find_raid((hp_min, hp_max, join_min, join_max))
            status = self.start_battle(goal_turn, custom)
            logger.info(f"战斗结果是{status}")
            if status in [Status.BATTLE_LOSE, Status.BATTLE_TURN_ENOUGH]:
                count_wait_raid += 1
            elif status == Status.BATTLE_RESULT_EMPTY:
                count -= 1

            count += 1

            if count_wait_raid >= max_wait:
                self.check_reward()
                count_wait_raid -= 1

            if data.get("stop"):
                self.get_home()
                return

            logger.info("-" * 20)
        self.get_home()
