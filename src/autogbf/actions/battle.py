from DrissionPage._pages.mix_tab import MixTab
import json
from ...utils.logger import logger
from ..metadata.constants import Loc, Url
from ..metadata.status import Status, get_status


class Battle:
    """
    Battle类用于自动化战斗过程。

    Attributes:
        page (MixTab): 用于操作网页的MixTab实例。
    """

    def __init__(self, page: MixTab):
        """
        初始化Battle实例。

        Args:
            page (MixTab): 用于操作网页的MixTab实例。
        """
        self.page = page

    def set_auto(self):
        """
        设置战斗为自动模式。

        通过执行JavaScript代码设置窗口的auto_flag为true。
        """
        self.page.run_js("window.auto_flag = true;")

    def start_battle(self, goal_turn: int = 0, custom: str = None):
        """
        开始战斗，可以选择达到的目标回合数或使用自定义战斗配置。

        Args:
            goal_turn (int): 目标回合数，默认为0，表示无限制。
            custom (str): 自定义战斗配置的名称，默认为None。

        Returns:
            Status: 战斗结束时的状态。
        """
        logger.info("开始战斗")
        if custom and custom != "":
            return self.custom_battle(goal_turn, custom)
        count_turn = 0
        while True:
            for packet in self.page.listen.steps(timeout=30):
                status = get_status(packet)
                logger.debug(status)
                match status:
                    case Status.BATTLE_INIT:
                        self.page.ele("#pop").ele(Loc.BTN_OK).click()
                    case Status.BATTLE_START:
                        self.set_auto()
                    case (
                        Status.BATTLE_FINISH
                        | Status.BATTLE_LONG_ABILITY
                        | Status.BATTLE_DIE
                        | Status.BATTLE_TRIGGER
                    ):
                        self.page.refresh()
                        self.page.wait.doc_loaded()
                    case Status.BATTLE_NORMAL_ATTACK:
                        count_turn += 1
                        logger.info(f"回合{count_turn}结束")
                        if goal_turn and count_turn >= goal_turn:
                            logger.info("已达到目标回合数")
                            return Status.BATTLE_TURN_ENOUGH
                        self.page.refresh()
                        self.page.wait.doc_loaded()
                    case Status.BATTLE_BACK:
                        self.page.back()
                        self.page.wait.url_change("#raid")
                    case Status.BATTLE_LOSE:
                        return Status.BATTLE_LOSE
                    case Status.BATTLE_RESULT:
                        logger.info("战斗结束")
                        return Status.BATTLE_RESULT
                    case Status.BATTLE_RESULT_EMPTY:
                        return Status.BATTLE_RESULT_EMPTY
                    case _:
                        pass

            self.page.refresh()
            self.page.wait.doc_loaded()

    def custom_battle(self, goal_turn: int, custom: str):
        """
        使用自定义配置进行战斗。

        Args:
            goal_turn (int): 目标回合数。
            custom (str): 自定义战斗配置的名称。

        Returns:
            Status: 战斗结束时的状态。
        """
        current_turn = 0
        current_user = 0
        count_all = 0
        setting_fa = False
        turn_start = True

        # 读取配置文件
        with open(f"./custom/{custom}.json", "r", encoding="utf-8") as f:
            commands = json.load(f)

        for command in commands:
            if "raid" not in self.page.url:
                return Status.BATTLE_LOSE

            type = command.get("type")
            logger.info(type)
            is_fa = command.get("is_fa")

            if is_fa:
                self.handle_fa(setting_fa, turn_start, current_user)
                setting_fa = True
                count_all += 1
                continue

            if setting_fa:
                self.handle_setting_fa(count_all)
                count_all = 0
                setting_fa = False

            match type:
                case "ability":
                    self.handle_ability(command, current_user)
                    current_user = command.get("user")
                    count_all += 1
                case "summon":
                    self.handle_summon(command, current_user)
                    current_user = 0
                    count_all += 1
                case "attack":
                    self.handle_attack(command, current_turn, current_user)
                    current_turn += 1
                    current_user = 0
                    count_all += 1
                case "chat":
                    self.handle_chat()
                    count_all += 1
                case "heal":
                    self.handle_heal(command, current_user)
                    current_user = 0
                    count_all += 1
                case "change_ca":
                    self.handle_change_ca(current_user)
                    current_user = 0
                    count_all += 1
                case "fc":
                    self.handle_fc(current_user)
                    current_user = 0
                    count_all += 1
                case "refresh":
                    self.handle_refresh(count_all)
                    count_all = 0
                    current_user = 0
                    turn_start = True
                    setting_fa = False
                case "mypage":
                    self.page.get(Url.MYPAGE)
                    return Status.BATTLE_TURN_ENOUGH

        left_turn = goal_turn - current_turn
        if left_turn <= 0:
            return Status.BATTLE_TURN_ENOUGH

        if not setting_fa:
            self.handle_final_auto(current_user)

        return self.battle(goal_turn=left_turn)

    def handle_fa(self, setting_fa, turn_start, current_user):
        """
        根据不同的条件处理自动模式的设置

        参数:
        - setting_fa: 表示是否正在设置FA模式的布尔值
        - turn_start: 表示是否是回合开始的布尔值
        - current_user: 表示当前用户的布尔值，用于确定是否需要进行操作

        返回值:
        无
        """
        if turn_start:
            # 如果是回合开始，则调用set_auto方法设置自动模式
            self.set_auto()
        elif setting_fa:
            # 如果正在设置FA模式，则不执行任何操作
            pass
        elif current_user:
            # 如果是当前用户，则需要进行返回并设置自动模式的操作
            self.wait_and_click([Loc.BTN_BACK])
            self.wait_and_click([Loc.BTN_AUTO])
        else:
            # 如果以上条件都不满足，则直接设置自动模式
            self.wait_and_click([Loc.BTN_AUTO])

    def handle_setting_fa(self, count_all):
        if count_all:
            count = 0
            for packet in self.page.listen.steps(timeout=60):
                status = get_status(packet)
                logger.debug(status)
                match status:
                    case Status.BATTLE_RESULT:
                        return Status.BATTLE_RESULT
                    case Status.BATTLE_RESULT_EMPTY:
                        return Status.BATTLE_RESULT_EMPTY
                    case Status.BATTLE_FINISH:
                        self.page.refresh()
                        self.page.wait.doc_loaded()
                        continue
                    case Status.BATTLE_LOSE:
                        return Status.BATTLE_LOSE
                    case Status.NOTHING | Status.BATTLE_INIT | Status.BATTLE_START:
                        continue
                    case Status.NET_ERROR:
                        self.page.refresh()
                        self.page.wait(1)
                        self.page.wait.doc_loaded()
                    case _:
                        count += 1
                        if count >= count_all:
                            break

        btn_auto = self.page.ele(Loc.BTN_AUTO)
        self.page.wait.ele_displayed(Loc.BTN_AUTO)
        btn_auto.click()

    def handle_ability(self, command, current_user):
        user = command.get("user")
        ability_number = command.get("ability_number")
        target = command.get("target")
        ability_sub_param = command.get("ability_sub_param")

        if user != current_user and current_user != 0:
            self.wait_and_click([Loc.BTN_BACK])

        self.wait_and_click([Loc.BTN_LIST_CHARAC, Loc.BTN_CHARACTER], [1, user])
        self.page.wait(0.2)
        self.wait_and_click(
            [Loc.BTN_LIST_ABILITY, Loc.BTN_ABILITY], [user, ability_number]
        )

        if ability_sub_param:
            for i in ability_sub_param:
                self.wait_and_click([Loc.BTN_BOX], [i])

        if target:
            self.wait_and_click([Loc.BTN_LIST_TARGET, Loc.BTN_CHARACTER], [1, target])

    def handle_summon(self, command, current_user):
        target = command.get("target")
        if current_user != 0:
            self.wait_and_click([Loc.BTN_BACK])
            current_user = 0

        self.wait_and_click([Loc.BTN_COMMAND_SUMMON])
        self.wait_and_click([Loc.BTN_SUMMON], [target])
        self.wait_and_click([Loc.BTN_SUMMON_OK])

    def handle_attack(self, command):
        guard = command.get("guard")
        for index, i in enumerate(guard, 1):
            if i:
                self.wait_and_click([Loc.BTN_GURAD], [index])

        self.wait_and_click([Loc.BTN_ATT])

    def handle_chat(self):
        self.wait_and_click([Loc.BTN_CHAT])
        self.wait_and_click([Loc.BTN_CHAT_TEXT])

    def handle_heal(self, command, current_user):
        pos = command.get("pos")
        if current_user != 0:
            self.wait_and_click([Loc.BTN_BACK])
            current_user = 0

        self.wait_and_click([Loc.BTN_HEAL])
        if pos < 0:
            self.wait_and_click([Loc.BTN_BLUE])
            self.wait_and_click([".btn-usual-use"])
        else:
            self.wait_and_click([Loc.BTN_GREEN])
            self.wait_and_click([Loc.BTN_LIST_CHARAC, Loc.BTN_CHARACTER], [1, pos + 1])

    def handle_change_ca(self, current_user):
        if current_user != 0:
            self.wait_and_click([Loc.BTN_BACK])
            current_user = 0

        self.wait_and_click([Loc.BTN_CHANGE_CA])

    def handle_fc(self, current_user):
        if current_user != 0:
            self.wait_and_click([Loc.BTN_BACK])
            current_user = 0

        self.wait_and_click([Loc.BTN_FC])
        self.wait_and_click([Loc.BTN_OK])

    def handle_refresh(self, count_all):
        if count_all:
            count = 0
            for packet in self.page.listen.steps(timeout=60):
                status = get_status(packet)
                logger.debug(status)
                match status:
                    case Status.BATTLE_RESULT:
                        return Status.BATTLE_RESULT
                    case Status.BATTLE_RESULT_EMPTY:
                        return Status.BATTLE_RESULT_EMPTY
                    case Status.BATTLE_FINISH:
                        self.page.refresh()
                        self.page.wait.doc_loaded()
                        continue
                    case Status.BATTLE_LOSE:
                        return Status.BATTLE_LOSE
                    case Status.NOTHING | Status.BATTLE_INIT | Status.BATTLE_START:
                        continue
                    case Status.NET_ERROR:
                        self.page.refresh()
                        self.page.wait(1)
                        self.page.wait.doc_loaded()
                    case _:
                        count += 1
                        if count >= count_all:
                            break

        self.page.stop_loading()
        self.page.refresh()
        self.page.wait.doc_loaded()

    def handle_final_auto(self, current_user):
        if current_user:
            self.wait_and_click([Loc.BTN_BACK])
            self.wait_and_click([Loc.BTN_AUTO])
        else:
            self.wait_and_click([Loc.BTN_AUTO])

    def wait_and_click(self, locs, indices=None):
        """
        等待页面元素加载并点击。

        Args:
            locs (list): 位置字符串列表，用于定位元素。
            indices (list): 可选的索引列表，指定要点击的元素的索引。
        """

        if indices is None:
            indices = []
        # 确保indices列表长度与locs一致，未指定索引的默认为0
        full_indices = indices + [1] * (len(locs) - len(indices))
        for i in range(3):
            try:
                element = self.page
                for loc, index in zip(locs, full_indices):
                    element = element.ele(loc, index=index)

                self.page.wait.ele_hidden("#command-mask")

                element.click()

            except:
                continue
        return
