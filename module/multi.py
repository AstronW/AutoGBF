from autogbf import AutoGBF
from config import ConfigManager
from logger import logger
from common.status import Status
from common.constants import Url, Loc


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
        summon_id = data.get("summon_id")
        method = data.get("method")
        hp_min = data.get("hp_min")
        hp_max = data.get("hp_max")
        join_min = data.get("join_min")
        join_max = data.get("join_max")
        repeat_times = data.get("repeat_times")
        treasure_id = data.get("treasure_id")
        treasure_count = data.get("treasure_count")
        goal_turn = data.get("goal_turn")
        custom = data.get("custom")

        count = 0
        count_wait_raid = 0
        max_wait = 3 if goal_turn else 1

        self.start_listen()
        while (
            (not repeat_times + treasure_count)
            | (repeat_times > count)
            | (self.find_treasure(treasure_id) < treasure_count)
        ):
            logger.info(f"开始第{count+1}次任务")
            self.find_raid((hp_min, hp_max, join_min, join_max), method)
            while not self.find_summon(summon_id):
                self.find_raid((hp_min, hp_max, join_min, join_max), method)
            status = self.start_battle(goal_turn, custom)
            if status in [Status.RAID_LOSE, Status.TURN_ENOUGH]:
                count_wait_raid += 1
            elif status == Status.RAID_EMPTY:
                count -= 1

            count += 1
            
            if count_wait_raid >= max_wait:
                self.check_reward()
                count_wait_raid -= 1

            logger.info("-"*20)

if __name__ == "__main__":
    data = ConfigManager("multi")
    multi = Multi()
    multi.start_mission(data)
