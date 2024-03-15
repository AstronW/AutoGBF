from module.battle import Battle
from selector.battle import *  # noqa E501
from selector.base import *  # noqa E501
import time
import yaml
from logger import logger
import traceback


URL_HOME = "https://game.granbluefantasy.jp/#mypage"


class Solo(Battle):

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.driver = self.parent.driver.driver

    def start_mission(self):
        try:
            with open("config.yaml") as f:
                self.data = yaml.load(f, Loader=yaml.FullLoader)
            url = self.data["solo"]["url"]
            summon_id = self.data["solo"]["summon_id"]
            method = self.data["solo"]["method"]
            repeat_times = self.data["solo"]["repeat_times"]
            treasure_id = self.data["solo"]["treasure_id"]
            treasure_count = self.data["solo"]["treasure_count"]
            logger.info("=" * 28)
            logger.attr("summon_id", summon_id)
            logger.attr("method", method)
            logger.attr("repeat_times", repeat_times)
            logger.attr("treasure_id", treasure_id)
            logger.attr("treasure_count", treasure_count)

            time.sleep(1)

            count = 0

            while (
                (not repeat_times + treasure_count)
                | (repeat_times > count)
                | (self.find_treasure(treasure_id) < treasure_count)
            ):
                logger.info('-' * 50)
                logger.info(f"开始第{count+1}次任务")
                self.get_url(url)
                time.sleep(0.5)
                while not self.find_summon(summon_id):
                    self.get_url(url)
                    time.sleep(0.5)
                time.sleep(0.5)
                if "stage" in self.driver.current_url:
                    self.click_element(BTN_OK)  # noqa F405
                logger.info("正在等待进入战斗界面")
                self.wait_url(["#raid", "#raid_multi"])
                logger.info("开始战斗")
                if method == 1:
                    self.full_auto()
                else:
                    pass
                logger.info("战斗结束")
                count += 1

                if self.parent.quit is True:
                    break
                time.sleep(1)
            logger.info('-' * 50)
            logger.info("任务已结束")
            self.get_url(URL_HOME)
        except Exception as e:
            logger.error(e)
            logger.debug("\n" + traceback.format_exc())
