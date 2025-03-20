from DrissionPage._pages.mix_tab import MixTab
import numpy as np
import cv2
import ddddocr
from ...utils.logger import logger
from ..metadata.status import Status, get_status
from ..metadata.constants import Loc


class Party:
    """
    处理召唤相关操作的类

    Attributes:
        page (MixTab): 用于操作网页的MixTab对象
        ocr (ddddocr.DdddOcr): 用于验证码识别的DdddOcr对象
    """

    def __init__(self, page: MixTab):
        """
        初始化Party类

        Args:
            page (MixTab): 用于操作网页的MixTab对象
        """
        self.page = page
        self.ocr = ddddocr.DdddOcr(show_ad=False)
        self.ocr.set_ranges(4)

    def check_party(self) -> bool:
        """
        检查召唤状态，直到达到召唤启用或禁用的状态

        Returns:
            bool: 如果召唤启用则返回True，如果召唤禁用则返回False
        """
        while True:
            for packet in self.page.listen.steps(timeout=10):
                status = get_status(packet)
                logger.debug(status)
                match status:
                    case Status.SUMMON_INIT:
                        # 处理召唤初始化状态
                        self.page.wait(0.1)
                        self.page.ele(Loc.BTN_OK).click()
                    case Status.CODE_FALSE | Status.CODE_INIT:
                        # 处理验证码错误或初始化状态
                        res, image = self.ocr.send_code()
                    case Status.CODE_TRUE:
                        # 处理验证码正确状态，保存验证码图片
                        cv2.imwrite(f"assets/img/{res}.png", image)
                    case Status.CODE_NONE:
                        # 处理没有验证码的状态
                        self.page.wait(0.1)
                        self.page.ele(Loc.BTN_OK).click()
                    case Status.SUMMON_DISABLE:
                        # 如果召唤禁用，返回False
                        return False
                    case Status.SUMMON_ENABLE:
                        # 如果召唤启用，返回True
                        return True
                    case _:
                        # 其他状态不做处理
                        pass
            # 如果没有达到期望的状态，则刷新页面并等待页面加载
            self.page.refresh()
            self.page.wait.doc_loaded()

    def send_code(self) -> tuple[str, np.ndarray]:
        """
        发送验证码

        Returns:
            tuple: 识别的验证码结果和验证码图片
        """
        code_input = self.page.ele(".frm-message")
        btn_send = self.page.ele(".btn-talk-message")
        # 获取验证码图片并处理
        img = self.page.ele(".image").src()
        byte_array = np.frombuffer(img, dtype=np.uint8)
        image = cv2.imdecode(byte_array, cv2.IMREAD_COLOR)
        gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        new_img = gray_img[1:][:]
        h, w = new_img.shape[:2]

        # 二值化处理验证码图片
        for i in range(1, h):
            for j in range(1, w):
                if new_img[i, j] == 2:
                    new_img[i, j] = 215
                if new_img[i, j] > 160:
                    new_img[i, j] = 255
                else:
                    new_img[i, j] = 0
        _, encoded_image = cv2.imencode(".png", new_img)
        img_bytes = encoded_image.tobytes()
        logger.info("识别验证码")
        res = self.ocr.classification(img_bytes, probability=True)
        s = ""
        for i in res["probability"]:
            s += res["charsets"][i.index(max(i))]
        logger.info(f"当前识别结果为{s}")
        # 输入验证码并发送
        code_input.input(s)
        self.page.wait(0.5)
        btn_send.click()
        return s, image
