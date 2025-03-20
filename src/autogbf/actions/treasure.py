from ..metadata.constants import Loc
from DrissionPage._pages.mix_tab import MixTab
import os


class Treasure:
    def __init__(self, page: MixTab):
        self.page = page

    def find_treasure(self, treasure_id: str) -> int:
        list_treasure = self.page.eles(Loc.LIST_TREASURE)
        for treasure in list_treasure:
            if treasure.child().attr("data-item-id") == treasure_id:
                return int(treasure.child().child(2).text)
        return 0

    def get_treasure_list(self) -> list:
        list_treasure = []
        if "game.granbluefantasy.jp" not in self.page.url:
            return list_treasure
        ele_treasure = self.page.eles(".prt-treasure-wrapper")
        for ele in ele_treasure:
            data_item_id = ele.attr("data-item-id")
            list_treasure.append(data_item_id)
            if not os.path.exists("./assets/treasure/%s.jpg" % data_item_id):
                img = ele("t:img")
                # 保存图片
                img.save("./assets/treasure")
        return list_treasure
