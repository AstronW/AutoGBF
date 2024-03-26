from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import os
from logger import logger
from selector.base import *
import time
from bs4 import BeautifulSoup
from selenium.common.exceptions import WebDriverException


PATH_CHROME = r"\Chrome\App\Chrom.exe"
PATH_USER_DATA_DIR = r"\Chrome\Data"
PATH_CHROMEDRIVER = r"\Chrome\chromedriver.exe"
PATH_ROOT = r'.\AutoGBF.exe'

CHROME_HEIGHT = "return document.documentElement.scrollHeight"
SCROLL_INTO_VIEW = "arguments[0].scrollIntoView();"
GET_UA = "return navigator.userAgent"

URL_HOME = "https://game.granbluefantasy.jp/#mypage"

DELAY_TIME = 10
DELAY_DISPLAY = 60


class Driver:
    def start_chrome(self):
        """初始化浏览器"""
        basepath = os.path.dirname(os.path.abspath(__file__))
        basepath = "\\".join(basepath.split("\\")[:-1])
        caps = {
            "browserName": "chrome",
            'goog:loggingPrefs': {'performance': 'ALL'}  # 开启日志性能监听
        }
        option = Options()
        for key, value in caps.items():
            option.set_capability(key, value)
        option.add_experimental_option("detach", True)
        option.add_experimental_option(
            "excludeSwitches", ["enable-automation", "enable-logging"]
        )
        option.binary_location = basepath + PATH_CHROME
        option.add_argument(f"--user-data-dir={basepath + PATH_USER_DATA_DIR}")
        service = ChromeService(executable_path=basepath + PATH_CHROMEDRIVER)
        self.driver = webdriver.Chrome(service=service, options=option)
        self.change_wait(DELAY_TIME)
        logger.info("浏览器初始化成功")
        try:
            self.get_url(URL_HOME)
        except WebDriverException:
            logger.error("请检查网络")
        return self.driver

    def stop_chrome(self):
        """关闭浏览器"""
        self.driver.quit()

    def change_wait(self, time):
        """设置等待时间"""
        self.driver.implicitly_wait(time)

    def find_element(self, *selector):
        """查找元素"""
        if len(selector) == 1:
            return self.driver.find_element(By.CSS_SELECTOR, selector[0])
        else:
            return selector[0].find_element(By.CSS_SELECTOR, selector[1])

    def find_element_list(self, selector):
        """查找元素列表"""
        return self.driver.find_elements(By.CSS_SELECTOR, selector)

    def click_element(self, selector):
        """点击元素"""
        self.driver.find_element(By.CSS_SELECTOR, selector).click()

    def get_url(self, url):
        """打开网址"""
        self.driver.get(url)

    def wait_element_display(self, selector, timeout=20):
        """等待元素出现"""
        WebDriverWait(self.driver, timeout).until(
            lambda driver: driver.find_element(By.CSS_SELECTOR, selector).is_displayed()
        )

    def wait_element_disappear(self, selector, timeout=20):
        """等待元素消失"""
        WebDriverWait(self.driver, timeout).until_not(
            lambda driver: driver.find_element(By.CSS_SELECTOR, selector).is_displayed()
        )

    def wait_url(self, url):
        """等待网址出现"""
        WebDriverWait(self.driver, 20).until(
            lambda x: x.current_url.split("/")[3] in url
        )

    def element_is_displayed(self, selector):
        """判断元素是否出现"""
        return self.driver.find_element(By.CSS_SELECTOR, selector).is_displayed()

    def find_summon(self, id, module='solo'):
        """寻找召唤石"""
        base_summon_id = id.split("_")[0]
        list_summon_id = [base_summon_id + '_04', base_summon_id + '_03', base_summon_id + '_02', base_summon_id]
        logger.info("正在寻找合适的召唤石")
        list_summon = self.find_element_list(LIST_SUMMON)  # noqa F405
        list_id_summon = self.find_element_list(LIST_ID_SUMMON)  # noqa F405
        height = self.driver.execute_script(CHROME_HEIGHT)  # noqa F405
        offset = (height - 43) // 81 - 2
        for summon_id in list_summon_id:
            for i in range(len(list_summon)):
                if (
                    self.get_attribute(list_id_summon[i], "data-image") == summon_id
                ):
                    logger.info(f"已找到指定的召唤石:{summon_id}")
                    logger.debug(f"召唤石位置: {i}")
                    if i > offset:
                        self.driver.execute_script(SCROLL_INTO_VIEW, list_summon[i - offset])  # noqa F405
                        list_summon[i].click()
                    else:
                        self.driver.execute_script(SCROLL_INTO_VIEW, list_summon[i])  # noqa F405
                        list_summon[i].click()
                    time.sleep(0.5)
                    if self.find_pop():
                        self.send_code()
                        time.sleep(1)
                        list_summon[i].click()
                    else:
                        pass
                    self.click_element(BTN_SUP_OK)  # noqa F405
                    time.sleep(1)
                    if module == 'multi':
                        if "quest" in self.driver.current_url:
                            logger.info("无法进入房间，重新选择副本")
                            self.driver.back()
                            return False
                    return True
        logger.info("未找到指定的召唤石")
        logger.info("已选择默认的召唤石")
        list_summon[0].click()
        time.sleep(0.5)
        if self.find_pop():
            self.send_code()
            time.sleep(1)
            list_summon[0].click()
        else:
            pass
        self.click_element(BTN_SUP_OK)  # noqa F405
        time.sleep(1)
        if module == 'multi':
            if "quest" in self.driver.current_url:
                logger.info("无法进入房间，重新选择副本")
                self.driver.back()
                return False
        return True

    def get_attribute(self, *selector):
        """查看元素的属性"""
        if len(selector) == 2:
            if isinstance(selector[0], str):
                return self.find_element(selector[0]).get_attribute(selector[1])
            else:
                return selector[0].get_attribute(selector[1])
        else:
            return self.find_element(selector[0], selector[1]).get_attribute(selector[2])

    def get_treasure_id(self):
        '''获取已登记素材id'''
        list_treasure = self.find_element_list(LIST_TREASURE)  # noqa F405
        list_id = []
        for treasure in list_treasure:
            list_id.append(self.get_attribute(treasure, "data-item-id"))
        return list_id

    def find_pop(self):
        """寻找弹窗"""
        pop0 = self.find_element(POP0)  # noqa F405
        pop0_html = self.get_attribute(pop0, "outerHTML")
        soup0 = BeautifulSoup(pop0_html, "html.parser")
        pop1 = self.find_element(POP)  # noqa F405
        pop1_html = self.get_attribute(pop1, "outerHTML")
        soup1 = BeautifulSoup(pop1_html, "html.parser")
        return max(len(soup0.find_all()), len(soup1.find_all())) > 1

    def send_code(self):
        import ddddocr
        import requests
        from cv2 import imread, imwrite, cvtColor, COLOR_BGR2GRAY
        """发送验证码"""
        img = None
        time.sleep(2)
        count = 0
        session = requests.session()
        cookies = self.driver.get_cookies()
        UA = self.driver.execute_script(GET_UA)  # noqa F405
        headers = {
            'User-Agent': UA,
        }
        for cookie in cookies:
            session.cookies.set(cookie["name"], cookie["value"])
        code_img = self.find_element(CODER_IMAGE)  # noqa F405
        src = self.get_attribute(code_img, "src")
        while self.find_code():
            req = session.get(url=src, headers=headers)
            text = req.content
            with open('code.png', 'wb') as f:
                f.write(text)
            img = imread("code.png")
            gray_img = cvtColor(img, COLOR_BGR2GRAY)
            new_img = gray_img[1:][:]

            for i in range(1, 48):
                for j in range(1, 129):
                    if new_img[i, j] == 2:
                        new_img[i, j] = 215
                    if new_img[i, j] > 160:
                        new_img[i, j] = 255
                    else:
                        new_img[i, j] = 0

            imwrite("code.png", new_img)
            with open("code.png", "rb") as f:
                image = f.read()
            ocr = ddddocr.DdddOcr()
            res = ocr.classification(image)
            code_inter = self.find_element(CODER_INTER)  # noqa F405
            code_inter.send_keys(res)
            self.click_element(CODER_SEND)  # noqa F405
            time.sleep(1)
            count += 1
            if count > 50:
                return
        logger.attr("CODE", res)
        imwrite("assets/img/%s.png" % res, img)
        try:
            os.remove("code.png")
        except Exception:
            pass
        session.close()
        return

    def find_code(self):
        pop = self.find_element(POP0)  # noqa F405
        pop_html = self.get_attribute(pop, "outerHTML")
        soup = BeautifulSoup(pop_html, "html.parser")
        return len(soup.find_all()) > 1

    def find_treasure(self, treasure_id):

        if treasure_id is None:
            return 0

        list_treasure = self.find_element_list(LIST_TREASURE)  # noqa F405
        list_count_treasure = self.find_element_list(LIST_COUNT_TREASURE)  # noqa F405

        for i in range(len(list_treasure)):
            if self.get_attribute(list_treasure[i], "data-item-id") == treasure_id:
                if self.get_attribute(list_count_treasure[i], 'innerHTML') != "":
                    return int(
                        self.get_attribute(list_count_treasure[i], 'innerHTML').split('/')[0]
                    )
                else:
                    return 0

        return 0

    def run_js(self, *js):
        """执行js"""
        return self.driver.execute_script(js)

    def quit(self):
        self.driver.quit()

    def chrome_is_exist(self):
        try:
            self.driver.execute_script('javascript:void(0);')
            return True
        except Exception:
            return False


if __name__ == "__main__":
    driver = Driver()
    driver.start_chrome()
    time.sleep(3)
    list_id = driver.get_treasure_id()
    print(list_id)
