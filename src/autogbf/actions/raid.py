from DrissionPage._pages.mix_tab import MixTab
from ...utils.logger import logger
from ..metadata.constants import Loc, Url
from ..metadata.status import Status, get_status


class Raid:
    def __init__(self, page: MixTab):
        self.page = page

    def click_ele(self, loc: str, index: int = 1):
        ele = self.page.ele(loc, index)
        ele.run_js("this.scrollIntoView();", timeout=3)
        ele.click()

    def find_raid(self, raid_data: tuple, method: int = 1):
        logger.info(f"开始寻找副本")
        match method:
            case 1:
                return self.find_raid_normal(raid_data)
            case 2:
                return self.find_raid_event(raid_data)
            case _:
                raise ValueError()

    def find_raid_normal(self, data: tuple):
        if self.page.url != Url.MULTI_RAID:
            self.page.get(Url.MULTI_RAID)
            self.page.wait.doc_loaded()
        # self.page.listen.clear()
        self.page.ele(Loc.RAID_REFRESH).click()
        while True:
            for packet in self.page.listen.steps(timeout=10):
                status = get_status(packet)
                logger.info(status)
                match status:
                    case Status.NET_ERROR:
                        self.page.refresh()
                        self.page.wait(1)
                        self.page.wait.doc_loaded()
                    case Status.ASSIST_DISABLE:
                        self.page.ele(Loc.RAID_REFRESH).click()
                    case Status.ASSIST_ENABLE:
                        self.click_raid(packet, data)
                    case Status.RAID_DISABLE:
                        self.page.ele(Loc.BTN_OK).click()
                        self.page.ele(Loc.RAID_REFRESH).click()
                    case Status.RAID_ENABLE:
                        return
                    case _:
                        pass
            self.click_ele(Loc.RAID_REFRESH)

    def find_raid_event(self, data: tuple):
        self.page.get(Url.MULTI_EVENT)
        self.page.ele(Loc.RAID_REFRESH_EVENT).click()
        while True:
            for packet in self.page.listen.steps(timeout=10):
                status = get_status(packet)
                match status:
                    case Status.NET_ERROR:
                        self.page.refresh()
                        self.page.wait(1)
                        self.page.wait.doc_loaded()
                    case Status.ASSIST_DISABLE:
                        self.page.ele(Loc.RAID_REFRESH_EVENT).click()
                    case Status.ASSIST_ENABLE:
                        self.click_raid(packet, data, 1)
                    case Status.RAID_DISABLE:
                        self.page.ele(Loc.BTN_OK).click()
                        self.page.ele(Loc.RAID_REFRESH_EVENT).click()
                    case Status.RAID_ENABLE:
                        return
                    case _:
                        pass
            self.click_ele(Loc.RAID_REFRESH_EVENT)

    def click_raid(self, packet, data: dict, method: int = 0):
        index = 0
        (hp_min, hp_max, join_min, join_max) = data
        for i, cmd in enumerate(packet.response.body.get("assist_raids_data"), 1):
            boss_hp = cmd.get("boss_hp_width")  # BOSS剩余血量
            member_count = cmd.get("member_count")  # 已加入人数
            is_fp = cmd.get("is_unpopular")  # 是否是FP本
            if hp_min <= boss_hp <= hp_max and join_min <= member_count <= join_max:
                index = i
                if method == 2:
                    used_battle_point = cmd.get("used_battle_point")
                    raid_data = cmd.get("raid")
                    multi_raid_id = raid_data.get("multi_raid_id")
                    quest_id = raid_data.get("quest_id")
                if is_fp:
                    break
        if index:
            if method == 0:
                self.click_ele(Loc.LIST_RAID, index)
            elif method == 1:
                self.click_ele(Loc.LIST_RAID_EVENT, index)
            elif method == 2:
                self.page.get(
                    Url.RAID_DETAIL_URL.format(
                        multi_raid_id=multi_raid_id,
                        quest_id=quest_id,
                        used_battle_point=used_battle_point,
                    )
                )
                return True
        else:
            if method == 0:
                self.click_ele(Loc.RAID_REFRESH)
            elif method == 1:
                self.click_ele(Loc.RAID_REFRESH_EVENT)
            elif method == 2:
                self.click_ele(Loc.RAID_REFRESH)
                return False
