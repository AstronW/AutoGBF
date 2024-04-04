from module.battle import Battle
import time
import yaml
import re
from logger import logger
import traceback


URL_MULTI_RAID = "https://game.granbluefantasy.jp/#quest/assist"
URL_HOME = "https://game.granbluefantasy.jp/#mypage"
URL_PENDING = 'https://game.granbluefantasy.jp/#quest/assist/unclaimed/0/0'

BP_COST = "#prt-search-list > div > div > div > div.prt-use-ap"
BP_CURRENT = "#cnt-quest > div.prt-user-status > div.prt-user-bp.se > div.prt-user-bp-value"
LIST_RAIDS = "#prt-search-list > div"
HP_LEFT = "div.prt-raid-info > div.prt-raid-status > div.prt-raid-gauge > div"
PLAYER_COUNT = "div.prt-raid-info > div.prt-raid-subinfo > div.prt-flees-in"
FP = 'div.prt-raid-info > div.prt-raid-status > div.prt-use-ap'
BTN_REFRESH = "#prt-assist-search > div.prt-module > div.btn-search-refresh"
PENDING_RAID = "#prt-unclaimed-list > div"

CHROME_HEIGHT = "return document.documentElement.scrollHeight"
SCROLL_INTO_VIEW = "arguments[0].scrollIntoView();"


class Multi(Battle):

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.driver = self.parent.driver.driver

    def find_raid(self, hp_upper, hp_lower, joined_upper, joined_lower, method):
        logger.info("正在寻找合适的副本")
        while True:
            h = self.driver.execute_script(CHROME_HEIGHT)
            offset = (h - 43) // 81 - 2
            firstpage = (h - 500) // 81
            ref = False
            current_bp = int(self.get_attribute(BP_CURRENT, "data-current-bp"))
            list_raids = self.find_element_list(LIST_RAIDS)
            list_raids.pop()
            if self.get_attribute(list_raids[0], "class") != "txt-no-multi":
                cost_bp = int(self.get_attribute(BP_COST, "data-ap-max"))
                if method == 2 and (cost_bp > current_bp):
                    for i in range(600 * (cost_bp - current_bp)):
                        time.sleep(1)
                        if self.parent.quit is True:
                            return
                    self.driver.refresh()
                    time.sleep(1)
                    continue
                raid_index = -1
                for i in range(len(list_raids)):
                    hp_left = int(re.split("[ %]", self.get_attribute(list_raids[i], HP_LEFT, "style"))[1])
                    player_count = int(self.find_element(list_raids[i], PLAYER_COUNT).text.split("/")[0])
                    if hp_lower <= hp_left <= hp_upper and joined_lower <= player_count <= joined_upper:
                        raid_index = i
                        if 'decreased' in self.get_attribute(list_raids[i], FP, 'class'):
                            if (i > offset):
                                self.driver.execute_script(SCROLL_INTO_VIEW, list_raids[i - offset])
                                try:
                                    list_raids[i].click()
                                except Exception:
                                    ref = True
                                    break
                            elif len(list_raids) <= firstpage:
                                try:
                                    list_raids[i].click()
                                except Exception:
                                    ref = True
                                    break
                            else:
                                self.driver.execute_script(SCROLL_INTO_VIEW, list_raids[0])
                                try:
                                    list_raids[i].click()
                                except Exception:
                                    ref = True
                                    break
                            time.sleep(1)
                            try:
                                if self.find_pop():
                                    ref = True
                                    break
                            except Exception:
                                ref = True
                                break
                            if "assist" in self.driver.current_url:
                                ref = True
                                break
                            return
                    if self.parent.quit is True:
                        return
                if ref:
                    self.driver.refresh()
                    time.sleep(1)
                    continue
                if raid_index < 0:
                    time.sleep(3)
                    try:
                        self.click_element(BTN_REFRESH)
                    except Exception:
                        self.driver.refresh()
                    time.sleep(1)
                    continue
                if (raid_index > offset):
                    self.driver.execute_script(SCROLL_INTO_VIEW, list_raids[raid_index - offset])
                    try:
                        list_raids[raid_index].click()
                    except Exception:
                        self.driver.refresh()
                        time.sleep(1)
                        continue
                elif len(list_raids) <= firstpage:
                    try:
                        list_raids[raid_index].click()
                    except Exception:
                        self.driver.refresh()
                        time.sleep(1)
                        continue
                else:
                    self.driver.execute_script(SCROLL_INTO_VIEW, list_raids[0])
                    try:
                        list_raids[raid_index].click()
                    except Exception:
                        self.driver.refresh()
                        time.sleep(1)
                        continue
                time.sleep(1)
                try:
                    if self.find_pop():
                        self.driver.refresh()
                        time.sleep(1)
                        continue
                except Exception:
                    self.get_url(URL_MULTI_RAID)
                    time.sleep(1)
                    continue
                if "assist" in self.driver.current_url:
                    self.driver.refresh()
                    time.sleep(1)
                    continue
                return
            if self.parent.quit is True:
                return
            time.sleep(3)
            try:
                self.click_element(BTN_REFRESH)
            except Exception:
                self.driver.refresh()
            time.sleep(1)

    def start_mission(self):
        try:
            with open("config.yaml") as f:
                self.data = yaml.load(f, Loader=yaml.FullLoader)
            summon_id = self.data["multi"]["summon_id"]
            method = self.data["multi"]["method"]
            repeat_times = self.data["multi"]["repeat_times"]
            treasure_id = self.data["multi"]["treasure_id"]
            treasure_count = self.data["multi"]["treasure_count"]
            hp_upper = self.data["multi"]["hp_upper"]
            hp_lower = self.data["multi"]["hp_lower"]
            joined_upper = self.data["multi"]["joined_upper"]
            joined_lower = self.data["multi"]["joined_lower"]
            goal_turn = self.data["multi"]["goal_turn"]
            logger.info("=" * 28)
            logger.attr("summon_id", summon_id)
            logger.attr("method", method)
            logger.attr("repeat_times", repeat_times)
            logger.attr("treasure_id", treasure_id)
            logger.attr("treasure_count", treasure_count)
            logger.attr("hp_upper", hp_upper)
            logger.attr("hp_lower", hp_lower)
            logger.attr("joined_upper", joined_upper)
            logger.attr("joined_lower", joined_lower)
            logger.attr("goal_turn", goal_turn)

            time.sleep(1)

            count = 0
            count_raid = 0

            while (
                (not repeat_times + treasure_count)
                | (repeat_times > count)
                | (self.find_treasure(treasure_id) < treasure_count)
            ):
                logger.info('-' * 50)
                logger.info(f"开始第{count+1}次任务")
                self.get_url(URL_MULTI_RAID)
                time.sleep(1)
                self.find_raid(hp_upper, hp_lower, joined_upper, joined_lower, method)
                if self.parent.quit is True:
                    break
                while not self.find_summon(summon_id, module='multi'):
                    self.find_raid(hp_upper, hp_lower, joined_upper, joined_lower, method)
                time.sleep(0.5)
                logger.info("正在等待进入战斗界面")
                self.wait_url(["#raid", "#raid_multi"])
                logger.info("开始战斗")
                if self.full_auto_multi(goal_turn=goal_turn):
                    count_raid += 1
                logger.info("战斗结束")
                count += 1

                if self.parent.quit is True:
                    break
                time.sleep(1)
                logger.info(f"当前正在等待{count_raid}个副本")
                if count_raid > 2:
                    logger.info("已达到最大等待副本数")
                while count_raid > 2:
                    self.get_url(URL_PENDING)
                    time.sleep(1)
                    pending_raid = self.find_element(PENDING_RAID)
                    if 'lis-raid' in self.get_attribute(pending_raid, "class"):
                        pending_raid.click()
                        time.sleep(1)
                        count_raid -= 1
                        logger.info("已清理1个未结算的副本")
                    else:
                        time.sleep(5)
            while count_raid > 0:
                logger.info(f"还有{count_raid}个未结算的副本")
                self.get_url(URL_PENDING)
                time.sleep(1)
                pending_raid = self.find_element(PENDING_RAID)
                if 'lis-raid' in self.get_attribute(pending_raid, "class"):
                    pending_raid.click()
                    time.sleep(1)
                    count_raid -= 1
                else:
                    if self.parent.quit is True:
                        break
                    time.sleep(10)
            logger.info('-' * 50)
            logger.info("任务已结束")

            self.get_url(URL_HOME)
        except Exception as e:
            logger.error(e)
            logger.debug("\n" + traceback.format_exc())
