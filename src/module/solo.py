from autogbf import AutoGBF
from config import ConfigManager
import time
import logging
logger = logging.getLogger("autogbf")


class Solo(AutoGBF):

    def __init__(self, parent=None):
        AutoGBF.__init__(self)
        self.parent = parent

    def start(self):
        data = ConfigManager("solo")
        url = data.get_config("url")
        summon_id = data.get_config("summon_id")
        repeat_times = data.get_config("repeat_times")
        treasure_id = data.get_config("treasure_id")
        treasure_count = data.get_config("treasure_count")
        custom = data.get_config("custom")
        logger.hr(1)
        logger.attr("url", url[32:])
        logger.attr("summon_id", summon_id)
        if repeat_times != 0:
            logger.attr("repeat_times", repeat_times)
        if treasure_count != 0:
            logger.attr("treasure_id", treasure_id)
            logger.attr("treasure_count", treasure_count)
        if custom != "无":
            logger.attr("custom", custom)

        count = 0

        while (
            (not repeat_times + treasure_count)
            | (repeat_times > count)
            | (self.find_treasure(treasure_id) < treasure_count)
        ):
            logger.hr(2)
            time_start = time.time()
            logger.info(f"开始第{count+1}次任务")
            self.get(url)
            self.find_summon(summon_id)
            try:
                self.battle(custom=custom)
            except Exception:
                logger.exception("战斗失败")
            count += 1
            time_stop = time.time()
            time_cost = time.strftime("%H:%M:%S", time.gmtime(time_stop - time_start))
            logger.info(f"任务结束，用时{time_cost}")
            if self.parent.quit is True:
                return


if __name__ == "__main__":
    mission = Solo()
    mission.start()
