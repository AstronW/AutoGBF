import sys
import os
from PySide6.QtCore import (
    Qt,
    Signal,
    QThread,
)
from PySide6.QtWidgets import (
    QApplication,
)
from qfluentwidgets import (
    ComboBox,
    LineEdit,
    SpinBox,
    RadioButton,
    Theme,
    setTheme,
)
from ..module import Solo, Multi, SandBox
from .baseui import BaseInterface, BaseWindow, TreasureButton
from .widgets.range_slider import RangeSlider


class Mission(QThread):
    """任务线程类，用于在后台执行耗时操作"""

    progress_updated = Signal(int)  # 进度更新信号
    task_completed = Signal(str)  # 任务完成信号
    log_signal = Signal(str)  # 日志信号
    progress = Signal(str)  # 进度信息信号

    def __init__(self, control_params):
        super().__init__()
        self.control_params = control_params
        self.mission = None

    def run(self):
        """线程主运行方法，根据模式创建相应的任务实例"""
        if self.control_params["mode"] == "solo":
            self.mission = Solo()
        elif self.control_params["mode"] == "multi":
            self.mission = Multi()
        elif self.control_params["mode"] == "sandbox":
            self.mission = SandBox()
        self.mission.start_mission(self.control_params)

    def stop(self):
        """停止当前任务"""
        self.control_params["stop"] = True


class SoloInterface(BaseInterface):
    """单人任务界面类"""

    def __init__(self, parent=None, browser=None):
        super().__init__(parent, browser)
        self.setTitle("单人模式")
        self.setObjectName("solo")

        # 添加界面控件
        self.addRow("副本网址", LineEdit, "url")
        self.addRow("自定义战斗", ComboBox, "custom_battle")
        self.addRow("重复次数", SpinBox, "repeat_count")
        self.addRow(
            "素材选择",
            TreasureButton,
            "treasure_id",
            icon_path="./assets/treasure/settings.png",
        )
        self.addRow("素材数量", SpinBox, "treasure_count")


class MultiInterface(BaseInterface):
    """多人任务界面类"""

    def __init__(self, parent=None, browser=None):
        super().__init__(parent, browser)
        self.setTitle("多人模式")
        self.setObjectName("multi")

        # 创建组件
        self.addRow(
            "Boss血量",
            RangeSlider,
            "boss_hp",
            min=0,
            max=100,
            left=0,
            right=100,
        )
        self.addRow(
            "玩家数量",
            RangeSlider,
            "player_count",
            min=0,
            max=30,
            left=0,
            right=30,
        )
        self.addRow("模式选择", RadioButton, "method", items=["通常", "活动"])
        self.addRow("目标回合", SpinBox, "target_turn")
        self.addRow("自定义战斗", ComboBox, "custom_battle")
        self.addRow("重复次数", SpinBox, "repeat_count")
        self.addRow(
            "素材选择",
            TreasureButton,
            "treasure_id",
            icon_path="./assets/treasure/settings.png",
        )
        self.addRow("素材数量", SpinBox, "treasure_count")


class SandBoxInterface(BaseInterface):
    """沙盒模式界面类"""

    def __init__(self, parent=None, browser=None):
        super().__init__(parent, browser)
        self.setTitle("沙盒模式")
        self.setObjectName("sandbox")

        self.addRow("副本网址", LineEdit, "url")
        self.addRow("Buff次数", SpinBox, "buff_count")
        self.addRow("自定义战斗", ComboBox, "custom_battle")
        self.addRow("重复次数", SpinBox, "repeat_count")
        self.addRow(
            "素材选择",
            TreasureButton,
            "treasure_id",
            icon_path="./assets/treasure/settings.png",
        )
        self.addRow("素材数量", SpinBox, "treasure_count")


class HaloInterface(BaseInterface):
    """星本模式界面类"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("星本模式")
        self.setObjectName("halo")

        # 启用需要的组件
        self.enableComponent(self.URL_EDIT)
        self.enableComponent(self.CUSTOM_BATTLE)
        self.enableComponent(self.REPEAT_COUNT)
        self.enableComponent(self.TREASURE_SELECT)
        self.enableComponent(self.TREASURE_COUNT)

    def onMaterialSelect(self):
        """素材选择事件处理"""
        print("选择素材")


class TokenInterface(BaseInterface):
    """战货模式界面类"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("战货模式")
        self.setObjectName("token")
        self.params["mode"] = "token"

        # 启用需要的组件
        self.enableComponent(self.URL_EDIT)
        self.enableComponent(self.CUSTOM_BATTLE)
        self.enableComponent(self.REPEAT_COUNT)
        self.enableComponent(self.TREASURE_SELECT)
        self.enableComponent(self.TREASURE_COUNT)


class MainWindow(BaseWindow):
    """主窗口类"""

    def __init__(self, page):
        super().__init__()
        self.browser = page
        self.values = {}  # 存储当前值的字典
        self.pages = {}  # 页面映射字典

        self.initWindow()
        # 加载配置
        self.load_config()
        self.stop_button.setEnabled(False)

    def initWindow(self):
        """初始化窗口"""
        self.setWindowTitle("AutoGBF")
        self.changeBotton(False)

        # 创建界面实例
        self.solo_interface = SoloInterface(self, self.browser)
        self.multi_interface = MultiInterface(self, self.browser)
        # 下面的界面暂时注释掉，未实际使用
        self.sandbox_interface = SandBoxInterface(self, self.browser)
        # self.halo_interface = HaloInterface(self)
        # self.token_interface = TokenInterface(self)

        # 添加界面到窗口
        self.addSubInterface(
            self.solo_interface,
            os.path.join("assets", "icons", "single.png"),
            "单人",
        )
        self.addSubInterface(
            self.multi_interface,
            os.path.join("assets", "icons", "single.png"),
            "多人",
        )
        # 下面的界面暂时注释掉，未实际使用
        self.addSubInterface(
            self.sandbox_interface,
            os.path.join("assets", "icons", "single.png"),
            "沙盒",
        )
        # self.addSubInterface(
        #     self.halo_interface,
        #     os.path.join("assets", "icons", "single.png"),
        #     "星本",
        # )
        # self.addSubInterface(
        #     self.token_interface,
        #     os.path.join("assets", "icons", "single.png"),
        #     "战货",
        # )

        # 页面映射字典，用于在页面间切换
        self.pages = {
            "solo": self.solo_interface,
            "multi": self.multi_interface,
            "sandbox": self.sandbox_interface,
            # "halo": self.halo_interface,
            # "token": self.token_interface,
        }

    def onStart(self):
        """开始按钮点击事件处理"""
        self.values = {}
        current_page = self.stackedWidget.currentWidget()

        if isinstance(current_page, BaseInterface):
            # 获取当前页面的值
            self.values = current_page.getValues()

            # 根据当前页面设置模式
            self.values["mode"] = next(
                (key for key, value in self.pages.items() if value == current_page),
                None,
            )

            # 设置停止标志为False
            self.values["stop"] = False

            # 创建并启动任务线程
            mission = Mission(self.values)
            mission.finished.connect(lambda: mission.deleteLater())
            mission.finished.connect(lambda: self.changeBotton(False))
            mission.start()

            # 日志输出
            print(f"当前页面 ({current_page.__class__.__name__}) 的值：{self.values}")
            self.textBrowser.append(
                f"当前页面 ({current_page.__class__.__name__}) 的值：{self.values}"
            )

        # 更新按钮状态
        self.changeBotton(True)

    def onStop(self):
        """停止按钮点击事件处理"""
        self.values["stop"] = True
        self.stop_button.setEnabled(False)

        # 日志输出
        print(f"停止任务，当前值：{self.values}")
        self.textBrowser.append(f"停止任务，当前值：{self.values}")

    def changeBotton(self, is_start: bool):
        """切换按钮状态"""
        self.start_button.setEnabled(not is_start)
        self.stop_button.setEnabled(is_start)


def init_gui(page):
    """初始化GUI应用"""
    # 设置高DPI策略
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    setTheme(Theme.AUTO)  # 设置主题

    # 创建并显示主窗口
    window = MainWindow(page)
    window.show()

    # 运行应用
    app.exec()


if __name__ == "__main__":
    init_gui()
