from autogbf import AutoGBF
from config import ConfigManager
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


class Sandbox(AutoGBF):

    def __init__(self, parent=None):
        AutoGBF.__init__(self)
        self.parent = parent

    def check_start(self, url):
        self.page.listen.start([RE_CHECK_SUM, RE_VER_CODE, RE_QUEST_CREATE])
        self.page.get(url)
        for packet in self.page.listen.steps(timeout=10):
            # logger.info(packet.url)
            if "/c/a?_=" in packet.url:
                if not packet.response.body.get("is_correct"):
                    res, image = self.send_code()
                else:
                    cv2.imwrite(f"assets/img/{res}.png", image)
                    self.page.wait(1)
                    logger.info("验证码正确")
                    break
            elif "quest/decks_info" in packet.url:
                if packet.response.body is None:
                    self.page.refresh()
                elif "popup" in packet.response.body:
                    res, image = self.send_code()
                else:
                    # logger.info("wu")
                    break
        # self.page.listen.stop()
        while True:
            self.page.ele(BTN_OK).click()
            packet = self.page.listen.wait(timeout=5)
            if packet:
                self.page.listen.stop()
                break
        self.page.wait.url_change("#raid", timeout=5)
        return

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

    def _start(self):
        data = ConfigManager("sandbox")
        url = data.get_config("url")
        repeat_times = data.get_config("repeat_times")
        treasure_id = data.get_config("treasure_id")
        treasure_count = data.get_config("treasure_count")
        goal_buff = data.get_config("buff")
        custom = data.get_config("custom")
        logger.hr(1)
        logger.attr("url", url[32:])
        if goal_buff:
            logger.attr("goal_buff", goal_buff)
        if repeat_times:
            logger.attr("repeat_times", repeat_times)
        if treasure_count:
            logger.attr("treasure_id", treasure_id)
            logger.attr("treasure_count", treasure_count)
        if custom != "无":
            logger.attr("custom", custom)

        self.url_buff = None
        self.url_chest = None
        self.enable_buff = True
        init_flag = True
        count = 0
        count_buff = 0

        while (
            (not repeat_times + treasure_count)
            | (repeat_times > count)
            | (self.find_treasure(treasure_id) < treasure_count)
        ):
            logger.hr(2)
            time_start = time.time()
            logger.info(f"开始第{count+1}次任务")
            self.check_start(url)
            self.battle()
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

            if self.enable_buff and self.count_enemy and count_buff < goal_buff:
                for _ in range(goal_buff - count_buff):
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


if __name__ == "__main__":
    mission = Sandbox()
    mission.start()
