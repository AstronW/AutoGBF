# -*- coding: UTF-8 -*-
from driver import Driver
import time
from logger import logger
import json
import re


PATTERN_ABILITY = r'https://game\.granbluefantasy\.jp/rest/(multiraid|raid)/ability_result\.json\?.*'
PATTERN_SUMMON = r'https://game\.granbluefantasy\.jp/rest/(multiraid|raid)/summon_result\.json\?.*'
ABILITY_LIST = ['Koenig Dekret', 'ケーニヒ・ベシュテレン', 'ツープラトン', 'Tag Team']
ENEMY_HP = "#wrapper > div.contents > div.cnt-raid > div.cnt-raid-stage > div.prt-targeting-area > div.prt-gauge-area > div.alive > span"  # noqa E501
BTN_AUTO = "#wrapper > div.contents > div.cnt-raid > div.btn-auto"
BTN_ATT = "#cnt-raid-information > div.btn-attack-start"
BTN_NEXT = '#wrapper > div.contents > div.cnt-raid > div.prt-command-end'
MAIN_MASK = "#main-mask"


class Battle(Driver):

    def full_auto(self, is_refresh=True):
        while ("#raid" in self.driver.current_url):
            logger.info("等待怪物血条出现")
            try:
                self.wait_element_display(ENEMY_HP)
            except Exception:
                self.driver.refresh()
                continue
            for i in range(50):
                try:
                    if self.element_is_displayed(BTN_AUTO):
                        logger.info("点击FA按钮")
                        self.click_element(BTN_AUTO)
                        break
                    else:
                        logger.info("点击攻击按钮")
                        self.click_element(BTN_ATT)
                    break
                except Exception:
                    time.sleep(0.2)
            logger.info("等待回合结束")
            time_1 = time.time()
            while True:
                self.performance_log = self.driver.get_log('performance')
                if (
                    self.start_attack()
                    | self.find_pop()
                    | self.zero_hp()
                    | self.battle_end()
                    | self.check_ability()
                ):
                    break
                time.sleep(1)
                time_2 = time.time()
                if time_2 - time_1 > 120:
                    break
            if is_refresh:
                self.driver.refresh()
                time.sleep(1)
            else:
                self.driver.back()
                time.sleep(0.5)
                self.driver.refresh()
                time.sleep(1)

    def full_auto_multi(self, goal_turn=0):
        self.count_turn = 0
        while ("#raid" in self.driver.current_url):
            logger.info(f"开始第{self.count_turn+1}回合")
            logger.info("等待怪物血条出现")
            try:
                self.wait_element_display(ENEMY_HP)
            except Exception:
                self.driver.refresh()
                time.sleep(2)
                continue
            if (
                (self.find_pop())
                | (self.zero_hp())
                | self.battle_end()
            ):
                return True
            else:
                pass
            try:
                if self.element_is_displayed(BTN_AUTO):
                    logger.info("点击FA按钮")
                    self.click_element(BTN_AUTO)
                else:
                    logger.info("点击攻击按钮")
                    self.click_element(BTN_ATT)
            except Exception:
                self.driver.refresh()
                time.sleep(2)
                continue
            time_1 = time.time()
            logger.info("等待回合结束")
            while True:
                self.performance_log = self.driver.get_log('performance')
                if (
                    self.start_attack()
                    | self.find_pop()
                    | self.zero_hp()
                    | self.battle_end()
                    | self.check_ability()
                ):
                    self.count_turn += 1
                    if goal_turn != 0 and self.count_turn >= goal_turn:
                        return True
                    break
                time.sleep(1)
                time_2 = time.time()
                if time_2 - time_1 > 120:
                    break
            time.sleep(1)
            self.driver.refresh()
            time.sleep(2)
        return False

    def start_attack(self):
        try:
            if self.get_attribute(MAIN_MASK, "style") == "display: block;":
                return True
            else:
                return False
        except Exception:
            return True

    def zero_hp(self):
        try:
            if self.find_element(ENEMY_HP).text == "0":
                return True
            else:
                return False
        except Exception:
            return True

    def battle_end(self):
        try:
            if self.element_is_displayed(BTN_NEXT):
                return True
            else:
                return False
        except Exception:
            return True

    def check_ability(self):
        try:
            for packet in self.performance_log:
                message = json.loads(packet.get('message')).get('message')
                if message.get('method') != 'Network.responseReceived':
                    continue
                requestid = message.get('params').get('requestId')
                url = message.get('params').get('response').get('url')
                if re.match(PATTERN_ABILITY, url):
                    resp = self.driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': requestid})
                    ability_name = json.loads(resp.get("body")).get("scenario")[0].get("name")
                    if ability_name in ABILITY_LIST:
                        self.count_turn -= 1
                        logger.info(7)
                        return True
            return False
        except Exception:
            # logger.error(e)
            # logger.info(8)
            return False

    def check_summon(self, summon_refresh):
        if summon_refresh:
            for packet in self.performance_log:
                message = json.loads(packet.get('message')).get('message')
                if message.get('method') != 'Network.responseReceived':
                    continue
                url = message.get('params').get('response').get('url')
                if re.match(PATTERN_SUMMON, url):
                    self.count_turn -= 1
                    return True
            return False
        else:
            return False
