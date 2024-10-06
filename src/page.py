from DrissionPage import WebPage, ChromiumOptions
import os


IS_107 = True
PATH_CHROME = r"./Chrome/App/chrome.exe"    # chrome路径


class Custom_Page(WebPage):
    def _handle_alert(self, accept=True, send=None, timeout=None, next_one=True):  # 改变默认值
        super()._handle_alert(accept, send, timeout, next_one)  # 调用基类方法

    # def handle_alert(self, accept=True, send=None, timeout=None, next_one=False):
    #     """处理提示框，可以自动等待提示框出现
    #     :param accept: True表示确认，False表示取消，为None不会按按钮但依然返回文本值
    #     :param send: 处理prompt提示框时可输入文本
    #     :param timeout: 等待提示框出现的超时时间（秒），为None则使用self.timeout属性的值
    #     :param next_one: 是否处理下一个出现的提示框，为True时timeout参数无效
    #     :return: 提示框内容文本，未等到提示框则返回False
    #     """
    #     r = self._handle_alert(accept=accept, send=send, timeout=timeout, next_one=next_one)
    #     if not isinstance(accept, bool):
    #         return r
    #     while self._has_alert:
    #         if r:
    #             self.run_cdp('Page.reload', ignoreCache=False)
    #             self.wait.load_start()
    #         sleep(.1)
    #     return r


class DPage:
    def __init__(self):
        self.init_chrome()
        self.page.set.scroll.smooth(on_off=False)
        self.page.set.scroll.wait_complete(on_off=True)
        self.page.set.auto_handle_alert(all_tabs=True)    # 设置全局弹窗自动处理

    def init_chrome(self):
        """初始化chrome"""
        self.co = ChromiumOptions()
        self.co.set_local_port(9333)
        if os.path.exists(PATH_CHROME):
            self.co.set_browser_path(path=PATH_CHROME)    # 设置浏览器路径
            self.co.use_system_user_path(True)    # 使用默认用户数据
        self.co.set_argument('--disable-background-networking')    # 关闭更新提示
        # self.co.set_argument('--no-sandbox')
        self.page = Custom_Page(chromium_options=self.co)

    def quit(self):
        return self.page.quit()

    def get(self, url):
        return self.page.get(url)

    def click_ele(self, locator, index=1, timeout=None):
        ele = self.page.ele(locator, index, timeout)
        ele.run_js("this.scrollIntoView();", timeout=3)
        ele.click()


if __name__ == '__main__':
    dp = DPage()
