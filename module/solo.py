from autogbf import AutoGBF
from config import ConfigManager
from logger import logger


class Solo(AutoGBF):
    def __init__(self):
        super().__init__()

    def start_mission(self, data : dict):
        url = data.get("url")
        summon_id = data.get("summon_id")
        repeat_times = data.get("repeat_times")
        treasure_id = data.get("treasure_id")
        treasure_count = data.get("treasure_count")
        count = 0
        self.start_listen()
        while (
            (not repeat_times + treasure_count)
            | (repeat_times > count)
            | (self.find_treasure(treasure_id) < treasure_count)
        ):
            logger.info(f"开始第{count+1}次任务")
            if self.page.url != url:
                self.page.get(url)
            else:
                self.page.refresh()
                self.page.wait.doc_loaded()
            self.find_summon(summon_id)
            self.start_battle()
            count += 1
            logger.info("-"*20)

if __name__ == "__main__":
    data = ConfigManager("solo")
    solo = Solo()
    solo.start_mission(data)
