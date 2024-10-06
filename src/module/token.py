from autogbf import AutoGBF
from config import ConfigManager
from bs4 import BeautifulSoup
from math import ceil
import logging
logger = logging.getLogger("autogbf")


COUNT_MEAT = ".txt-possessed-item"
BTN_HELL = ".prt-battle-quest"
INFO_HELL = ".:type-treasureraid-hell"
BTN_SKIP = ".:btn-usual-text"
BTN_DRAW = "@|class=prt-bulk-blink@|class=btn-use-all"
BTN_RESET = ".:btn-reset"
BTN_OK = ".:btn-usual-ok"
BTN_LIMITED = "c=#cnt-present > div > div.termed"
BTN_OTHER = "c=#prt-present-limit > div > div.btn-present-other"
BTN_PICK = "c=#prt-present-limit > div > div.btn-get-all"
COUNT_ITEM = "c=#prt-present-limit > div > div > div.txt-unclaimed-present"
ENABLE_SKIP = ".:btn-hell-skip-check"
SCR_IM = "#tpl-button-battle3"
BASE_URL = "https://game.granbluefantasy.jp/#quest/supporter/"
URL_CRATE = "https://game.granbluefantasy.jp/#present"


class Token(AutoGBF):

    def __init__(self, parent=None) -> None:
        AutoGBF.__init__(self)
        self.parent = parent

    def start(self) -> None:
        data = ConfigManager("token")
        url = data.get_config("url")
        summon_id = data.get_config("summon_id")
        method = data.get_config("method")
        custom = data.get_config("custom")
        logger.hr(1)
        logger.attr("url", url[32:])
        logger.attr("summon_id", summon_id)
        self.page.get(url)
        html = self.page.ele(SCR_IM).inner_html
        soup = BeautifulSoup(html, 'lxml')
        div_element = soup.find('div', {'class': 'btn-offer'})
        data_quest_id = div_element['data-quest-id']
        data_treasure_id = div_element['data-treasure-id']
        url_vh = f"{BASE_URL}{str((int(data_quest_id) - 20))}/1"
        if method == 1:
            url_ex = f"{BASE_URL}{str((int(data_quest_id) - 10))}/1/0/{data_treasure_id}"
            raid_cost = 3
        elif method == 2:
            url_ex = f"{BASE_URL}{data_quest_id}/1/0/{data_treasure_id}"
            raid_cost = 5
        logger.attr("url_vh", url_vh[32:])
        logger.attr("url_ex", url_ex[32:])
        if custom != "无":
            logger.attr("custom", custom)
        count = 0

        while True:

            # 获取当前肉的数量
            meat_count = int(self.page.ele(COUNT_MEAT).text)
            logger.hr(2)
            logger.info(f'当前拥有{meat_count}个肉')

            for _ in range(meat_count // raid_cost):
                logger.hr(2)
                logger.info(f"开始第{count + 1}次任务")
                self.page.wait(.5)
                self.page.get(url_ex)
                self.find_summon(summon_id)
                logger.info("开始战斗")
                self.battle()
                logger.info("战斗结束")
                count += 1

                if self.parent.quit is True:
                    return

            logger.info("开始补肉")
            for i in range(5):
                logger.hr(2)
                logger.info(f"开始第{i + 1}次补肉")
                self.page.get(url_vh)
                self.find_summon("2040114000")
                logger.info("开始战斗")
                self.battle()
                logger.info("战斗结束")

                if self.parent.quit is True:
                    return
            logger.hr(2)
            self.page.get(url)
            self.page.get(url)
            hell = self.page.ele(BTN_HELL)

            if hell.inner_html != '':
                info_hell = hell.ele(INFO_HELL)
                skip_vaild = int(info_hell.attr("data-hell-skip-vaild"))
                skip_status = int(info_hell.attr("data-hell-skip-status"))
                hell.click()
                self.page.wait(1)
                if skip_vaild:
                    if skip_status:
                        self.page.ele(BTN_SKIP).click()
                        self.page.wait(1)
                    else:
                        self.page.ele(ENABLE_SKIP).click()
                        self.page.wait(.5)
                        self.page.ele(BTN_SKIP).click()
                        self.page.wait(1)
                else:
                    self.page.ele(BTN_SKIP).click()
                    self.page.wait(1)
                    self.find_summon(summon_id)
                    logger.info("开始战斗")
                    self.battle()
                    logger.info("战斗结束")
                self.page.get(url)

    def _draw(self) -> None:
        data = ConfigManager("token")
        url = data.get_config("url")
        count_goal = data.get_config("count_goal")
        count_draw = 0
        url_draw = '/'.join(url.split('/')[:5]) + '/gacha'
        self.page.get(url_draw)
        btn_draw = self.page.ele(BTN_DRAW, timeout=5)
        if btn_draw:
            is_uaf = False
        else:
            is_uaf = True
            url_draw += "/index"
            self.page.get(url_draw)
        logger.hr(2)
        logger.info("已打开战货抽取页面")
        self.page.wait(1)
        while True:
            btn_draw = self.page.ele(BTN_DRAW, timeout=5)
            if btn_draw:
                btn_draw.click()
                logger.info("已点击全部抽取按钮")
                count_draw += 1
                self.page.wait(1)
                self.page.get(url_draw)
                if is_uaf and count_draw >= count_goal and count_goal:
                    logger.info("战货已抽完")
                    break
                self.page.wait(1)
                btn_reset = self.page.ele(BTN_RESET)
                if btn_reset:
                    btn_reset.run_js("this.scrollIntoView();")
                    self.page.wait(.3)
                    btn_reset.click()
                else:
                    logger.info("战货已抽完")
                    break
                logger.info("已点击重置按钮")
                self.page.wait(.3)
                self.page.ele(BTN_OK).click()
                self.page.refresh()
                self.page.wait.doc_loaded()
                logger.hr(2)
                logger.info("已打开战货抽取页面")
                self.page.wait(1)
            else:
                logger.info("战货已抽完")
                break
        logger.info("任务已结束")

    def draw(self) -> None:
        try:
            self._draw()
        except Exception as e:
            logger.exception(e)

    def pick(self) -> None:
        self.page.get(URL_CRATE)
        logger.info("已打开礼物箱网址")
        self.page.wait(1)
        self.page.ele(BTN_LIMITED).click()
        logger.info("已点击限时按钮")
        self.page.wait(1)
        self.page.ele(BTN_OTHER).click()
        logger.info("已点击其他礼物按钮")
        self.page.wait(1)
        items_text = self.page.ele(COUNT_ITEM).text
        if items_text[-1:] != '個':
            items_count = int(items_text)
        else:
            items_count = int(items_text[:-1])
        logger.info(f"待领取礼物剩余{items_count}个")
        count = ceil(items_count / 100)
        logger.info(f"预计领取{count}次")
        for i in range(count):
            self.page.ele(BTN_PICK).click()
            logger.info(f"已点击全部领取按钮({i+1}/{count})")
            self.page.wait(.5)
            self.page.ele(BTN_OK).click()
            self.page.wait(.5)
            self.page.ele(BTN_OK).click()
            self.page.wait(.5)
        logger.info("任务已结束")


if __name__ == "__main__":
    mission = Token()
    # mission.load_config()
    # mission.set_config(["Token", "url"], "https://game.granbluefantasy.jp/#event/treasureraid150")
    # mission.save_config()
    mission.pick()
