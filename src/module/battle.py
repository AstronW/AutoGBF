from driver import Driver
from selector.battle import *  # noqa E501
import time
from logger import logger


class Battle(Driver):

    def full_auto(self):
        while ("#raid_multi" in self.driver.current_url
               or "#raid" in self.driver.current_url):
            logger.info("等待怪物血条出现")
            try:
                self.wait_element_display(ENEMY_HP)  # noqa F405
            except Exception:
                self.driver.refresh()
                continue
            for i in range(50):
                try:
                    if self.element_is_displayed(BTN_AUTO):  # noqa F405
                        logger.info("点击FA按钮")
                        self.click_element(BTN_AUTO)  # noqa F405
                        break
                    else:
                        logger.info("点击攻击按钮")
                        self.click_element(BTN_ATT)  # noqa F405
                    break
                except Exception:
                    time.sleep(0.2)
            logger.info("等待回合结束")
            try:
                self.wait_element_display(MAIN_MASK, 80) # noqa F405
            except Exception:
                pass
            self.driver.back()
            time.sleep(0.5)
            self.driver.refresh()
            time.sleep(1)

    def full_auto_multi(self):
        # count_turn = 0
        while ("#raid_multi" in self.driver.current_url
               or "#raid" in self.driver.current_url):
            logger.info("等待怪物血条出现")
            try:
                self.wait_element_display(ENEMY_HP)  # noqa F405
            except Exception:
                self.driver.refresh()
                time.sleep(2)
                continue
            try:
                if self.element_is_displayed(BTN_AUTO):  # noqa F405
                    logger.info("点击FA按钮")
                    self.click_element(BTN_AUTO)  # noqa F405
                else:
                    logger.info("点击攻击按钮")
                    self.click_element(BTN_ATT)  # noqa F405
            except Exception:
                self.driver.refresh()
                time.sleep(2)
                continue
            time_1 = time.time()
            logger.info("等待回合结束")
            time.sleep(1)
            while True:
                if (
                    (self.start_attack())
                    | (self.find_pop())
                    | (self.zero_hp())
                    | self.battle_end()
                ):
                    # count_turn += 1
                    # if count_turn >= goal_turn:
                    #     return
                    break
                time.sleep(1)
                time_2 = time.time()
                if time_2 - time_1 > 120:
                    break
            time.sleep(1)
            self.driver.refresh()
            time.sleep(2)

    def start_attack(self):
        try:
            if self.get_attribute(MAIN_MASK, "style") == "display: block;":  # noqa F405
                return True
            else:
                return False
        except Exception:
            return True

    def zero_hp(self):
        try:
            if self.find_element(ENEMY_HP).text == "0":  # noqa F405
                return True
            else:
                return False
        except Exception:
            return True

    def battle_end(self):
        try:
            return self.element_is_displayed(BTN_NEXT)  # noqa F405
        except Exception:
            return True
