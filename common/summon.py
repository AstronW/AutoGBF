from logger import logger
from common.constants import Loc
from common.status import Status, get_status
import cv2
from DrissionPage._pages.mix_tab import MixTab
from common.ocr import Ocr


class Summon:
    def __init__(self, page : MixTab):
        self.page = page
        self.ocr = Ocr(self.page)

    def find_summon(self, sum_id : str):
        logger.info("开始寻找召唤石")
        for packet in self.page.listen.steps(timeout=10):
            status = get_status(packet)
            match status:
                case Status.SUPPORT:
                    summon =  self.click_summon(sum_id)
                case Status.CODE_FALSE | Status.CODE_POP:
                    res, image = self.ocr.send_code()
                case Status.CODE_TRUE:
                    cv2.imwrite(f"assets/img/{res}.png", image)
                    summon.run_js("this.scrollIntoView()")
                    summon.click()
                case Status.PARTY_CLICK:
                    self.page.ele(Loc.BTN_OK).click()
                case Status.NET_ERROR:
                    self.page.refresh()
                    self.page.wait.doc_loaded()
                case Status.RAID_CREATE_FALSE:
                    return False
                case Status.RAID_CREATE:
                    return True
                case _:
                    pass
        self.page.refresh()
        self.page.wait.doc_loaded()
        return self.find_summon(sum_id)
    
    def click_summon(self, sum_id : str):
        list_summon_id = [sum_id + '_04', sum_id + '_03', sum_id + '_02', sum_id]
        list_summon_info = self.page.eles(Loc.SUM_INFO)
        
        try:
            id, summon_info = next(
                (id, info) for id in list_summon_id
                for info in list_summon_info
                if info.attr("data-image") == id
            )
            summon = summon_info.parent(2)
            logger.info(f"找到召唤石{id}")
        except StopIteration:
            logger.info(f"未找到召唤石{sum_id}")
            summon = list_summon_info[0].parent(2)
        
        summon.run_js("this.scrollIntoView()")
        summon.click()
        return True
