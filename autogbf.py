from common.base import BasePage
from common.summon import Summon
from common.battle import Battle
from common.constants import Pat
from common.treasure import Treasure
from common.raid import Raid
from common.record import Record

class AutoGBF(BasePage):
    def __init__(self):
        super().__init__()
        self.summon = Summon(self.page)
        self.battle = Battle(self.page)
        self.treasure = Treasure(self.page)
        self.raid = Raid(self.page)
        self.record = Record(self.page)

    def start_listen(self):
        list_pat = []
        
        for i in Pat:
            list_pat.append(i.value)

        self.page.listen.start(list_pat, is_regex=True)
        # self.page.listen.start([Pat.ATT, Pat.RAID_START, Pat.RESULT, Pat.SUM, Pat.CODE, Pat.RAID_CREATE, Pat.ASSIST_LIST, Pat.RAID_CHECK],
        #                        is_regex=True)
    
    def find_raid(self, raid_data : tuple, method : int, ):
        return self.raid.find_raid(raid_data, method)

    def find_summon(self, sum_id : str):
        return self.summon.find_summon(sum_id)
    
    def start_battle(self, goal_turn : int = 0, custom : str = None):
        return self.battle.start_battle(goal_turn, custom)

    def find_treasure(self, treasure_id: str) -> int:
        return self.treasure.find_treasure(treasure_id)
    
    def record_raid(self):
        return self.record.record_battle()


if __name__ == "__main__":
    autogbf = AutoGBF()
