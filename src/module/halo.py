from autogbf import AutoGBF
from config import ConfigManager
import logging
logger = logging.getLogger("autogbf")


URL_VH = "https://game.granbluefantasy.jp/#quest/supporter/510031/5"
URL_NM = "https://game.granbluefantasy.jp/#quest/supporter/510051/5"

KAGUYA_ID = "2040114000"


class Halo(AutoGBF):

    def __init__(self, parent=None):
        AutoGBF.__init__(self)
        self.parent = parent

    def start(self):
        data = ConfigManager("halo")
        summon_id = data.get_config("summon_id")
        repeat_times = data.get_config("repeat_times")
        treasure_id = data.get_config("treasure_id")
        treasure_count = data.get_config("treasure_count")
        logger.hr(1)
        logger.attr("summon_id", summon_id)
        logger.attr("repeat_times", repeat_times)
        logger.attr("treasure_id", treasure_id)
        logger.attr("treasure_count", treasure_count)

        count = 0

        while (
            (not repeat_times + treasure_count)
            | (repeat_times > count)
            | (self.find_treasure(treasure_id) < treasure_count)
        ):
            logger.info('-' * 50)
            logger.info(f"开始第{count+1}次任务")
            self.page.get(URL_VH)
            self.find_summon(KAGUYA_ID)
            self.battle()
            if self.parent.quit is True:
                return
            count += 1

            if self.is_hell:
                self.page.get(URL_NM)
                self.find_summon(KAGUYA_ID)
                self.battle()


if __name__ == "__main__":
    mission = Halo()
    mission.start()
