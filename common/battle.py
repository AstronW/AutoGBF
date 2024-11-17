from logger import logger
from common.constants import Loc
from common.status import Status, get_status
from DrissionPage._pages.mix_tab import MixTab
import json
import re


class Battle:
    def __init__(self, page : MixTab):
        self.page = page

    def set_auto(self):
        self.page.run_js("window.auto_flag = true;")

    def start_battle(self, goal_turn : int = 0, custom : str = None):
        logger.info("开始战斗")
        if custom and custom != '':
            return self.custom_battle(goal_turn, custom)
        count_turn = 0
        while True:
            for packet in self.page.listen.steps(timeout=30):
                status = get_status(packet)
                match status:
                    case Status.BATTLE_INIT:
                        self.page.ele("#pop").ele(Loc.BTN_OK).click()
                    case Status.BATTLE_START:
                        self.set_auto()
                    case Status.BATTLE_FINISH\
                        | Status.BATTLE_LONG_ABILITY\
                        | Status.BATTLE_DIE:
                        self.page.refresh()
                        self.page.wait.doc_loaded()
                    case Status.BATTLE_NORMAL_ATTACK:
                        self.page.stop_loading()
                        count_turn += 1
                        logger.info(f"回合{count_turn}结束")
                        self.page.refresh()
                        self.page.wait.doc_loaded()
                    case Status.BATTLE_BACK:
                        self.page.back()
                        self.page.wait.url_change("#raid")
                    case Status.BATTLE_LOSE:
                        return Status.BATTLE_LOSE
                    case Status.BATTLE_RESULT:
                        self.page.stop_loading()
                        logger.info("战斗结束")
                        return Status.BATTLE_RESULT
                    case Status.BATTLE_RESULT_EMPTY:
                        return Status.BATTLE_RESULT_EMPTY
                    case _:
                        pass
                if goal_turn and count_turn >= goal_turn:
                    logger.info('已达到目标回合数')
                    return Status.BATTLE_TURN_ENOUGH
            self.page.refresh()
            self.page.wait.doc_loaded()

    def custom_battle(self, goal_turn: int, custom: str):
        #TODO 吃药等环节还没有制作
        current_turn = 0
        current_user = 0
        count_all = 0
        setting_fa = False
        turn_start = True

        # 读取配置文件
        with open(f"./custom/{custom}.json", "r", encoding='utf-8') as f:
            commands = json.load(f)

        def wait_and_click(locs, indices=None):
            """
            等待页面元素加载并点击。
            :param locs: 位置字符串列表，用于定位元素。
            :param indices: 可选的索引列表，指定要点击的元素的索引。
            """
            
            if indices is None:
                indices = []
            # 确保indices列表长度与locs一致，未指定索引的默认为0
            full_indices = indices + [1] * (len(locs) - len(indices))
            
            element = self.page
            for loc, index in zip(locs, full_indices):
                element = element.ele(loc, index=index)
                
            
            self.page.wait.ele_hidden("#main-mask")
            
            try:
                element.click()
                
            except:
                return

        for command in commands:

            if "raid" not in self.page.url:
                return Status.BATTLE_FINISH

            type = command.get("type")
            logger.info(type)
            is_fa = command.get("is_fa")

            if is_fa:
                if turn_start:
                    turn_start = False
                    self.set_auto()
                elif setting_fa:
                    pass
                elif current_user:
                    wait_and_click([Loc.BTN_BACK])
                    wait_and_click([Loc.BTN_AUTO])
                else:
                    wait_and_click([Loc.BTN_AUTO])
                setting_fa = True
                count_all += 1
                continue

            if setting_fa:
                if count_all:
                    count = 0
                    for packet in self.page.listen.steps(timeout=60):
                        status = get_status(packet)
                        logger.debug(status)
                        
                        match status:
                            case Status.BATTLE_RESULT\
                                | Status.BATTLE_RESULT_EMPTY\
                                | Status.BATTLE_LOSE\
                                | Status.BATTLE_FINISH:
                                return Status.BATTLE_FINISH
                            case Status.BATTLE_LOSE:
                                return Status.BATTLE_LOSE
                            case Status.NOTHING\
                                | Status.BATTLE_INIT\
                                | Status.BATTLE_START:
                                continue
                            case Status.NET_ERROR:
                                self.page.refresh()
                                self.page.wait.doc_loaded()
                            case _:
                                
                                count += 1
                                if count >= count_all:
                                    break
                
                self.page.stop_loading()
                
                self.page.wait.ele_displayed(Loc.BTN_AUTO)
                self.page.ele(Loc.BTN_AUTO).click()
                
                count_all = 0
                setting_fa = False

            if type == "ability":
                user = command.get("user")
                ability_number = command.get("ability_number")
                target = command.get("target")
                ability_sub_param = command.get("ability_sub_param")

                if user != current_user and current_user != 0:
                    wait_and_click([Loc.BTN_BACK])

                wait_and_click([Loc.BTN_LIST_CHARAC, Loc.BTN_CHARACTER], [1, user])
                wait_and_click([Loc.BTN_LIST_ABILITY, Loc.BTN_ABILITY], [user, ability_number])

                if ability_sub_param:
                    for i in ability_sub_param:
                        wait_and_click([Loc.BTN_BOX], [i])

                if target:
                    wait_and_click([Loc.BTN_LIST_TARGET, Loc.BTN_CHARACTER], [1, target])

                current_user = user
                count_all += 1

            elif type == "summon":
                target = command.get("target")
                if current_user != 0:
                    wait_and_click([Loc.BTN_BACK])
                    current_user = 0

                wait_and_click([Loc.BTN_COMMAND_SUMMON])
                wait_and_click([Loc.BTN_SUMMON], [target])
                wait_and_click([Loc.BTN_SUMMON_OK])
                count_all += 1

            elif type == "attack":
                guard = command.get("guard")
                for index, i in enumerate(guard, 1):
                    if i:
                        wait_and_click([Loc.BTN_GURAD], [index])

                wait_and_click([Loc.BTN_ATT])
                count_all += 1
                current_turn += 1
                current_user = 0

            elif type == "chat":
                wait_and_click([Loc.BTN_CHAT])
                wait_and_click([Loc.BTN_CHAT_TEXT])
                count_all += 1

            elif type == "heal":
                pos = command.get("pos")
                if current_user != 0:
                    wait_and_click([Loc.BTN_BACK])
                    current_user = 0

                wait_and_click([Loc.BTN_HEAL])
                if pos < 0:
                    wait_and_click([Loc.BTN_BLUE])
                    wait_and_click([".btn-usual-use"])
                else:
                    wait_and_click([Loc.BTN_GREEN])
                    wait_and_click([Loc.BTN_LIST_CHARAC, Loc.BTN_CHARACTER], [1, pos + 1])
                count_all += 1

            elif type == "change_ca":
                if current_user != 0:
                    wait_and_click([Loc.BTN_BACK])
                    current_user = 0

                wait_and_click([Loc.BTN_CHANGE_CA])
                count_all += 1

            elif type == "fc":
                if current_user != 0:
                    wait_and_click([Loc.BTN_BACK])
                    current_user = 0

                wait_and_click([Loc.BTN_FC])
                wait_and_click([Loc.BTN_OK])
                count_all += 1

            elif type == "refresh":
                if count_all:
                    count = 0
                    for packet in self.page.listen.steps(timeout=60):
                        status = get_status(packet)
                        logger.debug(status)
                        match status:
                            case Status.BATTLE_RESULT\
                                | Status.BATTLE_RESULT_EMPTY:
                                return Status.BATTLE_RESULT
                            case Status.BATTLE_LOSE\
                                | Status.BATTLE_FINISH:
                                return Status.BATTLE_LOSE
                            case Status.NOTHING\
                                | Status.BATTLE_INIT\
                                | Status.BATTLE_START:
                                continue
                            case Status.NET_ERROR:
                                self.page.refresh()
                                self.page.wait.doc_loaded()
                            case _:
                                count += 1
                                if count >= count_all:
                                    break
                self.page.stop_loading()
                self.page.refresh()
                self.page.wait.doc_loaded()
                count_all = 0
                current_user = 0
                turn_start = True
                setting_fa = False

            elif type == "mypage":
                return Status.BATTLE_TURN_ENOUGH

        left_turn = goal_turn - current_turn
        if left_turn <= 0:
            return Status.BATTLE_TURN_ENOUGH

        if not setting_fa:
            if current_user:
                wait_and_click([Loc.BTN_BACK])
                wait_and_click([Loc.BTN_AUTO])
            else:
                wait_and_click([Loc.BTN_AUTO])

        return self.battle(goal_turn=left_turn)
