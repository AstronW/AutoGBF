# -*- coding: UTF-8 -*-
from module.battle import Battle
import time
import yaml
from logger import logger
import traceback
from math import ceil


URL_HOME = "https://game.granbluefantasy.jp/#mypage"
URL_CRATE = "https://game.granbluefantasy.jp/#present"
GROUP_RAID = "#cnt-quest > div > div > div > div > div.btn-event-raid"
BTN_RAID = "#popup-body > div.prt-btn-list > div > div"
COUNT_MEAT = "#cnt-quest > div > div > div > div > div > div > div.txt-possessed-item"
HELL_RAID = "#cnt-quest > div > div > div > div > div.prt-battle-quest"
COUNT_HELL = "#cnt-quest > div > div > div > div > div.prt-battle-quest > div > div > div > div"
HELL_SKIP_SETTING = "#pop > div > div.prt-popup-body > div > div > div"
HELL_CLAIM_LOOT = '#pop > div > div.prt-popup-footer > div.btn-usual-text.hide-common-text'
BTN_HELL_SKIP = "#pop > div > div.prt-popup-body > div > div > div.prt-hell-skip-setting > label"
DRAW_ALL = "#cnt-gachas-reward > div > div > div > div > div.prt-medal-obtain"
BTN_DRAW = "#cnt-gachas-reward > div > div > div > div > div > div.btn-bulk-play"
BTN_RESET = "#cnt-gachas-reward > div > div > div > div.prt-event-reset > div.btn-reset"
BTN_OK = "#pop > div > div.prt-popup-footer > div.btn-usual-ok"
TIME_LIMIT = '#cnt-present > div.prt-3tabs > div.termed'
CRATE_OTHER = '#prt-present-limit > div.prt-present-type > div.btn-present-other'
PICK_UP = '#prt-present-limit > div.prt-get-all > div.btn-get-all'
ITEMS = '#prt-present-limit > div.prt-get-all > div.prt-get-all-title > div.txt-unclaimed-present'


class Token(Battle):

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.driver = self.parent.driver.driver

    def start_mission(self):
        try:
            with open("config.yaml") as f:
                self.data = yaml.load(f, Loader=yaml.FullLoader)
            url = self.data["token"]["url"]
            summon_id = self.data["token"]["summon_id"]
            method = self.data["token"]["method"]
            logger.info("=" * 28)
            logger.attr("url", url)
            logger.attr("summon_id", summon_id)

            time.sleep(1)
            self.get_url(url)
            time.sleep(1)
            self.get_url(url)
            time.sleep(1)
            self.click_element(GROUP_RAID)
            time.sleep(1)
            self.click_element(BTN_RAID)
            time.sleep(1)
            url_vh = self.driver.current_url
            # 获取3肉副本网址
            url_list = url_vh.split('/')
            if method == 1:
                url_list[-2] = str((int(url_list[-2]) + 10))
                raid_cost = 3
            elif method == 2:
                url_list[-2] = str((int(url_list[-2]) + 20))
                raid_cost = 5
            url_ex = '/'.join(url_list) + '/0/10525'
            logger.attr("url_vh", url_vh)
            logger.attr("url_ex", url_ex)
            time.sleep(1)

            count = 0

            while True:
                # logger.info('-' * 50)
                # logger.info(f"开始第{count+1}次任务")
                self.get_url(url)
                time.sleep(1)
                self.get_url(url)
                time.sleep(1)

                # 获取当前肉的数量
                meat_count = int(self.find_element(COUNT_MEAT).text)
                logger.info('-' * 50)
                logger.info(f'当前拥有{meat_count}个肉')

                for _ in range(meat_count // raid_cost):
                    logger.info('-' * 50)
                    logger.info(f"开始第{count + 1}次任务")
                    time.sleep(1)
                    self.get_url(url_ex)
                    time.sleep(0.5)
                    while not self.find_summon(summon_id):
                        self.get_url(url_ex)
                        time.sleep(0.5)
                    time.sleep(0.5)
                    logger.info("正在等待进入战斗界面")
                    self.wait_url(["#raid", "#raid_multi"])
                    logger.info("开始战斗")
                    self.full_auto()
                    logger.info("战斗结束")
                    count += 1

                    if self.parent.quit is True:
                        break
                if self.parent.quit is True:
                    break
                time.sleep(1)

                logger.info("开始补肉")
                for i in range(5):
                    logger.info('-' * 50)
                    logger.info(f"开始第{i + 1}次补肉")
                    time.sleep(1)
                    self.get_url(url_vh)
                    time.sleep(0.5)
                    while not self.find_summon(summon_id):
                        self.get_url(url_ex)
                        time.sleep(0.5)
                    time.sleep(0.5)
                    logger.info("正在等待进入战斗界面")
                    self.wait_url(["#raid", "#raid_multi"])
                    logger.info("开始战斗")
                    self.full_auto()
                    logger.info("战斗结束")

                    if self.parent.quit is True:
                        break
                if self.parent.quit is True:
                    break
                logger.info('-' * 50)
                # 开始清理HELL副本
                time.sleep(1)
                self.get_url(url)
                time.sleep(1)
                self.get_url(url)
                time.sleep(1)
                hell = self.find_element(HELL_RAID)
                if hell.get_attribute("innerHTML") != '':
                    hell_count = int(self.find_element(COUNT_HELL).text)
                    logger.info(f"hell副本数量为{hell_count}")
                    if self.parent.quit is True:
                        break
                    hell.click()
                    time.sleep(1)
                    if len(self.find_element_list(HELL_SKIP_SETTING)) > 4:
                        # 可开启跳过
                        if self.get_attribute(HELL_CLAIM_LOOT, "innerHTML") in ['Claim Loot', '報酬を獲得']:
                            # 已开启跳过
                            self.get_url(url)
                            time.sleep(1)
                            for i in range(ceil(hell_count / 10)):
                                logger.info("跳过HELL副本")
                                self.click_element(HELL_RAID)
                                time.sleep(1)
                                self.click_element(HELL_CLAIM_LOOT)
                                time.sleep(1)
                                self.get_url(url)
                                time.sleep(1)
                        else:
                            # 未开启跳过
                            self.click_element(BTN_HELL_SKIP)
                            time.sleep(1)
                            self.get_url(url)
                            time.sleep(1)
                            for i in range(ceil(hell_count / 10)):
                                logger.info("跳过HELL副本")
                                self.click_element(HELL_RAID)
                                time.sleep(1)
                                self.click_element(HELL_CLAIM_LOOT)
                                time.sleep(1)
                                self.get_url(url)
                                time.sleep(1)
                    else:
                        # 无法开启跳过
                        logger.info("无法开启skip")
                        self.click_element(HELL_CLAIM_LOOT)
                        time.sleep(1)
                        while not self.find_summon(summon_id):
                            self.driver.refresh()
                            time.sleep(1)
                        self.wait_url(["#raid", "#raid_multi"])
                        logger.info("开始战斗")
                        self.full_auto()
                        logger.info("战斗结束")
            logger.info("任务已结束")
            self.get_url(URL_HOME)
        except Exception as e:
            logger.error(e)
            logger.debug("\n" + traceback.format_exc())

    def draw(self):
        try:
            with open("config.yaml") as f:
                self.data = yaml.load(f, Loader=yaml.FullLoader)
            url = self.data["token"]["url"]
            url_draw = '/'.join(url.split('/')[:5]) + '/gacha'
            self.get_url(url_draw)
            logger.info('-' * 50)
            logger.info("已打开战货抽取页面")
            time.sleep(1)
            while True:

                if 'bulk' in self.get_attribute(DRAW_ALL, "class"):
                    self.click_element(BTN_DRAW)
                    logger.info("已点击全部抽取按钮")
                    time.sleep(1)
                    self.driver.back()
                    time.sleep(1)
                    btn_draw_reset = self.find_element(BTN_RESET)
                    self.driver.execute_script("arguments[0].scrollIntoView();", btn_draw_reset)
                    time.sleep(1)
                    btn_draw_reset.click()
                    logger.info("已点击重置按钮")
                    self.click_element(BTN_OK)
                    time.sleep(1)
                    self.get_url(url)
                    time.sleep(1)
                    self.get_url(url_draw)
                    logger.info('-' * 50)
                    logger.info("已打开战货抽取页面")
                    time.sleep(1)
                else:
                    logger.info("战货已抽完")
                    break
        except Exception as e:
            logger.error(e)
            logger.debug("\n" + traceback.format_exc())

    def pick(self):
        self.get_url(URL_CRATE)
        logger.info("已打开礼物箱网址")
        time.sleep(1)
        self.click_element(TIME_LIMIT)
        logger.info("已点击限时按钮")
        time.sleep(1)
        self.click_element(CRATE_OTHER)
        logger.info("已点击其他礼物按钮")
        time.sleep(1)
        items_text = self.find_element(ITEMS).text
        if items_text[-1:] != '個':
            items_count = int(items_text)
        else:
            items_count = int(items_text[:-1])
        logger.info(f"待领取礼物剩余{items_count}个")
        count = ceil(items_count / 100)
        logger.info(f"预计领取{count}次")
        for i in range(count):
            self.click_element(PICK_UP)
            logger.info("已点击全部领取按钮")
            time.sleep(1)
            self.click_element(BTN_OK)
            time.sleep(1)
            self.click_element(BTN_OK)
            time.sleep(1)
