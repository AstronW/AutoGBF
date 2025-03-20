from qfluentwidgets import Dialog, PushButton
from PySide6.QtWidgets import QGridLayout
from PySide6.QtGui import QIcon, QPainter
from PySide6.QtCore import (
    QSize,
    QRectF,
)

TREASURE_PATH = "./assets/treasure/{}.jpg"


class TreasureButton(PushButton):
    """
    自定义按钮类，用于显示宝藏图片。
    继承自 qfluentwidgets.PushButton，支持图标显示和自定义绘制。
    """

    def __init__(self, icon_path, parent=None):
        """
        初始化 TreasureButton。

        Args:
            icon_path (str): 图标文件路径。
            parent (QWidget, optional): 父窗口部件。默认为 None。
        """
        super().__init__(parent)
        self.setIcon(QIcon(icon_path))  # 设置按钮图标
        self.setFixedSize(QSize(140, 80))  # 设置按钮固定大小
        self.setIconSize(QSize(140, 80))  # 设置图标大小

    def paintEvent(self, e):
        """
        重写 paintEvent 方法，自定义按钮的绘制逻辑。
        根据按钮状态（禁用、按下）调整图标的透明度。
        """
        super().paintEvent(e)
        if self.icon().isNull():
            return

        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        # 根据按钮状态设置透明度
        if not self.isEnabled():
            painter.setOpacity(0.3628)
        elif self.isPressed:
            painter.setOpacity(0.786)

        w, h = self.iconSize().width(), self.iconSize().height()
        y = (self.height() - h) / 2
        mw = self.minimumSizeHint().width()
        if mw > 0:
            x = 12 + (self.width() - mw) // 2
        else:
            x = 12

        if self.isRightToLeft():
            x = self.width() - w - x

        self._drawIcon(self._icon, painter, QRectF(0, y, w, h))


class TreasureDialog(Dialog):
    """
    图片选择对话框，用于展示宝藏图片并允许用户选择。
    继承自 qfluentwidgets.Dialog。
    """

    def __init__(self, image_data, parent=None):
        """
        初始化 TreasureDialog。

        Args:
            image_data (list or set): 包含图片 ID 的列表或集合。
            parent (QWidget, optional): 父窗口部件。默认为 None。
        """
        super().__init__(title="选择素材", content="", parent=parent)

        # 移除默认标题和内容标签
        self.textLayout.removeWidget(self.titleLabel)
        self.textLayout.removeWidget(self.contentLabel)
        self.yesButton.setParent(None)
        self.yesButton.deleteLater()
        self.buttonLayout.removeWidget(self.yesButton)

        # 设置取消按钮文本
        self.cancelButton.setText("取消")

        # 保存父窗口引用
        self.parent_widget = parent

        # 创建网格布局并设置间距和边距
        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.grid_layout.setHorizontalSpacing(5)
        self.grid_layout.setVerticalSpacing(10)

        # 将网格布局插入到对话框中
        self.textLayout.insertLayout(0, self.grid_layout, 1)

        # 动态生成宝藏图片按钮
        row = 0
        col = 0
        for item_id in image_data:
            image_path = TREASURE_PATH.format(item_id)
            button = TreasureButton(image_path, self)
            button.clicked.connect(
                lambda item_id=item_id: self.on_image_selected(item_id)
            )
            self.grid_layout.addWidget(button, row, col)

            col += 1
            if col >= 6:
                col = 0
                row += 1

        # 设置对话框大小
        self.resize(600, 400)

    def on_image_selected(self, item_id):
        """
        当用户点击某个宝藏图片按钮时触发。

        Args:
            item_id (str): 被选中的宝藏图片 ID。
        """
        image_path = TREASURE_PATH.format(item_id)
        # 设置父窗口中触发按钮的图标
        self.parent_widget.treasure_select_button.setIcon(QIcon(image_path))
        self.parent_widget.treasure_id = item_id
        self.accept()
