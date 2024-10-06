# -*- coding: UTF-8 -*-
from page import DPage
from DrissionPage.common import wait_until
import logging
import numpy as np
import cv2
import ddddocr
import json
import os


PRT_SUM_LIST = "@@class:prt-supporter-attribute@@class:selected"
BTN_SUM = ".:btn-supporter lis-supporter"
BTN_OK = ".:btn-usual-ok"
CSS_SUM_INFO = "c:div.selected > div > div > div.prt-summon-image"

BTN_EVENT = ".:btn-switch-list event"
BTN_REFRESH = ".:btn-search-refresh"
BTN_MULTI = ".:btn-multi-raid lis-raid search"
BTN_MULTI_EVENT = ".:btn-multi-raid lis-raid"

BTN_MENU = ".btn-raid-menu menu"
BTN_ATT = ".btn-attack-start display-on"
BTN_AUTO = "@@class=btn-auto@@style=display: block;"
BTN_READY_AUTO = ".prt-start-direction"
BTN_BACK = ".:btn-command-back"
BTN_CHARAC_LIST = ".prt-member"
BTN_COMMAND_SUMMON = ".:btn-command-summon"
BTN_SUMMON = ".:lis-summon"
BTN_CHAT = ".btn-chat comment display-on"
BTN_CHAT_TEXT = ".lis-text"
BTN_HEAL = ".btn-temporary"
BTN_GREEN = ".:lis-item item-small btn-temporary-small"
BTN_BLUE = ".:lis-item item-large btn-temporary-large"
BTN_LIST_ABILITY = ".prt-ability-list"
BTN_ABILITY = ".:lis-ability btn-ability"
BTN_CHANGE_CA = ".:btn-lock"
BTN_BOX = ".:btn-box"
BTN_TARGET_LIST = ".:prt-character"
BTN_CHARACTER = ".:btn-command-character"
BTN_GURAD = ".:btn-guard"
BTN_FC = ".:btn-cb-gauge"

PRT_TREASURE = ".prt-treasure-wrapper"
COUNT_TREASURE = ".txt-treasure-num"

URL_MULTI_RAID = "https://game.granbluefantasy.jp/#quest/assist"
URL_MULTI_EVENT = "https://game.granbluefantasy.jp/#quest/assist/event"
URL_HOME = "https://game.granbluefantasy.jp/#mypage"
URL_PENDING = "https://game.granbluefantasy.jp/#quest/assist/unclaimed/0/0"

RE_RAID_LIST = r"quest/(assist/search/)?assist_list"
RE_CHECK_MULTI = r"quest/check_multi_start"
RE_CHECK_SUM = r"quest/decks_info"
RE_CHECK_ENDED = r"(?<!(model/))quest/(raid_deck_data_)?create"
RE_CHECK_START = r"(multi)?raid/start"
RE_ATT = r"(multi)?raid/(((normal_attack|ability|summon)_result)|start)"
RE_RESULT = r"result(multi)?/content/(index|empty)"
RE_VER_CODE = r"/c/a\?_="
RE_STATUS_PLAYER = r"quest/content/newassist"
RE_STAGE = r"quest/init_quest"
RE_CUSTOM = r"(multi)?raid/(((normal_attack|ability|summon|temporary_item|chat|fatal_chain)_result)|start|special_skill_setting)"  # noqa E501
RE_MYPAGE = r"https://prd-game-a2-granbluefantasy.akamaized.net/assets_en/1725537964/css/user/mypage.css"
ABILITY_LIST = ['Koenig Dekret', 'ケーニヒ・ベシュテレン', 'ツープラトン', 'Tag Team']
RAID_URL = "https://game.granbluefantasy.jp/#quest/supporter_raid/{multi_raid_id}/{quest_id}/1/{used_battle_point}/0/7"

logger = logging.getLogger("autogbf")


class AutoGBF(DPage):
    def __init__(self, parent=None):
        super().__init__()
        self.list_treasure = {}
        self.ocr = ddddocr.DdddOcr(show_ad=False)
        self.ocr.set_ranges(4)
        self.parent = parent

    def start_gbf(self):
        if URL_HOME not in self.page.url:
            self.page.get(URL_HOME)
        return True

    def find_raid(self, hp_upper, hp_lower, joined_upper, joined_lower, method=1):
        """
        寻找指定的多人副本
        :param hp_upper: BOSS血量上限
        :param hp_lower: BOSS血量下限
        :param joined_upper: 参与人数上限
        :param joined_lower: 参与人数下限
        :param method: 1为多人副本, 2为活动副本
        :return: True or False, True为正常运行, False为无法进入多人战斗, 将重新寻找多人副本
        """
        if method == 3:
            return self.find_raid_url(hp_upper, hp_lower, joined_upper, joined_lower)
        self.page.listen.start([RE_RAID_LIST, RE_CHECK_MULTI], is_regex=True, res_type="XHR")  # 开始监听多人副本数据包
        # 打开多人副本网页
        if method == 1:
            loc_multi = BTN_MULTI
            if self.page.url == URL_MULTI_RAID:
                self.click_ele(BTN_REFRESH)
            else:
                self.page.get(URL_MULTI_RAID)
        else:
            loc_multi = BTN_MULTI_EVENT
            self.page.get(URL_MULTI_EVENT)
            self.click_ele(BTN_EVENT)
        while True:
            index = 0
            try:
                packet = self.page.listen.wait(timeout=10, raise_err=True)
            except Exception:
                self.page.refresh()
                self.page.wait.doc_loaded()
                if method != 1:
                    self.click_ele(BTN_EVENT)
                continue
            data = packet.response.body.get("assist_raids_data")  # 获取副本列表数据
            if data is None:
                self.page.refresh()
                continue
            for i, cmd in enumerate(data, 1):
                boss_hp = cmd.get("boss_hp_width")  # BOSS剩余血量
                member_count = cmd.get("member_count")  # 已加入人数
                is_fp = cmd.get("is_unpopular")  # 是否是FP本
                raid_type = cmd.get("data-raid-type")
                if not raid_type:
                    continue
                if (hp_lower <= boss_hp <= hp_upper
                        and joined_lower <= member_count <= joined_upper):
                    index = i
                    # 是FP的本的情况跳出遍历
                    if is_fp:
                        break
            # 找不到符合条件的副本时index = 0，将直接刷新列表
            if index:
                self.click_ele(loc_multi, index)  # 点击对应副本
                try:
                    packet = self.page.listen.wait(timeout=10, raise_err=True)
                except Exception:
                    self.page.refresh()
                    self.page.wait.doc_loaded()
                    if method != 1:
                        self.click_ele(BTN_EVENT)
                    continue
                pop = packet.response.body.get("popup")  # 开始判断是否正常进入召唤石选择页面
                # 如果pop为False，则为正常，直接返回，否则为出现弹窗，需要点击确定后重新寻找副本
                if pop:
                    self.click_ele(BTN_OK)
                    break
                else:
                    self.page.listen.stop()
                    return
            self.page.wait(1.5)
            # 刷新，重新寻找副本
            if method == 1:
                self.click_ele(BTN_REFRESH)
            else:
                self.page.refresh()
                self.page.wait.doc_loaded()
                self.click_ele(BTN_EVENT)

    def find_raid_url(self, hp_upper, hp_lower, joined_upper, joined_lower):
        self.page.listen.start(RE_STATUS_PLAYER, is_regex=True, res_type="XHR")
        # 打开多人副本网页
        if self.page.url == URL_MULTI_RAID:
            self.page.refresh()
        else:
            self.page.get(URL_MULTI_RAID)
        packet = self.page.listen.wait(timeout=10)
        user_status = packet.response.body.get("option").get("user_status")
        now_battle_point = user_status.get("now_battle_point")
        self.page.listen.start(RE_RAID_LIST, is_regex=True, res_type="XHR")
        if now_battle_point < 5:
            self.page.ele(".prt-user-bp se").click()
            self.page.ele(".use-item-num", index=2).select.by_index(9 - now_battle_point)
            self.page.ele(".btn-use-item", index=2).click()
            self.page.ele(".btn-usual-ok").click()
            # self.page.listen.clear()
            self.page.wait(.3)
            self.page.ele(BTN_REFRESH).click()
        else:
            self.page.ele(BTN_REFRESH).click()
        while True:
            index = 0
            try:
                packet = self.page.listen.wait(timeout=10, raise_err=True)
                # logger.info(packet.url[32:])
            except Exception:
                self.page.refresh()
                self.page.wait.doc_loaded()
                continue
            data = packet.response.body.get("assist_raids_data")  # 获取副本列表数据
            if data is None or data == []:
                self.page.wait(1.5)
                self.click_ele(BTN_REFRESH)
                continue
            for i, cmd in enumerate(data, 1):
                boss_hp = cmd.get("boss_hp_width")  # BOSS剩余血量
                member_count = cmd.get("member_count")  # 已加入人数
                is_fp = cmd.get("is_unpopular")  # 是否是FP本
                raid_type = cmd.get("data-raid-type")
                if not raid_type:
                    continue
                if (hp_lower <= boss_hp <= hp_upper
                        and joined_lower <= member_count <= joined_upper):
                    index = i
                    used_battle_point = cmd.get("used_battle_point")
                    raid_data = cmd.get("raid")
                    multi_raid_id = raid_data.get("multi_raid_id")
                    quest_id = raid_data.get("quest_id")
                    # 是FP的本的情况跳出遍历
                    if is_fp:
                        break
            # 找不到符合条件的副本时index = 0，将直接刷新列表
            if index:
                self.page.get(RAID_URL.format(multi_raid_id=multi_raid_id,
                                              quest_id=quest_id,
                                              used_battle_point=used_battle_point))
                return
            # 刷新，重新寻找副本
            self.page.wait(1.5)
            self.click_ele(BTN_REFRESH)

    def _find_summon(self, sum_id: str):
        """
        寻找指定的召唤石
        :param sum_id: 召唤石id
        :return: Bool, True为正常运行, False为多人战斗已结束, 将重新寻找多人副本
        """

        # 对每个id每个召唤石遍历
        def iterate_twice(list_summon_id, list_summon_info):
            for id in list_summon_id:
                for summon_info in list_summon_info:
                    # 找到对应召唤石则点击
                    if summon_info.attr("data-image") == id:
                        logger.info(f"找到召唤石{id}")
                        summon = summon_info.parent(2)
                        summon.run_js("this.scrollIntoView()")
                        summon.click()
                        return summon
            return False

        logger.info("开始寻找召唤石")
        self.page.listen.start([RE_CHECK_ENDED, RE_CHECK_SUM, RE_VER_CODE], is_regex=True)

        # 获取超限等召唤石id列表
        list_summon_id = [sum_id + '_04', sum_id + '_03', sum_id + '_02', sum_id]
        # 获取当前列表的召唤石信息
        list_summon_info = self.page.eles(CSS_SUM_INFO)
        self.page.wait.doc_loaded()
        summon = iterate_twice(list_summon_id, list_summon_info)

        # 没找到对应召唤石则点击第一个召唤石
        if not summon:
            logger.info(f"未找到召唤石{sum_id}")
            summon = list_summon_info[0].parent(2)
            summon.run_js("this.scrollIntoView();")
            summon.click()

        for packet in self.page.listen.steps(timeout=10):
            if "/c/a?_=" in packet.url:
                if not packet.response.body.get("is_correct"):
                    res, image = self.send_code()
                else:
                    cv2.imwrite(f"assets/img/{res}.png", image)
                    summon.click()
            elif "quest/decks_info" in packet.url:
                if "popup" in packet.response.body:
                    res, image = self.send_code()
                else:
                    self.page.ele(BTN_OK).click()
            elif "create" in packet.url:
                if "error" in packet.response.body or "popup" in packet.response.body:
                    self.page.listen.stop()
                    return False
                # 正常进入战斗
                logger.info("正在进入战斗页面")

                def wait_url():
                    if "#raid" in self.page.url or "#quest/stage" in self.page.url:
                        return True
                    else:
                        return False
                wait_until(wait_url)
                if "#raid" in self.page.url:
                    self.page.wait.doc_loaded()
                    self.page.listen.stop()
                    return True
                elif "#quest/stage" in self.page.url:
                    self.page.wait(.5)
                    self.page.ele("#pop").ele(BTN_OK).click()
                    self.page.wait.url_change("#raid", timeout=5)
                    self.page.wait.doc_loaded()
                    self.page.listen.stop()
                    return True
        self.page.refresh()
        self.page.wait.doc_loaded()
        return self.find_summon(sum_id)

    def find_summon(self, sum_id):
        try:
            return self._find_summon(sum_id)
        except Exception:
            logger.exception("Error in find_summon")

    def find_treasure(self, treasure_id):
        if treasure_id is None:
            return 0
        count = self.list_treasure.get(treasure_id)
        return count if count is not None else 0

    def update_treasure(self):
        list_treasure = []
        ele_treasure = self.page.eles(".prt-treasure-wrapper")
        for ele in ele_treasure:
            data_item_id = ele.attr("data-item-id")
            list_treasure.append(data_item_id)
            if not os.path.exists("./assets/treasure/%s.jpg" % data_item_id):
                img = ele('t:img')
                # 保存图片
                img.save('./assets/treasure')
        return list_treasure

    def set_auto(self):
        while True:
            try:
                # self.page.wait.ele_displayed(".prt-start-direction")
                self.page.run_js("window.auto_flag = true")
                # logger.info(2)
                return
            except Exception:
                self.page.refresh()
                self.page.wait.load_start()
                self.page.wait(.2)

    def battle(self, current_turn=0, goal_turn=0, custom="无"):
        if custom != "无":
            return self.custom_battle(custom, goal_turn=goal_turn)
        is_finished = False
        is_win = False
        is_long_ability = False
        is_last_raid = True
        self.page.listen.start([RE_ATT, RE_RESULT], is_regex=True)    # 开始监听攻击结果和战斗结束
        init_flag = True
        revival_count = 0
        self.set_auto()
        while True:
            for packet in self.page.listen.steps(timeout=30):
                # 从每个数据包中获取对应信息
                # 为普通攻击或特定偷跑技能时，刷新，如果is_last_riad==False则后退
                # 当finished时，为多人战斗结束，刷新
                # 当lose时，为团灭，多人战斗时return，古战场模式时尝试吃药
                # 其他情况则跳过
                # logger.info(packet.url)
                if "content/index" in packet.url:
                    if packet.response.body is None or packet.response.body == '':
                        self.page.listen.stop()
                        return "empty"
                    if "redirect" in packet.response.body:
                        self.page.listen.stop()
                        return "empty"
                    display_list = packet.response.body.get("display_list")
                    if packet.response.body.get("option"):
                        if "result_data" in packet.response.body.get("option"):
                            result_data = packet.response.body.get("option").get("result_data")
                            replicard_data = result_data.get("replicard")
                            appearance = result_data.get("appearance")
                            if appearance == []:
                                self.is_hell = False
                            else:
                                self.is_hell = appearance.get("is_normal_hell").get("type")
                            if replicard_data != []:
                                card_replicard = replicard_data.get("enemy_icon_image")
                                if card_replicard:
                                    self.card_replicard = card_replicard
                                self.buff_name = replicard_data.get("enemy_quest_name")
                                self.is_chest = replicard_data.get("has_occurred_event")
                                self.count_enemy = replicard_data.get("enemy_stock")
                                self.stage_url = result_data.get("url")
                    if display_list:
                        for treasure in display_list.keys():
                            item_id = display_list.get(treasure).get("item_id")
                            number = int(display_list.get(treasure).get("number"))
                            self.list_treasure[item_id] = number
                    self.page.listen.stop()
                    return
                if "start" in packet.url:
                    if packet.response.body == "":
                        continue
                    scenarios = packet.response.body.get("scenario")
                    if scenarios:
                        self.page.refresh()
                        self.page.wait.doc_loaded()
                        continue
                    self.page.wait(.3)
                    self.set_auto()
                    continue
                elif init_flag:
                    try:
                        event = self.page.run_js("stage.gGameStatus.event", as_expr=True)
                    except Exception:
                        self.page.refresh()
                        self.page.wait.doc_loaded()
                        continue
                    if event and event.get("event_type") == "3":
                        is_uaf = True
                    else:
                        is_uaf = False
                    init_flag = False
                try:
                    scenarios = packet.response.body.get("scenario")
                except Exception:
                    break
                if scenarios is None:
                    continue
                for scenario in scenarios:
                    if scenario == []:
                        continue
                    cmd = scenario.get("cmd")
                    if cmd == "lose":
                        logger.info("已团灭")
                        logger.attr("is_uaf", is_uaf)
                        if not is_uaf:
                            self.page.listen.stop()
                            return "lose"
                        else:
                            self.page.refresh()
                            self.page.wait.doc_loaded()
                            if revival_count == 0:
                                self.page.ele(".btn-cheer").click()
                                self.page.wait(1)
                                self.page.ele(BTN_OK).click()
                            else:
                                self.page.ele(".btn-revival").click()
                            if revival_count <= 1:
                                self.page.ele(".btn-event-use").click()
                                self.page.wait.ele_displayed(BTN_ATT, timeout=5)
                                self.page.ele(".btn-temporary").click()
                                self.page.wait(1)
                                self.page.ele(".:lis-item btn-event-item").click()
                                self.page.ele(BTN_OK).click()
                                self.page.wait(1)
                                self.page.ele(".btn-temporary").click()
                                self.page.wait(1)
                                self.page.ele(".:lis-item btn-event-item").click()
                                self.page.ele(BTN_OK).click()
                            else:
                                self.page.ele('.btn-potion-use').click()
                            revival_count += 1
                    elif cmd == "finished":
                        is_finished = True
                        break
                    elif cmd == "win":
                        is_win = True
                        is_last_raid = scenario.get("is_last_raid")
                        break
                    if cmd == "ability":
                        if scenario.get("name") in ABILITY_LIST:
                            is_long_ability = True
                            break
                if is_long_ability:
                    self.page.refresh()
                    self.page.wait.doc_loaded()
                    is_long_ability = False
                    continue
                if is_finished:
                    self.page.refresh()
                    self.page.wait.doc_loaded()
                    break
                if "normal_attack" in packet.url or is_win or is_finished:
                    current_turn += 1
                    if current_turn == goal_turn:
                        return "turn_over"
                    break
            if is_last_raid or is_finished:
                self.page.refresh()
                self.page.wait.doc_loaded()
            else:
                self.page.back()
                self.page.wait.url_change("#raid")

    def _custom_battle(self, name, goal_turn=0):
        current_turn = 0
        current_user = 0
        count_all = 0
        setting_fa = False
        turn_start = True
        self.page.listen.start(RE_CUSTOM, is_regex=True)
        # 读取配置文件
        with open(f"./custom/{name}.json", "r", encoding='utf-8') as f:
            commands = json.load(f)

        for command in commands:
            type = command.get("type")
            is_fa = command.get("is_fa")
            if is_fa:
                if turn_start:
                    turn_start = False
                    self.set_auto()
                    setting_fa = True
                elif setting_fa:
                    pass
                elif current_user:
                    self.page.wait.ele_hidden("#main-mask")
                    self.page.ele(BTN_BACK).click()
                    self.page.wait(.5)
                    self.page.wait.ele_hidden("#main-mask")
                    self.page.ele(BTN_AUTO).click()
                    self.page.wait(.1)
                    setting_fa = True
                else:
                    self.page.wait.ele_hidden("#main-mask")
                    self.page.ele(BTN_AUTO).click()
                    self.page.wait(.1)
                    setting_fa = True
                count_all += 1
                continue
            else:
                if setting_fa:
                    self.page.listen.wait(count_all, timeout=60)
                    self.page.wait.ele_hidden("#main-mask")
                    self.page.ele(BTN_AUTO).click()
                    self.page.wait(.1)
                    count_all = 0
                    setting_fa = False
                if type == "ability":
                    user = command.get("user")
                    ability_number = command.get("ability_number")
                    target = command.get("target")
                    ability_sub_param = command.get("ability_sub_param")
                    if user != current_user and current_user != 0:
                        self.page.wait.ele_hidden("#main-mask")
                        self.page.ele(BTN_BACK).click()
                        self.page.wait(.1)
                    self.page.wait.ele_hidden("#main-mask")
                    self.page.ele(BTN_CHARAC_LIST).ele(BTN_CHARACTER, index=user).click()
                    self.page.wait(.1)
                    self.page.ele(BTN_LIST_ABILITY, index=user).ele(BTN_ABILITY, index=ability_number).click()
                    self.page.wait(.1)
                    if ability_sub_param:
                        for i in ability_sub_param:
                            self.page.ele(BTN_BOX, index=i).click()
                            self.page.wait(.1)
                    if target:
                        self.page.ele(BTN_TARGET_LIST).ele(BTN_CHARACTER, index=target).click()
                        self.page.wait(.1)
                    current_user = user
                    count_all += 1
                elif type == "summon":
                    target = command.get("target")
                    if current_user != 0:
                        self.page.wait.ele_hidden("#main-mask")
                        self.page.ele(BTN_BACK).click()
                        self.page.wait(.1)
                        current_user = 0
                    self.page.wait.ele_hidden("#main-mask")
                    self.page.ele(BTN_COMMAND_SUMMON).click()
                    self.page.wait(.3)
                    self.page.wait.ele_hidden("#main-mask")
                    self.page.ele(BTN_SUMMON, index=target).click()
                    self.page.wait(.1)
                    self.page.wait.ele_hidden("#main-mask")
                    self.page.ele(".btn-usual-ok btn-summon-use").click()
                    self.page.wait(.1)
                    count_all += 1
                elif type == "attack":
                    guard = command.get("guard")
                    for index, i in enumerate(guard, 1):
                        if i:
                            self.page.wait.ele_hidden("#main-mask")
                            self.page.ele(BTN_GURAD, index=index).click()
                            self.page.wait(.1)
                    self.page.wait.ele_hidden("#main-mask")
                    self.page.ele(BTN_ATT).click()
                    self.page.wait(.1)
                    count_all += 1
                    current_turn += 1
                    current_user = 0
                elif type == "chat":
                    self.page.wait.ele_hidden("#main-mask")
                    self.page.ele(BTN_CHAT).click()
                    self.page.wait(.1)
                    self.page.wait.ele_hidden("#main-mask")
                    self.page.ele(BTN_CHAT_TEXT).click()
                    self.page.wait(.1)
                    count_all += 1
                elif type == "heal":
                    pos = command.get("pos")
                    if current_user != 0:
                        self.page.wait.ele_hidden("#main-mask")
                        self.page.ele(BTN_BACK).click()
                        self.page.wait(.1)
                        current_user = 0
                    self.page.wait.ele_hidden("#main-mask")
                    self.page.ele(BTN_HEAL).click()
                    if pos < 0:
                        self.page.ele(BTN_BLUE).click()
                        self.page.wait(.1)
                        self.page.ele(".btn-usual-use").click()
                        self.page.wait(.1)
                    else:
                        self.page.ele(BTN_GREEN).click()
                        self.page.wait(.1)
                        self.page.ele(BTN_CHARAC_LIST).ele(BTN_CHARACTER, index=(pos + 1)).click()
                        self.page.wait(.1)
                    count_all += 1
                elif type == "change_ca":
                    if current_user != 0:
                        self.page.wait.ele_hidden("#main-mask")
                        self.page.ele(BTN_BACK).click()
                        self.page.wait(.1)
                        current_user = 0
                    self.page.wait.ele_hidden("#main-mask")
                    self.page.ele(BTN_CHANGE_CA).click()
                    self.page.wait(.1)
                    count_all += 1
                elif type == "fc":
                    if current_user != 0:
                        self.page.ele(BTN_BACK).click()
                        self.page.wait(.1)
                        current_user = 0
                    self.page.wait.ele_hidden("#main-mask")
                    self.page.ele(BTN_FC).click()
                    self.page.wait(.1)
                    self.page.ele(BTN_OK).click()
                    self.page.wait(.1)
                    count_all += 1
                elif type == "refresh":
                    self.page.listen.wait(count_all, timeout=60)
                    self.page.refresh()
                    self.page.wait.doc_loaded()
                    count_all = 1
                    current_user = 0
                    turn_start = True
                    setting_fa = False
                    self.page.wait(.1)
                elif type == "mypage":
                    self.page.get(URL_HOME)
                    return
            self.page.wait(.1)
        if not setting_fa:
            if current_user:
                self.page.wait.ele_hidden("#main-mask")
                self.page.ele(BTN_BACK).click()
                self.page.wait(.5)
                self.page.wait.ele_hidden("#main-mask")
                self.page.ele(BTN_AUTO).click()
                self.page.wait(.1)
            else:
                self.page.wait.ele_hidden("#main-mask")
                self.page.ele(BTN_AUTO).click()
        return self.battle(current_turn=current_turn, goal_turn=goal_turn)

    def custom_battle(self, name, goal_turn):
        try:
            self._custom_battle(name, goal_turn)
        except Exception:
            logger.exception("An error occurred during division")

    def _record_raid(self):
        self.page.listen.start([RE_CUSTOM, RE_MYPAGE], is_regex=True, res_type="XHR")
        data = []
        init_flag = True
        while True:
            for packet in self.page.listen.steps(timeout=1):
                # logger.info(packet.url)
                if "mypage" in packet.url:
                    logger.attr("type", "mypage")
                    data.append({
                        "type" : "mypage",
                    })
                elif "start" in packet.url:
                    if init_flag:
                        init_flag = False
                        pass
                    else:
                        logger.attr("type", "refresh")
                        data.append({
                            "type" : "refresh",
                        })
                elif "special_skill_setting" in packet.url:
                    logger.attr("type", "change_ca")
                    data.append({
                        "type" : "change_ca",
                    })
                elif "fatal_chain_result" in packet.url:
                    logger.attr("type", "fc")
                    data.append({
                        "type" : "fc",
                    })
                elif "normal_attack" in packet.url:
                    guard = []
                    is_guard_status = packet.response.body.get("status").get("is_guard_status")
                    for status in is_guard_status:
                        guard.append(status.get("is_guard_status"))
                    is_fa = self.page.run_js("stage.gGameStatus.auto_attack", as_expr=True)
                    logger.attr("type", "attack")
                    logger.info(f"is_fa = {is_fa}")
                    logger.info(f"guard = {guard}")
                    data.append({
                        "type" : "attack",
                        "is_fa" : is_fa,
                        "guard" : guard[:],
                    })
                    logger.info("回合结束")
                elif "temporary" in packet.url:
                    list_heal = packet.response.body.get("scenario")[0].get("list")
                    if len(list_heal) == 1:
                        pos = list_heal[0].get("pos")
                        type_heal = "green"
                    else:
                        pos = -1
                        type_heal = "blue"
                    logger.attr("type", "heal")
                    logger.info(f"pos = {pos}")
                    logger.info(f"type_heal = {type_heal}")
                    data.append({
                        "type" : "heal",
                        "pos" : pos,
                        "type_heal" : type_heal,
                    })
                elif "chat" in packet.url:
                    logger.attr("type", "chat")
                    data.append({
                        "type" : "chat",
                    })
                elif "summon" in packet.url:
                    name = packet.response.body.get("scenario")[0].get("name")
                    param = self.page.run_js("stage.gGameStatus.attackQueue.queue[0].param", as_expr=True)
                    summon_id = param.get("summon_id")
                    if summon_id != "supporter":
                        summon_id = int(summon_id) + 1
                    else:
                        summon_id = 6
                    is_fa = param.get("is_quick_summon")
                    logger.attr("type", "summon")
                    logger.info(f'is_fa = {is_fa}')
                    logger.info(f'summon_id = {summon_id}')
                    logger.info(f"name = {name}")
                    data.append({
                        "type" : "summon",
                        "target" : summon_id,
                        "is_fa" : is_fa if is_fa != "supporter" else "6",
                        "name" : name,
                    })
                elif "ability" in packet.url:
                    name = packet.response.body.get("scenario")[0].get("name")
                    param = self.page.run_js("stage.gGameStatus.attackQueue.queue[0].param", as_expr=True)
                    is_fa = param.get("is_by_auto")
                    if is_fa:
                        ability_number = param.get("abilityNumber")
                        user = int(param.get("ability_character_num")) + 1
                        target = 0
                        ability_sub_param = 0
                    else:
                        ele_ablity_class = self.page.run_js("stage.gGameStatus.$use_ability.context.firstElementChild", as_expr=True).attr("class")  # noqa E501
                        user, ability_number = ele_ablity_class[-3:].split("-")
                        target = int(param.get("ability_aim_num")) + 1 if param.get("ability_aim_num") is not None else 0  # noqa E501
                        ability_sub_param = param.get("ability_sub_param")
                    logger.attr("type", "ability")
                    logger.info(f'is_fa = {is_fa}')
                    logger.info(f'user = {user}')
                    logger.info(f'ability_number = {ability_number}')
                    logger.info(f"target = {target}")
                    logger.info(f"ability_sub_param = {ability_sub_param}")
                    logger.info(f"name = {name}")
                    data.append({
                        "type" : "ability",
                        "user" : int(user),
                        "ability_number" : int(ability_number),
                        "target" : int(target),
                        "is_fa" : is_fa,
                        "ability_sub_param" : ability_sub_param,
                        "name" : name,
                    })
                if self.parent.record_stop:
                    break
                logger.hr(2)
            if self.parent.record_stop:
                self.page.listen.stop()
                if self.parent.record_name:
                    with open(f"./custom/{self.parent.record_name}.json", 'w', encoding="utf-8") as file:
                        json.dump(data, file, indent=4)
                return True

    def record_raid(self):
        try:
            self._record_raid()
        except Exception:
            logger.exception("战斗录制出错")

    def send_code(self):
        code_input = self.page.ele(".frm-message")
        btn_send = self.page.ele(".btn-talk-message")
        img = self.page.ele(".image").src()
        byte_array = np.frombuffer(img, dtype=np.uint8)
        image = cv2.imdecode(byte_array, cv2.IMREAD_COLOR)
        gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        new_img = gray_img[1:][:]

        for i in range(1, 48):
            for j in range(1, 129):
                if new_img[i, j] == 2:
                    new_img[i, j] = 215
                if new_img[i, j] > 160:
                    new_img[i, j] = 255
                else:
                    new_img[i, j] = 0
        _, encoded_image = cv2.imencode('.png', new_img)
        img_bytes = encoded_image.tobytes()
        logger.info("识别验证码")
        res = self.ocr.classification(img_bytes, probability=True)
        s = ""
        for i in res['probability']:
            s += res['charsets'][i.index(max(i))]
        logger.info(f"当前识别结果为{s}")
        code_input.input(s)
        self.page.wait(0.5)
        btn_send.click()
        return s, image


if __name__ == '__main__':
    gbf = AutoGBF()
