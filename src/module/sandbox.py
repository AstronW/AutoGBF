from module.battle import Battle
import time
import yaml
from logger import logger
import traceback


URL_HOME = "https://game.granbluefantasy.jp/#mypage"
URL_ZONE = [
    "https://game.granbluefantasy.jp/#replicard/stage/2",
    "https://game.granbluefantasy.jp/#replicard/stage/3",
    "https://game.granbluefantasy.jp/#replicard/stage/4",
    "https://game.granbluefantasy.jp/#replicard/stage/5",
    "https://game.granbluefantasy.jp/#replicard/stage/6",
    "https://game.granbluefantasy.jp/#replicard/stage/7",
    "https://game.granbluefantasy.jp/#replicard/stage/8",
    "https://game.granbluefantasy.jp/#replicard/stage/9",
    "https://game.granbluefantasy.jp/#replicard/stage/10",
]
ENEMY_LIST = "#cnt-division > div > div.prt-division-list > div"
BTN_OK = "#pop > div > div.prt-popup-footer > div.btn-usual-ok"
BTN_SUP_OK = "#wrapper > div.contents > div.pop-deck > div.prt-btn-deck > div.btn-usual-ok"


class Sandbox(Battle):

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.driver = self.parent.driver.driver

    def start_mission(self):
        try:
            with open("config.yaml") as f:
                self.data = yaml.load(f, Loader=yaml.FullLoader)
            url = self.data["sandbox"]["url"]
            zone = self.data["sandbox"]["zone"]
            buff = self.data["sandbox"]["buff"]
            repeat_times = self.data["sandbox"]["repeat_times"]
            treasure_id = self.data["sandbox"]["treasure_id"]
            treasure_count = self.data["sandbox"]["treasure_count"]
            logger.info("=" * 28)
            logger.attr("zone", zone)
            logger.attr("method", buff)
            logger.attr("repeat_times", repeat_times)
            logger.attr("treasure_id", treasure_id)
            logger.attr("treasure_count", treasure_count)

            time.sleep(1)

            count = 0
            count_buff = 0

            while (
                (not repeat_times + treasure_count)
                | (repeat_times > count)
                | (self.find_treasure(treasure_id) < treasure_count)
            ):
                logger.info('-' * 50)
                logger.info(f"开始第{count+1}次任务")
                self.get_url(url)
                time.sleep(1)
                if self.find_pop():
                    self.send_code()
                    time.sleep(1)
                self.click_element(BTN_SUP_OK)
                logger.info("正在等待进入战斗界面")
                self.wait_url(["#raid", "#raid_multi"])
                logger.info("开始战斗")
                self.full_auto()
                logger.info("战斗结束")
                count += 1
                self.get_url(URL_ZONE[zone])
                enemy_list = self.find_element_list(ENEMY_LIST)
                enemy_count = len(enemy_list)
                logger.info(f"敌人数量：{enemy_count}")
                if enemy_count > 2:
                    if "chest" in self.get_attribute(enemy_list[0], "class"):
                        enemy_list[0].click()
                        time.sleep(1)
                        self.click_element(BTN_OK)
                        time.sleep(0.5)
                        self.driver.refresh()
                        time.sleep(0.5)
                        enemy_list = self.find_element_list(ENEMY_LIST)
                        if len(enemy_list) == enemy_count:
                            logger.info("进入宝箱怪战斗")
                            time.sleep(0.2)
                            if self.find_pop():
                                self.send_code()
                                time.sleep(1)
                            enemy_list[0].click()
                            self.click_element(BTN_SUP_OK)
                            self.wait_url(["#raid", "#raid_multi"])
                            logger.info("宝箱怪战斗开始")
                            self.full_auto()
                            logger.info("宝箱怪战斗结束")
                            time.sleep(2)
                    elif (buff > count_buff):
                        enemy_list[0].click()
                        logger.info("进入buff怪战斗")
                        time.sleep(0.2)
                        if self.find_pop():
                            self.send_code()
                            time.sleep(1)
                        self.click_element(BTN_SUP_OK)
                        self.wait_url(["#raid", "#raid_multi"])
                        logger.info("buff怪战斗开始")
                        self.full_auto()
                        logger.info("buff怪战斗结束")
                        time.sleep(2)
                        count_buff += 1
                    elif not buff:
                        enemy_list[0].click()
                        logger.info("进入buff怪战斗")
                        time.sleep(0.2)
                        if self.find_pop():
                            self.send_code()
                            time.sleep(1)
                        self.click_element(BTN_SUP_OK)
                        self.wait_url(["#raid", "#raid_multi"])
                        logger.info("buff怪战斗开始")
                        self.full_auto()
                        logger.info("buff怪战斗结束")
                        time.sleep(2)
                if self.parent.quit is True:
                    break
                time.sleep(1)
            logger.info('-' * 50)
            logger.info("任务已结束")
            self.get_url(URL_HOME)
        except Exception as e:
            logger.error(e)
            logger.debug("\n" + traceback.format_exc())
