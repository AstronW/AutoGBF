import sys
import os
import json
from PySide6.QtCore import (
    Qt,
    QSize,
    QRectF,
)
from PySide6.QtGui import QIcon, QFont, QPainter
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QButtonGroup,
    QDialog,
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
    Dialog,
    RadioButton,
    setFont,
)

from .widgets.range_slider import RangeSlider
from .widgets.treasure_dialog import TreasureButton, TreasureDialog
from ..utils.logger import logger


class ConfigManager:
    """配置管理类，负责保存和加载配置"""

    CONFIG_FILE = "config.json"

    @staticmethod
    def load_config():
        """加载配置"""
        try:
            # 检查配置文件是否存在
            if os.path.exists(ConfigManager.CONFIG_FILE):
                with open(ConfigManager.CONFIG_FILE, "r", encoding="utf-8") as f:
                    # 尝试解析JSON文件
                    config_data = json.load(f)
                    logger.info("配置文件加载成功")
                    return config_data
            else:
                logger.warning("配置文件不存在，使用默认配置")
                return {}
        except (FileNotFoundError, PermissionError) as e:
            # 处理文件找不到或权限不足的情况
            logger.error(f"无法访问配置文件: {e}")
            return {}
        except json.JSONDecodeError as e:
            # 处理JSON格式错误的情况
            logger.error(f"配置文件格式错误: {e}")
            return {}

    @staticmethod
    def save_config(config):
        """保存配置"""
        with open(ConfigManager.CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)


class BaseInterface(QWidget):
    """子页面基类"""

    def __init__(self, parent=None, browser=None):
        super().__init__(parent)
        self.browser = browser
        self.treasure_select_button = None
        self.layout = QVBoxLayout(self)
        self.titleLabel = SubtitleLabel(self)
        self.layout.addWidget(self.titleLabel)

        self.grid_layout = QGridLayout()  # 使用QGridLayout
        self.layout.addLayout(self.grid_layout)

        self.layout.setSpacing(20)

        self.row_count = 0
        self.widgets = {}  # 存储所有组件

        self.label_column_width = 100  # 可以根据需要调整
        self.grid_layout.setColumnMinimumWidth(0, self.label_column_width)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setColumnStretch(1, 1)  # 设置第 1 列（组件列）拉伸因子为 1

    def addRow(self, label_text, widget_type, widget_key, **kwargs):
        """添加一行组件"""
        label = CaptionLabel(label_text, self)

        if widget_type == RangeSlider:
            widget = RangeSlider(
                self,
                kwargs.get("min", 0),
                kwargs.get("max", 100),
                kwargs.get("left", 0),
                kwargs.get("right", 100),
            )

        elif widget_type == TreasureButton:
            widget = TreasureButton(kwargs.get("icon_path", ""), self)
            if label_text == "素材选择":
                self.treasure_select_button = widget
                self.treasure_id = None
                widget.clicked.connect(self.show_treasure_select)
        elif widget_type == RadioButton:
            items = kwargs.get("items", [])
            widget = QButtonGroup(self)
            layout = QHBoxLayout()
            for item in items:
                radio_button = RadioButton(item, self)
                layout.addWidget(radio_button)
                widget.addButton(radio_button)
                setFont(radio_button, 16)
            setFont(label, 16)

            self.grid_layout.addWidget(label, self.row_count, 0)
            self.grid_layout.addLayout(layout, self.row_count, 1)

            self.widgets[widget_key] = widget
            self.row_count += 1  # 行数加 1

            return widget
        else:
            widget = widget_type(self)

        setFont(label, 16)
        setFont(widget, 16)

        self.grid_layout.addWidget(label, self.row_count, 0)
        self.grid_layout.addWidget(widget, self.row_count, 1)

        self.widgets[widget_key] = widget
        self.row_count += 1  # 行数加 1

        return widget  # 返回组件实例，方便进一步配置

    def getValues(self):
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
                    widget.left(),
                    widget.right(),
                )
            elif isinstance(widget, TreasureButton):
                values[key] = self.treasure_id
            elif isinstance(widget, QButtonGroup):
                values[key] = widget.checkedId()
            else:
                pass

        return values

    def setValues(self, values: dict):
        """设置所有组件的值"""
        for key, value in values.items():
            widget = self.widgets.get(key)
            if widget:
                if isinstance(widget, LineEdit):
                    widget.setText(value)
                elif isinstance(widget, SpinBox):
                    widget.setValue(value)
                elif isinstance(widget, RangeSlider):
                    widget.set_left_thumb_value(value[0])
                    widget.set_right_thumb_value(value[1])
                elif isinstance(widget, TreasureButton):
                    widget.setIcon(QIcon(f"./assets/treasure/{value}.jpg"))
                    self.treasure_id = value
                elif isinstance(widget, QButtonGroup):
                    widget.button(value).setChecked(True)
                else:
                    pass

    def show_treasure_select(self):

        list_treasure = []
        # self.browser.get_treasure_list()

        # 创建并显示对话框
        dialog = TreasureDialog(list_treasure, self)
        dialog.exec()

    def update_combobox_options(self):
        list_combo = self.getComboList()
        # ComboBox.set
        self.widgets.get("custom_battle").addItems(list_combo)

    def getComboList(self):
        list_combo = [""]
        list_custom = os.listdir("./custom/")
        for custom in list_custom:
            if custom.endswith(".json"):
                list_combo.append(custom.replace(".json", ""))
        return list_combo

    def setTitle(self, title: str):
        """设置界面标题"""
        self.titleLabel.setText(title)


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

    def load_config(self):
        """加载配置"""
        config = ConfigManager.load_config()
        if config:
            for page_name, page_config in config.items():
                page = self.pages.get(page_name)
                if page:
                    page.setValues(page_config)

            for page_name, page in self.pages.items():
                page.update_combobox_options()

    def saveConfig(self):
        """保存配置"""
        config = {}
        for page_name, page in self.pages.items():
            config[page_name] = page.getValues()
        ConfigManager.save_config(config)

    def closeEvent(self, event):
        """关闭窗口事件"""
        self.saveConfig()
        import logging
        logging.shutdown()
        # event.accept()
        super().closeEvent(event)

    def onStart(self):
        """开始按钮点击事件"""
        pass

    def onStop(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BaseWindow()
    window.show()
    sys.exit(app.exec())
