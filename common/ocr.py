import numpy as np
import cv2
import ddddocr
from logger import logger
from DrissionPage._pages.mix_tab import MixTab


class Ocr:
    def __init__(self, page : MixTab):
        self.page = page
        self.ocr = ddddocr.DdddOcr(show_ad=False)
        self.ocr.set_ranges(4)

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