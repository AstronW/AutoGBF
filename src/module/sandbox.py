from ..autogbf import AutoGBF
import time
import cv2
import logging

logger = logging.getLogger("autogbf")


BASE_URL = "https://game.granbluefantasy.jp/#"
BTN_OK = ".:btn-usual-ok"
BTN_QUEST = ".:prt-banner-wrapper"

RE_CHEST = "replicard/open_chest"
RE_START = "quest/create_quest"
RE_CHECK_SUM = "quest/decks_info"
RE_VER_CODE = "/c/a?_="
RE_QUEST_CREATE = "/quest/create_quest"


class SandBox(AutoGBF):

    def __init__(self, parent=None):
        AutoGBF.__init__(self)
        self.parent = parent

    def check_chest(self):
        self.page.get(BASE_URL + self.stage_url)
        self.page.listen.start(RE_CHEST)
        self.page.ele(BTN_QUEST).click()
        self.page.ele(BTN_OK).click()
        packet = self.page.listen.wait(timeout=10)
        self.page.listen.stop()
        if not packet.response.body.get("is_force_quest"):
            return
        else:
            self.page.refresh()
            if not self.url_chest:
                self.page.wait.doc_loaded()
                self.page.ele(BTN_QUEST).click()
                self.page.wait.load_start()
                self.url_chest = self.page.url
            self.check_start(self.url_chest)
            self.battle()
            return

    def check_buff(self):
        if not self.url_buff:
            self.page.get(BASE_URL + self.stage_url)
            if self.page.ele(".txt-quest-name").text != self.buff_name:
                self.enable_buff = False
                return
            self.page.ele(BTN_QUEST).click()
            self.page.wait.load_start()
            self.url_buff = self.page.url
        self.check_start(self.url_buff)
        self.battle()
        return

    def start_mission(self, data: dict):
        url = data.get("url")
        repeat_count = data.get("repeat_count")
        treasure_id = data.get("treasure_id")
        treasure_count = data.get("treasure_count")
        buff_count = data.get("buff_count")
        custom_battle = data.get("custom_battle")

        self.url_buff = None
        self.url_chest = None
        self.enable_buff = True
        init_flag = True
        count = 0
        count_buff = 0

        while (
            (not repeat_count + treasure_count)
            | (count < repeat_count)
            | (self.find_treasure(treasure_id) < treasure_count)
        ):
            time_start = time.time()
            logger.info(f"开始第{count+1}次任务")
            if self.page.url != url:
                self.page.get(url)
            else:
                self.page.refresh()
                self.page.wait.doc_loaded()
            self.check_party()
            self.start_battle()
            if init_flag:
                init_flag = False
                current_emeny = self.count_enemy
            if (not self.enable_buff) and self.count_enemy > current_emeny:
                self.enable_buff = True
            count += 1
            time_stop = time.time()
            time_cost = time.strftime("%H:%M:%S", time.gmtime(time_stop - time_start))
            logger.info(f"任务结束，用时{time_cost}")
            if self.parent.quit is True:
                return
            if self.is_chest:
                self.check_chest()

            if self.enable_buff and self.count_enemy and count_buff < buff_count:
                for _ in range(buff_count - count_buff):
                    self.check_buff()
                    if not self.enable_buff:
                        break
                    count_buff += 1
                    if self.parent.quit is True:
                        return

    def start(self):
        try:
            self._start()
        except Exception:
            logger.exception("Error in mission")
