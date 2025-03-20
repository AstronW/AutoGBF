from DrissionPage._pages.mix_tab import MixTab
from ..utils.logger import logger
from .actions.party import Party
from .actions.battle import Battle
from .actions.raid import Raid
from .actions.treasure import Treasure
from .metadata.status import Status


class AutoGBF:
    """
    AutoGBF类是一个游戏自动化工具类，提供了一系列方法来自动执行游戏中的各种操作。

    Attributes:
        page (MixTab): 一个MixTab对象，代表游戏页面，用于执行具体的操作。
        party (Party): Party模块，用于管理队伍相关操作。
        battle (Battle): Battle模块，用于管理战斗相关操作。
        raid (Raid): Raid模块，用于管理共斗相关操作。
        treasure (Treasure): Treasure模块，用于管理宝藏相关操作。
    """

    def __init__(self, page: MixTab):
        """
        初始化AutoGBF类。

        Args:
            page (MixTab): 一个MixTab对象，用于执行具体的游戏操作。
        """
        self.page = page
        self.party = Party(self.page)
        self.battle = Battle(self.page)
        self.raid = Raid(self.page)
        self.treasure = Treasure(self.page)

    def check_party(self):
        """
        检查队伍状态。

        Returns:
            队伍状态检查结果。
        """
        return self.party.check_party()

    def start_battle(self, goal_turn: int = 0, custom: str = None) -> Status:
        """
        开始战斗。

        Args:
            goal_turn (int, optional): 目标回合数。默认为0。
            custom (str, optional): 自定义战斗指令。默认为None。

        Returns:
            Status: 战斗结束后的状态。
        """
        return self.battle.start_battle(goal_turn, custom)

    def find_raid(self, raid_data: tuple, method: int = 1) -> None:
        """
        寻找共斗。

        Args:
            raid_data (tuple): 共斗数据，包含识别共斗所需的信息。
            method (int, optional): 寻找共斗的方法。默认为1。

        Returns:
            None
        """
        return self.raid.find_raid(raid_data, method)

    def find_treasure(self, treasure_id: str) -> int:
        """
        寻找宝藏。

        Args:
            treasure_id (str): 宝藏ID，用于识别特定的宝藏。

        Returns:
            int: 寻找宝藏的结果。
        """
        return self.treasure.find_treasure(treasure_id)

    def get_treasure_list(self) -> list:
        """
        获取宝藏列表。

        Returns:
            list: 宝藏列表。
        """
        return self.treasure.get_treasure_list()
