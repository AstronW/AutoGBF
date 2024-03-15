from module.battle import Battle
from selector.battle import *  # noqa E501
from selector.base import *  # noqa E501
import time
import yaml
from logger import logger
import traceback


URL_HOME = "https://game.granbluefantasy.jp/#mypage"
URL_TREASURE = "https://game.granbluefantasy.jp/#quest/extra"
URL_VH = "https://game.granbluefantasy.jp/#quest/supporter/510031/5"
URL_NM = "https://game.granbluefantasy.jp/#quest/supporter/510051/5"
KAGUYA_ID = "2040114000"
LIST_TREASURE_QUEST = '#cnt-normal-quest > div > div > div'


class Halo(Battle):

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.driver = self.parent.driver.driver

    def start_mission(self):
        try:
            with open("config.yaml") as f:
                self.data = yaml.load(f, Loader=yaml.FullLoader)
            summon_id = self.data["halo"]["summon_id"]
            repeat_times = self.data["halo"]["repeat_times"]
            treasure_id = self.data["halo"]["treasure_id"]
            treasure_count = self.data["halo"]["treasure_count"]
            logger.info("=" * 28)
            logger.attr("summon_id", summon_id)
            logger.attr("repeat_times", repeat_times)
            logger.attr("treasure_id", treasure_id)
            logger.attr("treasure_count", treasure_count)

            time.sleep(1)
            self.get_url(URL_TREASURE)
            list_treasure_quest = self.find_element_list(LIST_TREASURE_QUEST)
            number_base = len(list_treasure_quest)
            count = 0

            while (
                (not repeat_times + treasure_count)
                | (repeat_times > count)
                | (self.find_treasure(treasure_id) < treasure_count)
            ):
                logger.info('-' * 50)
                logger.info(f"开始第{count+1}次任务")
                self.get_url(URL_VH)
                time.sleep(0.5)
                self.find_summon(KAGUYA_ID)
                time.sleep(0.5)
                if "stage" in self.driver.current_url:
                    self.click_element(BTN_OK)  # noqa F405
                logger.info("正在等待进入战斗界面")
                self.wait_url(["#raid", "#raid_multi"])
                logger.info("开始战斗")
                self.full_auto()
                logger.info("战斗结束")
                count += 1

                self.get_url(URL_TREASURE)
                if len(self.find_element_list(LIST_TREASURE_QUEST)) > number_base:
                    logger.info("噩梦任务出现")
                    self.get_url(URL_NM)
                    self.find_summon(summon_id)
                    self.wait_url(["#raid", "#raid_multi"])
                    logger.info("噩梦战斗开始")
                    self.full_auto()
                    logger.info("噩梦战斗结束")

                if self.parent.quit is True:
                    break
                time.sleep(1)
            logger.info('-' * 50)
            logger.info("任务已结束")
            self.get_url(URL_HOME)
        except Exception as e:
            logger.error(e)
            logger.debug("\n" + traceback.format_exc())
