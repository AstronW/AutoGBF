from ..autogbf import AutoGBF
from ..utils.logger import logger


class Solo(AutoGBF):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

    def start_mission(self, data: dict):
        url = data.get("url")
        repeat_count = data.get("repeat_count")
        treasure_id = data.get("treasure_id")
        treasure_count = data.get("treasure_count")
        custom_battle = data.get("custom_battle")
        count = 0
        self.start_listen()
        while (
            (not repeat_count + treasure_count)
            | (count < repeat_count)
            | (self.find_treasure(treasure_id) < treasure_count)
        ):
            logger.info(f"开始第{count+1}次任务")
            if self.page.url != url:
                self.page.get(url)
            else:
                self.page.refresh()
                self.page.wait.doc_loaded()
            self.check_party()
            self.start_battle()
            count += 1
            logger.info("-" * 20)

            if data.get("stop"):
                return
