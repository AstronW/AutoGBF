from autogbf import AutoGBF
from config import ConfigManager
import logging
logger = logging.getLogger("autogbf")


BTN_REWARD_RAID = ".:btn-multi-raid"
BTN_SWITCH = ".prt-search-switch-wrapper"

URL_PENDING_BATTLE = "https://game.granbluefantasy.jp/#quest/assist/unclaimed/0/0"
URL_MULTI_RAID = "https://game.granbluefantasy.jp/#quest/assist"

RE_MULTI_RESULT = "resultmulti/content/index"


class Multi(AutoGBF):

    def __init__(self, parent=None):
        AutoGBF.__init__(self)
        self.parent = parent
        self.count_wait_raid = 0

    def switch_raid(self, index : int) -> None:
        self.page.get(URL_MULTI_RAID)
        self.page.wait(2)
        self.page.ele(BTN_SWITCH, index=index).click()
        self.page.wait(2)

    def check_reward(self):
        self.page.listen.start(RE_MULTI_RESULT)
        while True:
            self.page.get(URL_PENDING_BATTLE)
            if ele := self.page.ele(BTN_REWARD_RAID, timeout=5):
                ele.click()
                packet = self.page.listen.wait(timeout=10)
                display_list = packet.response.body.get("display_list")
                if display_list:
                    for treasure in display_list.keys():
                        item_id = display_list.get(treasure).get("item_id")
                        number = int(display_list.get(treasure).get("number"))
                        self.list_treasure[item_id] = number
                self.page.listen.stop()
                return
            self.page.refresh()
            self.page.wait.doc_loaded()

    def _start(self) -> None:
        data = ConfigManager("multi")
        summon_id = data.get_config("summon_id")
        repeat_times = data.get_config("repeat_times")
        treasure_id = data.get_config("treasure_id")
        treasure_count = data.get_config("treasure_count")
        hp_upper = data.get_config("hp_upper")
        hp_lower = data.get_config("hp_lower")
        joined_upper = data.get_config("joined_upper")
        joined_lower = data.get_config("joined_lower")
        method = data.get_config("method")
        goal_turn = data.get_config("goal_turn")
        custom = data.get_config("custom")
        logger.hr(1)
        logger.attr("summon_id", summon_id)
        logger.attr("hp", f"[{hp_lower}, {hp_upper}]")
        logger.attr("joined", f"[{joined_lower}, {joined_upper}]")
        logger.attr("method", method)
        logger.attr("goal_turn", goal_turn)
        if repeat_times == 0:
            logger.attr("repeat_times", "∞")
        else:
            logger.attr("repeat_times", repeat_times)
        if treasure_count != 0:
            logger.attr("treasure_id", treasure_id)
            logger.attr("treasure_count", treasure_count)
        if custom != "无":
            logger.attr("custom", custom)
        logger.hr(1)

        count = 0
        max_wait = 3 if goal_turn else 1

        while (
            (not repeat_times + treasure_count)
            | (repeat_times > count)
            | (self.find_treasure(treasure_id) < treasure_count)
        ):
            logger.hr(2)
            logger.info(f"开始第{count+1}次任务")
            self.find_raid(hp_upper, hp_lower, joined_upper, joined_lower, method)
            while not self.find_summon(summon_id):
                self.find_raid(hp_upper, hp_lower, joined_upper, joined_lower, method)
            status = self.battle(goal_turn=goal_turn, custom=custom)
            if self.parent.quit is True:
                return
            if status == "lose" or status == "turn_over":
                self.count_wait_raid += 1
            elif status == "empty":
                count -= 1
            count += 1
            if self.count_wait_raid >= max_wait:
                self.check_reward()
                self.count_wait_raid -= 1

    def start(self):
        try:
            self._start()
        except Exception:
            logger.exception("任务失败，请检查配置文件")


if __name__ == "__main__":
    mission = Multi()
    mission.start()
