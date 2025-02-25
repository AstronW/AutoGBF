import sys
import os
import json
import yaml
from PySide6.QtCore import (
    Qt,
    Signal,
    QThread,
)
from PySide6.QtWidgets import (
    QApplication,
)
from qfluentwidgets import (
    FluentWindow,
    PushButton,
    ComboBox,
    LineEdit,
    SpinBox,
    SubtitleLabel,
    CaptionLabel,
    TextBrowser,
    Theme,
    setTheme,
)
from module.solo import Solo
from module.multi import Multi
from copy import deepcopy
from common.baseui import BaseInterface, BaseWindow, SquareIconButton


class Mission(QThread):

    progress_updated = Signal(int)
    task_completed = Signal(str)
    log_signal = Signal(str)

    progress = Signal(str)

    def __init__(self, control_params):
        super().__init__()
        self.control_params = control_params

    def run(self):
        if self.control_params["mode"] == "Solo":
            self.mission = Solo(self.control_params)
        elif self.control_params["mode"] == "Multi":
            self.mission = Multi(self.control_params)
        self.mission.start_mission()

    def stop(self):
        self.control_params["stop"] = True


class SoloInterface(BaseInterface):
    """单人界面类"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("单人模式")
        self.setObjectName("solo")
        self.add_row("副本网址", LineEdit, "url")
        self.add_row("自定义战斗", ComboBox, "custom_battle")
        self.add_row("重复次数", SpinBox, "repeat_count")
        self.add_row(
            "素材选择",
            SquareIconButton,
            "material_select",
            icon_path="resource/settings.png",
        )
        self.add_row("素材数量", SpinBox, "material_count")


class MultiInterface(BaseInterface):
    """多人界面类"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("多人模式")
        self.setObjectName("multi")
        self.params["mode"] = "multi"

        # 创建组件
        self.enableComponent(self.BOSS_HP_RANGE)
        self.enableComponent(self.PLAYER_COUNT_RANGE)
        self.enableComponent(self.TARGET_TURN)
        self.enableComponent(self.CUSTOM_BATTLE)
        self.enableComponent(self.REPEAT_COUNT)
        self.enableComponent(self.TREASURE_SELECT)
        self.enableComponent(self.TREASURE_COUNT)

        # 加载保存的配置

    def onStart(self):
        print("多人模式开始")
        super().onStart()

    def onStop(self):
        print("多人模式停止")
        super().onStop()

    def onSummonSelect(self):
        print("选择召唤石")

    def onMaterialSelect(self):
        print("选择素材")


class SandBoxInterface(BaseInterface):
    """多人界面类"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("沙盒模式")
        self.setObjectName("sandbox")
        self.params["mode"] = "sandbox"

        # 创建组件
        self.enableComponent(self.URL_EDIT)
        self.enableComponent(self.BUFF_COUNT)
        self.enableComponent(self.CUSTOM_BATTLE)
        self.enableComponent(self.REPEAT_COUNT)
        self.enableComponent(self.TREASURE_SELECT)
        self.enableComponent(self.TREASURE_COUNT)

        # 加载保存的配置

    def onMaterialSelect(self):
        print("选择素材")


class HaloInterface(BaseInterface):
    """多人界面类"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("星本模式")
        self.setObjectName("halo")
        self.params["mode"] = "halo"

        # 创建组件
        self.enableComponent(self.URL_EDIT)
        self.enableComponent(self.CUSTOM_BATTLE)
        self.enableComponent(self.REPEAT_COUNT)
        self.enableComponent(self.TREASURE_SELECT)
        self.enableComponent(self.TREASURE_COUNT)

        # 加载保存的配置

    def onMaterialSelect(self):
        print("选择素材")


class TokenInterface(BaseInterface):
    """多人界面类"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("战货模式")
        self.setObjectName("token")
        self.params["mode"] = "token"

        # 创建组件
        self.enableComponent(self.URL_EDIT)
        self.enableComponent(self.CUSTOM_BATTLE)
        self.enableComponent(self.REPEAT_COUNT)
        self.enableComponent(self.TREASURE_SELECT)
        self.enableComponent(self.TREASURE_COUNT)

        # 加载保存的配置

    def onMaterialSelect(self):
        print("选择素材")


class MainWindow(BaseWindow):
    """主窗口类"""

    def __init__(self):
        super().__init__()
        self.initWindow()
        self.stop_button.setEnabled(False)
        # self.loadSettings()

    # def closeEvent(self, event):
    #     """主窗口关闭时保存所有子页面配置"""
    #     config = {}
    #     for interface in self.findChildren(BaseInterface):
    #         params = interface.getCurrentSettings()
    #         module = params["mode"]
    #         data = params["data"]
    #         config[module] = data
    #     with open("config.yaml", "w") as f:
    #         yaml.dump(config, f)
    #     super().closeEvent(event)

    def initWindow(self):
        """初始化窗口"""
        self.setWindowTitle("AutoGBF")

        self.solo_interface = SoloInterface(self)
        # self.multi_interface = MultiInterface(self)
        # self.sandbox_interface = SandBoxInterface(self)
        # self.halo_interface = HaloInterface(self)
        # self.token_interface = TokenInterface(self)
        self.addSubInterface(
            self.solo_interface,
            os.path.join("assets", "icons", "single.png"),
            "单人",
        )
        # self.addSubInterface(
        #     self.multi_interface,
        #     os.path.join("assets", "icons", "single.png"),
        #     "多人",
        # )
        # self.addSubInterface(
        #     self.sandbox_interface,
        #     os.path.join("assets", "icons", "single.png"),
        #     "沙盒",
        # )
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

    # def loadSettings(self):
    #     with open("config.yaml", "r") as f:
    #         config = yaml.load(f, Loader=yaml.FullLoader)
    #     for module, data in config.items():
    #         interface = self.findChild(BaseInterface, module)
    #         interface.setCurrentSettings(data)

    def onStart(self):
        self.data = self.stackedWidget.currentWidget().getCurrentSettings()
        self.stop_button.setEnabled(True)

    def onStop(self):
        self.data["stop"] = True
        self.start_button.setEnabled(True)


def init_gui():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    setTheme(Theme.AUTO)
    # 创建主窗口
    window = MainWindow()

    window.show()
    app.exec()


if __name__ == "__main__":
    init_gui()
