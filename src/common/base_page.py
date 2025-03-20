from DrissionPage import Chromium, ChromiumOptions
from DrissionPage._pages.mix_tab import MixTab
import os

PATH_USER_DATA = r"./UserData"


class BasePage:
    def __init__(self) -> None:
        self.init_chrome()

    def init_chrome(self) -> None:
        """初始化chrome"""
        co = ChromiumOptions()
        co.set_local_port(9333)
        if os.path.exists(PATH_USER_DATA):
            co.set_user_data_path(path=PATH_USER_DATA)
        co.set_argument("useAutomationExtension", False)
        co.set_argument("excludeSwitches", ["enable-automation"])
        co.set_argument("--disable-background-networking")  # 关闭更新提示
        co.set_load_mode("eager")
        self.chromium = Chromium(co)
        self.chromium.set.auto_handle_alert(True)
        self.chromium.set.timeouts(base=10, page_load=10, script=10)
        self.chromium.set.retry_times(5)
        self.chromium.set.retry_interval(2)
        self.page: MixTab = self.chromium.get_tab(1)
        self.page.set.scroll.smooth(on_off=False)
        self.page.set.auto_handle_alert(True)

    def get_page(self):
        return self.page

    def quit_chromium(self):
        self.chromium.quit()


if __name__ == "__main__":
    dp = BasePage()
