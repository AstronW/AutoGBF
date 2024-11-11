from common.constants import Loc
from DrissionPage._pages.mix_tab import MixTab
from DrissionPage._elements.chromium_element import ChromiumElement


class Treasure:
    def __init__(self, page: MixTab):
        self.page = page

    def find_treasure(self, treasure_id: str) -> int:
        list_treasure = self.page.eles(Loc.LIST_TREASURE)
        for treasure in list_treasure:
            treasure: ChromiumElement
            if treasure.child().attr("data-item-id") == treasure_id:
                return int(treasure.child().child(2).text)
        return -1
