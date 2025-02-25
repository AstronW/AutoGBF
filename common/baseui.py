import sys
import os
import json
from PySide6.QtCore import (
    Qt,
    QSize,
)
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
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
    setFont,
)

from range_slider import RangeSlider


class ConfigManager:
    """配置管理类，负责保存和加载配置"""

    CONFIG_FILE = "config.json"

    @staticmethod
    def load_config():
        """加载配置"""
        if os.path.exists(ConfigManager.CONFIG_FILE):
            with open(ConfigManager.CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    @staticmethod
    def save_config(config):
        """保存配置"""
        with open(ConfigManager.CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)


class SquareIconButton(PushButton):
    """正方形图标按钮"""

    def __init__(self, icon_path, parent=None):
        super().__init__(parent)
        self.setIcon(QIcon(icon_path))
        self.setFixedSize(QSize(48, 48))  # 设置固定大小
        self.setIconSize(QSize(32, 32))  # 设置图标大小


class BaseInterface(QWidget):
    """子页面基类"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.titleLabel = SubtitleLabel(self)
        # self.titleLabel.setFixedWidth(400)
        self.layout.addWidget(self.titleLabel)

        self.grid_layout = QGridLayout()  # 使用QGridLayout
        self.layout.addLayout(self.grid_layout)
        # self.layout.setAlignment(Qt.AlignTop)  # 顶部对齐
        self.layout.setSpacing(20)
        # self.layout.setStretch(1, 1)
        self.row_count = 0
        self.widgets = {}  # 存储所有组件
        # 设置标签列的固定宽度
        self.label_column_width = 100  # 可以根据需要调整
        self.grid_layout.setColumnMinimumWidth(0, self.label_column_width)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setColumnStretch(1, 1)  # 设置第 1 列（组件列）拉伸因子为 1

        # 设置字体
        # font = QFont()
        # font.setPointSize(20)  # 可以根据需要调整字体大小
        # self.setFont(font)

    def add_row(self, label_text, widget_type, widget_key, **kwargs):
        """添加一行组件"""
        label = CaptionLabel(label_text, self)
        # 创建组件实例

        # 特殊处理 RangeSlider
        if widget_type == RangeSlider:
            widget = RangeSlider(
                self,
                kwargs.get("min", 0),
                kwargs.get("max", 100),
                kwargs.get("left_value", 0),
                kwargs.get("right_value", 100),
            )

        # 特殊处理 SquareIconButton
        elif widget_type == SquareIconButton:
            widget = SquareIconButton(kwargs.get("icon_path", ""))
        else:
            widget = widget_type(self)

        setFont(label, 16)
        setFont(widget, 16)

        self.grid_layout.addWidget(label, self.row_count, 0)
        self.grid_layout.addWidget(widget, self.row_count, 1)
        # self.grid_layout.setAlignment(label, Qt.AlignLeft)
        # self.grid_layout.setAlignment(widget, Qt.AlignLeft)

        self.widgets[widget_key] = widget
        self.row_count += 1  # 行数加 1

        return widget  # 返回组件实例，方便进一步配置

    def get_values(self):
        """获取所有组件的值"""
        values = {}
        for key, widget in self.widgets.items():
            if isinstance(widget, LineEdit):
                values[key] = widget.text()
            elif isinstance(widget, ComboBox):
                values[key] = widget.currentText()
            elif isinstance(widget, SpinBox):
                values[key] = widget.value()
            elif isinstance(widget, RangeSlider):
                values[key] = (
                    widget.get_left_thumb_value(),
                    widget.get_right_thumb_value(),
                )
            # 可以根据需要添加其他类型的组件
        return values

    def set_values(self, values):
        """设置所有组件的值"""
        for key, value in values.items():
            widget = self.widgets.get(key)
            if widget:
                if isinstance(widget, LineEdit):
                    widget.setText(value)
                elif isinstance(widget, ComboBox):
                    widget.setCurrentText(value)
                elif isinstance(widget, SpinBox):
                    widget.setValue(value)
                elif isinstance(widget, RangeSlider):
                    widget.set_left_thumb_value(value[0])
                    widget.set_right_thumb_value(value[1])
                # 可以根据需要添加其他类型的组件

    def update_combobox_options(self):
        pass

    def setTitle(self, title: str):
        """设置界面标题"""
        self.titleLabel.setText(title)

    # """基础界面类,提供基础功能和工具方法"""

    # _default_params = {"stop": False, "data": {}, "mode": None}

    # URL_EDIT = "UrlInput"
    # REPEAT_COUNT = "RepeatTimes"
    # TREASURE_SELECT = "TreasureSelect"
    # TREASURE_COUNT = "TreasureCount"
    # BOSS_HP_RANGE = "BossHPRange"
    # PLAYER_COUNT_RANGE = "PlayerCountRange"
    # TARGET_TURN = "TargetTurn"
    # BUFF_COUNT = "BuffCount"
    # CUSTOM_BATTLE = "CustomBattle"

    # # def __init__(self, parent=None):
    # #     super().__init__(parent=parent)
    # #     self.parent = parent
    # #     self.worker = None
    # #     self.params = deepcopy(self._default_params)
    # #     # self.module = None
    # #     # self.module_data = {}

    # #     # 组件字典,用于管理组件的启用状态
    # #     self.components = {}

    # #     # 创建布局
    # #     self.vBoxLayout = QVBoxLayout(self)

    # #     # 设置边距
    # #     self.vBoxLayout.setContentsMargins(30, 30, 30, 30)
    # #     self.vBoxLayout.setSpacing(20)

    # #     # 添加标题
    # #     self.titleLabel = SubtitleLabel(self)
    # #     self.vBoxLayout.addWidget(self.titleLabel)

    # # def setTitle(self, title: str):
    # #     """设置界面标题"""
    # #     self.titleLabel.setText(title)

    # # def createUrlInput(self):
    # #     """创建副本网址输入框"""
    # #     input_widget = LineEdit(self)
    # #     if self.params["mode"] == "token":
    # #         input_widget.setPlaceholderText("请输入战货活动页面网址")
    # #         input_widget.setToolTip("请输入战货活动页面网址")
    # #     else:
    # #         input_widget.setPlaceholderText("请输入队伍确认界面网址")
    # #         input_widget.setToolTip("请输入队伍确认界面网址")
    # #     input_widget.installEventFilter(
    # #         ToolTipFilter(input_widget, showDelay=300, position=ToolTipPosition.TOP)
    # #     )
    # #     input_widget.setClearButtonEnabled(True)
    # #     self.addComponent("urlInput", input_widget, "副本网址：")

    # # def createRepeatTimes(self):
    # #     """创建重复次数设置"""
    # #     count_widget = SpinBox(self)
    # #     count_widget.setRange(0, 99999)
    # #     count_widget.setValue(0)
    # #     self.addComponent("repeatTimes", count_widget, "重复次数：")

    # # def createTreasureSelect(self):
    # #     """创建素材选择按钮"""
    # #     treasure_button = self.createImageButton(QSize(80, 80))
    # #     widget = QWidget()
    # #     layout = QHBoxLayout(widget)
    # #     layout.addStretch(1)
    # #     layout.addWidget(treasure_button)
    # #     treasure_button.clicked.connect(self.onMaterialSelect)
    # #     self.addComponent("treasureSelect", widget, "素材选择：", {"id_treasure": 0})

    # # def createTreasureCount(self):
    # #     """创建素材数量设置"""
    # #     treasure_count = SpinBox(self)
    # #     treasure_count.setRange(0, 9999)
    # #     treasure_count.setValue(0)
    # #     self.addComponent("treasureCount", treasure_count, "素材数量：")

    # # def createBossHPRange(self):
    # #     """创建BOSS血量范围设置"""
    # #     boss_hp_slider = RangeSlider(self, 0, 100, 0, 100)
    # #     self.addComponent("bossHPRange", boss_hp_slider, "BOSS血量：")

    # # def createPlayerCountRange(self):
    # #     """创建参加人数范围设置"""
    # #     player_count_slider = RangeSlider(self, 1, 30, 1, 30)
    # #     self.addComponent("playerCountRange", player_count_slider, "参加人数：")

    # # def createTargetTurn(self):
    # #     """创建目标回合设置"""
    # #     target_turn = SpinBox(self)
    # #     target_turn.setRange(0, 99)
    # #     target_turn.setValue(0)
    # #     self.addComponent("targetTurn", target_turn, "目标回合：")

    # # def createBuffCount(self):
    # #     """创建素材数量设置"""
    # #     treasure_count = SpinBox(self)
    # #     treasure_count.setRange(0, 9999)
    # #     treasure_count.setValue(0)
    # #     self.addComponent("buffCount", treasure_count, "Buff怪数量：")

    # # def createCustomBattle(self):
    # #     """创建自定义战斗按钮"""
    # #     custom_battle = ComboBox(self)
    # #     self.addComponent("customBattle", custom_battle, "自定义战斗：")

    # # def createImageButton(self, size: QSize) -> PushButton:
    # #     """创建图片按钮"""
    # #     button = PushButton(self)
    # #     button.setFixedSize(size)
    # #     return button

    # # def createComponentGroup(self, label_text: str, widget: QWidget) -> tuple:
    # #     """创建带标签的组件组
    # #     Args:
    # #         label_text: 标签文本
    # #         widget: 组件实例
    # #     Returns:
    # #         tuple: (组件组Widget, 标签Label)
    # #     """
    # #     group = QWidget(self)
    # #     layout = QHBoxLayout(group)
    # #     layout.setContentsMargins(0, 0, 0, 0)
    # #     layout.setSpacing(20)

    # #     label = CaptionLabel(label_text, self)
    # #     label.setFixedWidth(80)
    # #     layout.addWidget(label)
    # #     layout.addWidget(widget)

    # #     return group, label

    # # def addComponent(
    # #     self, name: str, widget: QWidget, label_text: str = None, addition={}
    # # ) -> None:
    # #     """添加组件到界面"""
    # #     if label_text is not None:
    # #         group, label = self.createComponentGroup(label_text, widget)
    # #         self.components[name] = {
    # #             "widget": group,
    # #             "main_widget": widget,
    # #             "label": label,
    # #             "enabled": True,
    # #         }
    # #         self.components[name].update(addition)
    # #         self.vBoxLayout.addWidget(group)
    # #     else:
    # #         self.components[name] = {
    # #             "widget": widget,
    # #             "main_widget": widget,
    # #             "enabled": True,
    # #         }
    # #         self.vBoxLayout.addWidget(widget)

    # # def getComponent(self, name: str) -> QWidget:
    # #     """获取组件实例"""
    # #     return self.components[name]["main_widget"] if name in self.components else None

    # # def enableComponent(self, name: str) -> None:
    # #     """启用组件
    # #     Args:
    # #         name: 组件名称
    # #         label_text: 标签文本(如果需要创建新组件)
    # #     """
    # #     if name not in self.components:
    # #         # 根据组件名称创建对应的组件
    # #         create_method = getattr(self, f"create{name}", None)
    # #         if create_method:
    # #             create_method()
    # #         return

    # #     component = self.components[name]
    # #     component["enabled"] = True
    # #     component["widget"].setVisible(True)

    # # def disableComponent(self, name: str) -> None:
    # #     """禁用组件"""
    # #     if name in self.components:
    # #         component = self.components[name]
    # #         component["enabled"] = False
    # #         component["widget"].setVisible(False)

    # # def getCurrentSettings(self):
    # #     data = {"stop": False, "data": {}}
    # #     data["mode"] = type(self).__name__[:-9].lower()
    # #     for name, component in self.components.items():
    # #         widget = component["main_widget"]
    # #         match name:
    # #             case "urlInput":
    # #                 data["data"]["url"] = widget.text()
    # #             case "repeatTimes":
    # #                 data["data"]["repeatTimes"] = widget.value()
    # #             case "treasureSelect":
    # #                 data["data"]["treasureSelect"] = component["id_treasure"]
    # #             case "treasureCount":
    # #                 data["data"]["treasureCount"] = widget.value()
    # #             case "bossHPRange":
    # #                 data["data"]["bossHP_min"] = widget.get_left_thumb_value()
    # #                 data["data"]["bossHP_max"] = widget.get_right_thumb_value()
    # #             case "playerCountRange":
    # #                 data["data"]["playerCount_min"] = widget.get_left_thumb_value()
    # #                 data["data"]["playerCount_max"] = widget.get_right_thumb_value()
    # #             case "targetTurn":
    # #                 data["data"]["targetTurn"] = widget.value()
    # #             case "buffCount":
    # #                 data["data"]["buffCount"] = widget.value()
    # #             case "customBattle":
    # #                 data["data"]["customBattle"] = widget.currentText()
    # #             case _:
    # #                 pass
    # #     return data

    # # def setCurrentSettings(self, data: dict):
    # #     for name, value in self.components.items():
    # #         widget = component["main_widget"]

    # # # def onMaterialSelect(self):
    # # #     """素材选择事件"""
    # # #     print("选择素材")


class BaseWindow(FluentWindow):
    """主窗口类"""

    def __init__(self):
        super().__init__()

        self.resize(900, 600)

        self.navigationInterface.panel.setReturnButtonVisible(False)
        self.navigationInterface.panel.setCollapsible(False)
        self.navigationInterface.setExpandWidth(100)
        self.navigationInterface.setMinimumExpandWidth(100)
        self.navigationInterface.expand(useAni=False)

        self.widgetLayout.removeWidget(self.stackedWidget)

        self.stackLayout = QVBoxLayout()
        self.stackLayout.addWidget(self.stackedWidget)
        self.stackLayout.setContentsMargins(0, 0, 0, 0)  # 去除边距
        self.stackLayout.setSpacing(0)

        self.start_button = PushButton("开始", self)
        self.stop_button = PushButton("停止", self)
        button_widget = QWidget(self)
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(10, 10, 10, 10)
        button_layout.setSpacing(10)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)

        self.start_button.clicked.connect(self.onStart)
        self.stop_button.clicked.connect(self.onStop)

        self.stackLayout.addWidget(button_widget)
        self.widgetLayout.addLayout(self.stackLayout)

        self.textBrowser = TextBrowser()
        self.widgetLayout.addWidget(self.textBrowser)

        # setFont(self.stackedWidget, 40)

    def load_config(self):
        """加载配置"""
        config = ConfigManager.load_config()
        if config:
            for page_name, page_config in config.items():
                page = self.pages.get(page_name)
                if page:
                    page.set_values(page_config)
            # 加载配置后更新所有子页面的 combobox
            for page_name, page in self.pages.items():
                page.update_combobox_options()

    def save_config(self):
        """保存配置"""
        config = {}
        for page_name, page in self.pages.items():
            config[page_name] = page.get_values()
        ConfigManager.save_config(config)

    def closeEvent(self, event):
        """关闭窗口事件"""
        self.save_config()
        event.accept()

    def onStart(self):
        """开始按钮点击事件"""
        current_page = self.stackedWidget.currentWidget()
        if isinstance(current_page, BaseInterface):
            values = current_page.get_values()
            # 在这里处理获取到的 values，例如打印
            print(f"当前页面 ({current_page.__class__.__name__}) 的值：{values}")
            # 可以将 values 发送到其他模块进行处理
            self.textBrowser.append(
                f"当前页面 ({current_page.__class__.__name__}) 的值：{values}"
            )

    def onStop(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BaseWindow()
    window.show()
    sys.exit(app.exec())
